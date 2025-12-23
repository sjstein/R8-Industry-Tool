import csv
import sys
import os

from r8lib import IndustryFile, Industry

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QPushButton, QHBoxLayout, QWidget
from mainWindow_ui import Ui_MainWindow
from mainTable import DictTableModel
from industryDetailDialog import IndustryDetailDialog
from instructionsDialog import InstructionsDialog
from aboutDialog import AboutDialog
from findReplaceDialog import FindReplaceDialog


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


carfile = resource_path('r8CarTypes.csv')
INTLEN = 4
BYTLEN = 1
SHTLEN = 2
UTFLEN = 2              # Length of UTF-16 char


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

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
        self.ui.actionAbout.triggered.connect(self.show_about)

        # Disable Save and Save As until a file is loaded
        self.ui.actionSave.setEnabled(False)
        if hasattr(self.ui, 'actionQuit_2'):
            self.ui.actionQuit_2.setEnabled(False)

    def open_file(self):
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

        row = index.row()
        if row < len(indFile1.industries):
            industry = indFile1.industries[row]

            # Open the detail dialog, passing the row index
            dialog = IndustryDetailDialog(industry, cardict, self, industry_row=row)
            result = dialog.exec()

            # If user clicked Save, refresh the table and mark as dirty
            if result == IndustryDetailDialog.DialogCode.Accepted:
                industry_data = [ind.to_dict() for ind in indFile1.industries]
                self.table_model.update_data(industry_data)
                self.table_model.mark_row_dirty(row)  # Mark this industry as having unsaved changes
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

