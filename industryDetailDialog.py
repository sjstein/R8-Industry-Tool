from PySide6.QtWidgets import QDialog, QTableWidgetItem, QMessageBox, QPushButton, QHBoxLayout, QStyledItemDelegate, QLineEdit
from PySide6.QtCore import Qt, QTimer
from industryDetailDialog_ui import Ui_IndustryDetailDialog
from r8lib import industry_track, producer, industry_tag, industry_filter, encode_run8string
from industryFindReplaceDialog import IndustryFindReplaceDialog


class VisualSelectDelegate(QStyledItemDelegate):
    """Custom delegate that visually highlights all text when editing"""
    def setEditorData(self, editor, index):
        """Set the editor data and visually select all text"""
        if isinstance(editor, QLineEdit):
            value = index.model().data(index, Qt.ItemDataRole.EditRole)
            editor.setText(str(value) if value else "")
            # Ensure text is visually selected (highlighted)
            QTimer.singleShot(0, editor.selectAll)


class IndustryDetailDialog(QDialog):
    def __init__(self, industry, cardict, parent=None, industry_row=None):
        super().__init__(parent)
        self.industry = industry
        self.cardict = cardict
        self.industry_row = industry_row  # Row index in main table

        # Setup UI from generated file
        self.ui = Ui_IndustryDetailDialog()
        self.ui.setupUi(self)

        # Set window title with industry name
        self.setWindowTitle(f"Industry Details - {industry.name}")

        # Configure table headers
        from PySide6.QtWidgets import QHeaderView

        # Tracks table - all columns stretch equally
        self.ui.tracks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Producers table - custom column widths
        header = self.ui.producers_table.horizontalHeader()

        # Hide row numbers on the left
        self.ui.producers_table.verticalHeader().setVisible(False)

        # Column 0: ID - fixed width for ~3 characters
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.ui.producers_table.setColumnWidth(0, 40)

        # Column 1: Car Type - resize to contents
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        # Column 2: Produce Empties - resize to contents
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # Column 3: Hours - resize to contents
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        # Column 4: Capacity - resize to contents
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # Column 5: Outbound tags - stretch to fill remaining space
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        # Apply custom delegate to tags column to visually highlight text on edit
        self.ui.producers_table.setItemDelegateForColumn(5, VisualSelectDelegate(self))

        # Make single-click immediately enter edit mode (so text gets highlighted)
        from PySide6.QtWidgets import QAbstractItemView
        self.ui.producers_table.setEditTriggers(
            QAbstractItemView.EditTrigger.CurrentChanged |
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.SelectedClicked |
            QAbstractItemView.EditTrigger.AnyKeyPressed
        )

        # Add Find button for producer tags
        find_button_layout = QHBoxLayout()
        find_button_layout.addStretch()
        self.find_tags_button = QPushButton("Find...")
        self.find_tags_button.clicked.connect(self.show_find_replace)
        self.find_tags_button.setMaximumWidth(100)
        find_button_layout.addWidget(self.find_tags_button)

        # Add the button layout to the producers group
        self.ui.producersGroup.layout().addLayout(find_button_layout)

        # Connect signals
        self.ui.remove_track_button.clicked.connect(self.remove_track)
        self.ui.save_button.clicked.connect(self.accept)
        self.ui.cancel_button.clicked.connect(self.reject)

        # Load data
        self.load_data()

    def load_data(self):
        """Load industry data into the form"""
        # Basic information
        self.ui.name_edit.setText(self.industry.name)
        self.ui.local_name_edit.setText(self.industry.local_name)
        self.ui.symbol_edit.setText(self.industry.trk_sym)
        self.ui.process_blocks_check.setChecked(self.industry.process_in_blocks)

        # Tracks
        self.load_tracks()

        # Producers
        self.load_producers()

    def load_tracks(self):
        """Load tracks into the table"""
        if self.industry.number_of_tracks > 0:
            self.ui.tracks_table.setRowCount(self.industry.number_of_tracks)
            for i, track in enumerate(self.industry.track):
                self.ui.tracks_table.setItem(i, 0, QTableWidgetItem(str(track.route_prefix)))
                self.ui.tracks_table.setItem(i, 1, QTableWidgetItem(str(track.track_section)))
                self.ui.tracks_table.setItem(i, 2, QTableWidgetItem(str(track.track_direction)))
        else:
            self.ui.tracks_table.setRowCount(0)

    def load_producers(self):
        """Load producers into the table"""
        if self.industry.num_producers > 0:
            # Sort producers alphabetically by car type name
            sorted_producers = sorted(
                self.industry.producer,
                key=lambda prod: self.cardict.get(str(prod.bIndex), "Unknown").lower()
            )

            self.ui.producers_table.setRowCount(self.industry.num_producers)
            for i, prod in enumerate(sorted_producers):
                # Car Type ID (read-only)
                car_id_item = QTableWidgetItem(str(prod.bIndex))
                car_id_item.setFlags(car_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.ui.producers_table.setItem(i, 0, car_id_item)

                # Car Type Name (read-only)
                car_type_name = self.cardict.get(str(prod.bIndex), "Unknown")
                car_name_item = QTableWidgetItem(car_type_name)
                car_name_item.setFlags(car_name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.ui.producers_table.setItem(i, 1, car_name_item)

                # Produce Empties
                self.ui.producers_table.setItem(i, 2, QTableWidgetItem("Empties" if prod.produce_empties else "Loads"))

                # Hours
                self.ui.producers_table.setItem(i, 3, QTableWidgetItem(str(prod.proc_hours)))

                # Capacity
                self.ui.producers_table.setItem(i, 4, QTableWidgetItem(str(prod.capacity)))

                # Tags (displayed comma-separated, can be entered with spaces or commas)
                tags_str = prod.returnTags() if prod.num_tags > 0 else ""
                self.ui.producers_table.setItem(i, 5, QTableWidgetItem(tags_str))
        else:
            self.ui.producers_table.setRowCount(0)

    def remove_track(self):
        """Remove selected track row"""
        current_row = self.ui.tracks_table.currentRow()
        if current_row >= 0:
            self.ui.tracks_table.removeRow(current_row)
        else:
            QMessageBox.warning(self, "No Selection", "Please select a track to remove.")

    def save_data(self):
        """Save form data back to the industry object"""
        # Update basic information
        if self.ui.name_edit.text() != self.industry.name:
            self.industry.replaceName(self.ui.name_edit.text())

        if self.ui.local_name_edit.text() != self.industry.local_name:
            self.industry.replaceLocalName(self.ui.local_name_edit.text())

        if self.ui.symbol_edit.text() != self.industry.trk_sym:
            self.industry.replaceSymbol(self.ui.symbol_edit.text())

        self.industry.process_in_blocks = self.ui.process_blocks_check.isChecked()

        # Save tracks
        self.save_tracks()

        # Save producers
        self.save_producers()

    def save_tracks(self):
        """Save tracks from table to industry object"""
        # Clear existing tracks
        self.industry.track = []
        self.industry.number_of_tracks = self.ui.tracks_table.rowCount()

        # Read each row and create industry_track objects
        for i in range(self.ui.tracks_table.rowCount()):
            # Create a mock memory map for the industry_track constructor
            track_data = bytearray()

            # unk1 (use 0 as default for new tracks)
            unk1 = 0
            track_data.extend(unk1.to_bytes(4, 'little', signed=True))

            # route_prefix
            route_prefix = int(self.ui.tracks_table.item(i, 0).text())
            track_data.extend(route_prefix.to_bytes(4, 'little', signed=True))

            # track_section
            track_section = int(self.ui.tracks_table.item(i, 1).text())
            track_data.extend(track_section.to_bytes(4, 'little', signed=True))

            # track_direction
            track_direction = int(self.ui.tracks_table.item(i, 2).text())
            track_data.extend(track_direction.to_bytes(4, 'little', signed=True))

            # Create the track object
            new_track = industry_track(track_data, 0)
            self.industry.track.append(new_track)

    def save_producers(self):
        """Save producers from table to industry object"""
        # Update existing producers (preserving rec_type and other internal fields)
        for i in range(min(self.ui.producers_table.rowCount(), len(self.industry.producer))):
            prod = self.industry.producer[i]

            # bIndex (car type) - read from column 0 (read-only but we still read it)
            bIndex = int(self.ui.producers_table.item(i, 0).text())
            prod.bIndex = bIndex

            # produce_empties - column 2
            produce_empties_text = self.ui.producers_table.item(i, 2).text().strip().lower()
            prod.produce_empties = produce_empties_text in ['yes', 'y', '1', 'true']

            # proc_hours - column 3
            prod.proc_hours = int(self.ui.producers_table.item(i, 3).text())

            # capacity - column 4
            prod.capacity = int(self.ui.producers_table.item(i, 4).text())

            # Parse tags (space or comma separated) - column 5
            tags_text = self.ui.producers_table.item(i, 5).text().strip()
            # Replace commas with spaces, then split by whitespace
            tags_text = tags_text.replace(',', ' ')
            tag_list = [tag for tag in tags_text.split() if tag]

            # Rebuild tags list
            prod.tags = []
            prod.num_tags = len(tag_list)
            for tag_name in tag_list:
                # Create tag data
                tag_data = bytearray()
                enc_tag = encode_run8string(tag_name)
                tag_len = len(enc_tag)
                tag_data.extend(tag_len.to_bytes(4, 'little', signed=True))
                tag_data.extend(enc_tag)

                # Create tag object
                new_tag = industry_tag(tag_data, 0)
                prod.tags.append(new_tag)

    def show_find_replace(self):
        """Show the find and replace dialog for tags in this industry"""
        # Get the main window reference
        main_window = self.parent()
        dialog = IndustryFindReplaceDialog(
            self.industry,
            self.ui.producers_table,
            self,
            main_window=main_window,
            industry_row=self.industry_row
        )
        dialog.show()

    def accept(self):
        """Override accept to save data before closing"""
        try:
            self.save_data()
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error Saving", f"Failed to save changes:\n{str(e)}")
