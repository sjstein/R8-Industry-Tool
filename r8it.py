import csv
import sys
import os
import json
import urllib.request
import threading
from packaging import version as pkg_version

from r8lib import IndustryFile, Industry

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QPushButton, QHBoxLayout, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from mainWindow_ui import Ui_MainWindow
from mainTable import DictTableModel
from industryDetailDialog import IndustryDetailDialog
from instructionsDialog import InstructionsDialog
from aboutDialog import AboutDialog
from findReplaceDialog import FindReplaceDialog
from version import VERSION


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def check_for_updates(timeout=5):
    """
    Check GitHub for newer releases.
    Returns: (has_update, latest_version, release_url, error_message)
    """
    try:
        # GitHub API endpoint for latest release
        api_url = "https://api.github.com/repos/sjstein/R8-Industry-Tool/releases/latest"

        # Create request with timeout
        req = urllib.request.Request(api_url)
        req.add_header('Accept', 'application/vnd.github.v3+json')

        # Make request with timeout
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode())

        # Extract version from tag_name (handles both "v1.2.3" and "1.2.3")
        latest_tag = data.get('tag_name', '')
        latest_version = latest_tag.lstrip('v')
        release_url = data.get('html_url', 'https://github.com/sjstein/R8-Industry-Tool/releases')

        # Compare versions using packaging library for semantic versioning
        current = pkg_version.parse(VERSION)
        latest = pkg_version.parse(latest_version)

        has_update = latest > current

        return (has_update, latest_version, release_url, None)

    except Exception as e:
        # Return error information
        return (False, None, None, str(e))


carfile = resource_path('r8CarTypes.csv')
INTLEN = 4
BYTLEN = 1
SHTLEN = 2
UTFLEN = 2              # Length of UTF-16 char


class UpdateChecker(QObject):
    """Worker class for checking updates in background thread"""
    # Define signals
    update_found = Signal(str, str)  # (latest_version, release_url)
    no_update = Signal()
    error_occurred = Signal(str)  # (error_message)

    def __init__(self):
        super().__init__()

    def check(self):
        """Perform the update check (runs in background thread)"""
        has_update, latest_version, release_url, error = check_for_updates()

        if error:
            self.error_occurred.emit(error)
        elif has_update:
            self.update_found.emit(latest_version, release_url)
        else:
            self.no_update.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set window title with version
        self.setWindowTitle(f"Run8 Industry Tool - v{VERSION}")

        # Set window icon
        icon_path = resource_path('app_icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Track the currently loaded file
        self.current_filename = None

        # Initialize the table model
        self.table_model = DictTableModel()
        self.ui.tableView.setModel(self.table_model)

        # Add Find button in lower right
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.find_button = QPushButton("Find...")
        self.find_button.clicked.connect(self.show_find_replace)
        self.find_button.setMaximumWidth(100)
        button_layout.addWidget(self.find_button)

        # Add the button layout to the main vertical layout
        from PySide6.QtCore import Qt
        central_widget = self.ui.centralwidget
        central_widget.layout().addLayout(button_layout)

        # Connect double-click signal
        self.ui.tableView.doubleClicked.connect(self.on_row_double_clicked)

        # Connect menu actions
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionSave.triggered.connect(self.save_file)
        if hasattr(self.ui, 'actionQuit_2'):
            self.ui.actionQuit_2.triggered.connect(self.save_file_as)  # Save As...
        if hasattr(self.ui, 'actionQuit_3'):
            self.ui.actionQuit_3.triggered.connect(self.close)  # Quit
        self.ui.actionInstructions.triggered.connect(self.show_instructions)
        self.ui.actionCheckUpdates.triggered.connect(self.check_updates_manual)
        self.ui.actionAbout.triggered.connect(self.show_about)

        # Disable Save and Save As until a file is loaded
        self.ui.actionSave.setEnabled(False)
        if hasattr(self.ui, 'actionQuit_2'):
            self.ui.actionQuit_2.setEnabled(False)

        # Check for updates on startup (non-blocking)
        QTimer.singleShot(500, self.check_updates_on_startup)

    def open_file(self):
        # Check for unsaved changes before opening a new file
        if self.table_model._dirty_rows:
            reply = QMessageBox.question(
                self,
                'Unsaved Changes',
                f'You have {len(self.table_model._dirty_rows)} unsaved changes.\n\n'
                'Opening a new file will discard these changes. Continue?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                return  # User cancelled, don't open new file

        file_name , _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'Industry Files (*.ind);;All Files (*)')
        if file_name:
            print(f'Selected file: {file_name}')
            with open(file_name, 'rb') as ifp:
                mem_ptr = 0
                fcontent = ifp.read()
                indFile1.unk1 = fcontent[mem_ptr:mem_ptr + INTLEN]
                mem_ptr += INTLEN
                indFile1.num_rec = int.from_bytes(fcontent[mem_ptr:mem_ptr + INTLEN], 'little')
                mem_ptr += INTLEN
                # Clear existing industries before loading new ones
                indFile1.industries = []
                for i in range(0, indFile1.num_rec):
                    indFile1.industries.append(Industry(fcontent, mem_ptr))
                    mem_ptr += len(indFile1.industries[i])

            # Track the loaded filename
            self.current_filename = file_name
            self.statusBar().showMessage('Loaded file: ' + file_name +
                                         f'      [{indFile1.num_rec} industries loaded]')

            # Populate the table with industry data
            industry_data = [ind.to_dict() for ind in indFile1.industries]
            self.table_model.update_data(industry_data)

            # Clear dirty rows since this is a fresh file load
            self.table_model.clear_dirty_flags()

            # Enable Save and Save As menu items now that data is loaded
            self.ui.actionSave.setEnabled(True)
            if hasattr(self.ui, 'actionQuit_2'):
                self.ui.actionQuit_2.setEnabled(True)

            # Configure column widths after data is loaded
            from PySide6.QtWidgets import QHeaderView
            header = self.ui.tableView.horizontalHeader()

            # Column 0: Name - wider
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
            self.ui.tableView.setColumnWidth(0, 300)

            # Column 1: Tag - small fixed width
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            self.ui.tableView.setColumnWidth(1, 70)

            # Column 2: Local Name
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
            self.ui.tableView.setColumnWidth(2, 150)

            # Column 3: # Tracks Nodes
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

            # Column 4: Incoming cars
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

            # Column 5: Process in Blocks
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

            # Enable column sorting by clicking headers
            self.ui.tableView.setSortingEnabled(True)
            # Sort by industry name (column 0) ascending by default
            self.ui.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)

    def save_file(self):
        """Save the industry configuration to the currently loaded file"""
        # Check if any data is loaded
        if indFile1.num_rec == 0:
            QMessageBox.warning(self, "No Data", "No industry data loaded. Please open a file first.")
            return

        # Check if we have a current filename
        if not self.current_filename:
            # No file loaded yet, redirect to Save As
            self.save_file_as()
            return

        # Confirm overwrite
        reply = QMessageBox.question(
            self,
            'Save File',
            f'Save changes to:\n{self.current_filename}\n\nAre you sure?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # Write the binary file
        try:
            with open(self.current_filename, 'wb') as ofp:
                new_content = indFile1.to_bytes()
                ofp.write(new_content)

            # Clear dirty flags since all changes are now saved
            self.table_model.clear_dirty_flags()

            self.statusBar().showMessage(f'Saved file: {self.current_filename}', 5000)
            QMessageBox.information(self, "Save Successful", f"Industry configuration saved to:\n{self.current_filename}")

        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Failed to save file:\n{str(e)}")

    def save_file_as(self):
        """Save the industry configuration to a new file"""
        # Check if any data is loaded
        if indFile1.num_rec == 0:
            QMessageBox.warning(self, "No Data", "No industry data loaded. Please open a file first.")
            return

        # Get the save file name
        default_filename = self.current_filename if self.current_filename else "config.ind"
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            'Save Industry File As',
            default_filename,
            'Industry Files (*.ind);;All Files (*)'
        )

        if not file_name:
            return  # User cancelled

        # Write the binary file
        try:
            with open(file_name, 'wb') as ofp:
                new_content = indFile1.to_bytes()
                ofp.write(new_content)

            # Clear dirty flags since all changes are now saved
            self.table_model.clear_dirty_flags()

            # Update current filename to the new file
            self.current_filename = file_name
            self.statusBar().showMessage(f'Saved file: {file_name}', 5000)
            QMessageBox.information(self, "Save Successful", f"Industry configuration saved to:\n{file_name}")

        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Failed to save file:\n{str(e)}")

    def on_row_double_clicked(self, index):
        """Handle double-click on table row - open detail dialog"""
        if not index.isValid():
            return

        display_row = index.row()
        # Get the original index in the data structure (before sorting)
        original_index = self.table_model.get_original_index(display_row)

        if original_index < len(indFile1.industries):
            industry = indFile1.industries[original_index]

            # Open the detail dialog, passing the original index
            dialog = IndustryDetailDialog(industry, cardict, self, industry_row=original_index)
            result = dialog.exec()

            # If user clicked Save, refresh the table and mark as dirty
            if result == IndustryDetailDialog.DialogCode.Accepted:
                industry_data = [ind.to_dict() for ind in indFile1.industries]
                self.table_model.update_data(industry_data)
                # Find the new display row for this original index after re-sorting
                new_display_row = self.table_model._original_indices.index(original_index)
                self.table_model.mark_row_dirty(new_display_row)  # Mark this industry as having unsaved changes
                self.statusBar().showMessage(f'Updated: {industry.name}', 3000)

    def show_instructions(self):
        """Show the instructions dialog (non-modal)"""
        dialog = InstructionsDialog(self)
        dialog.show()  # Use show() instead of exec() to allow interaction with main window

    def show_about(self):
        """Show the about dialog"""
        dialog = AboutDialog(self)
        dialog.exec()

    def show_find_replace(self):
        """Show the find and replace dialog"""
        dialog = FindReplaceDialog(self)
        dialog.show()  # Use show() instead of exec() to allow non-modal operation

    def check_updates_on_startup(self):
        """Check for updates on startup in background thread"""
        # Create worker and keep reference to prevent garbage collection
        self._startup_checker = UpdateChecker()

        # Connect signals to slots (auto_check=True)
        self._startup_checker.update_found.connect(lambda v, u: self.show_update_dialog(v, u, auto_check=True))
        # For startup check, we silently ignore errors and "no update" results

        # Run check in background thread
        def check_thread():
            self._startup_checker.check()

        thread = threading.Thread(target=check_thread, daemon=True)
        thread.start()

    def check_updates_manual(self):
        """Check for updates when user clicks menu item"""
        # Show status message
        self.statusBar().showMessage('Checking for updates...', 3000)

        # Create worker and keep reference to prevent garbage collection
        self._manual_checker = UpdateChecker()

        # Connect signals to handler methods
        self._manual_checker.update_found.connect(self.on_manual_update_found)
        self._manual_checker.no_update.connect(self.on_manual_no_update)
        self._manual_checker.error_occurred.connect(self.on_manual_update_error)

        # Run check in background thread
        def check_thread():
            self._manual_checker.check()

        thread = threading.Thread(target=check_thread, daemon=True)
        thread.start()

    def on_manual_update_found(self, latest_version, release_url):
        """Handle update found signal from manual check"""
        self.show_update_dialog(latest_version, release_url, auto_check=False)

    def on_manual_no_update(self):
        """Handle no update signal from manual check"""
        QMessageBox.information(
            self,
            'No Updates Available',
            f'You are running the latest version ({VERSION}).'
        )

    def on_manual_update_error(self, error_message):
        """Handle error signal from manual check"""
        QMessageBox.warning(
            self,
            'Update Check Failed',
            f'Could not check for updates:\n{error_message}\n\nPlease check your internet connection.'
        )

    def show_update_dialog(self, latest_version, release_url, auto_check=True):
        """Show dialog notifying user of available update"""
        if auto_check:
            message = (
                f'A new version of Run8 Industry Tool is available!\n\n'
                f'Current version: {VERSION}\n'
                f'Latest version: {latest_version}\n\n'
                f'Would you like to download the update?'
            )
        else:
            message = (
                f'Update available!\n\n'
                f'Current version: {VERSION}\n'
                f'Latest version: {latest_version}\n\n'
                f'Would you like to download the update?'
            )

        reply = QMessageBox.question(
            self,
            'Update Available',
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Open the releases page in the default browser
            import webbrowser
            webbrowser.open(release_url)

    def closeEvent(self, event):
        """Handle window close event - check for unsaved changes"""
        # Check if there are unsaved changes
        if self.table_model._dirty_rows:
            reply = QMessageBox.question(
                self,
                'Unsaved Changes',
                f'You have {len(self.table_model._dirty_rows)} unsaved changes.\n\nAre you sure you want to exit without saving?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                event.ignore()  # Cancel the close
                return

        event.accept()  # Proceed with close


if __name__ == "__main__":
    cardict = {}
    indFile1 = IndustryFile()

    with open(carfile, mode='r') as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
            cardict[lines[0]] = lines[1]

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

