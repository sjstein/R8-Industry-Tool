from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QComboBox, QGroupBox,
                               QFormLayout, QMessageBox)
from PySide6.QtCore import Qt


class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.setModal(False)  # Allow interaction with main window
        self.resize(400, 200)

        # Store reference to parent for accessing table data
        self.main_window = parent
        self.current_match_index = -1
        self.matches = []

        # Main layout
        main_layout = QVBoxLayout(self)

        # Search criteria group
        criteria_group = QGroupBox("Search Criteria")
        criteria_layout = QFormLayout()

        # Field selector
        self.field_combo = QComboBox()
        self.field_combo.addItems(["Tag", "Local Name", "Processed tags in all industries"])
        criteria_layout.addRow("Search in:", self.field_combo)

        # Find what
        self.find_edit = QLineEdit()
        self.find_edit.setPlaceholderText("Enter exact text to find")
        criteria_layout.addRow("Find what:", self.find_edit)

        # Replace with
        self.replace_edit = QLineEdit()
        self.replace_edit.setPlaceholderText("Enter replacement text")
        criteria_layout.addRow("Replace with:", self.replace_edit)

        criteria_group.setLayout(criteria_layout)
        main_layout.addWidget(criteria_group)

        # Note about exact matching
        self.note_label = QLabel("Note: Only exact matches (entire field) will be found")
        self.note_label.setStyleSheet("color: gray; font-style: italic;")
        main_layout.addWidget(self.note_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.find_button = QPushButton("Find Next")
        self.find_button.clicked.connect(self.find_next)
        button_layout.addWidget(self.find_button)

        self.replace_button = QPushButton("Replace")
        self.replace_button.clicked.connect(self.replace_current)
        self.replace_button.setEnabled(False)
        button_layout.addWidget(self.replace_button)

        self.replace_all_button = QPushButton("Replace All")
        self.replace_all_button.clicked.connect(self.replace_all)
        button_layout.addWidget(self.replace_all_button)

        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        main_layout.addLayout(button_layout)

        # Connect field/text changes to reset search
        self.field_combo.currentIndexChanged.connect(self.reset_search)
        self.field_combo.currentIndexChanged.connect(self.update_button_states)
        self.find_edit.textChanged.connect(self.reset_search)

        # Set initial button states
        self.update_button_states()

    def reset_search(self):
        """Reset search state when criteria changes"""
        self.current_match_index = -1
        self.matches = []
        self.replace_button.setEnabled(False)

    def update_button_states(self):
        """Update button enabled states based on selected field"""
        field_name = self.field_combo.currentText()
        is_tag_search = field_name == "Processed tags in all industries"

        # For tag search, only allow Replace All
        self.find_button.setEnabled(not is_tag_search)
        self.replace_button.setEnabled(False)  # Always disabled until find_next is used
        # Replace All is always enabled

        # Update note label
        if is_tag_search:
            self.note_label.setText("Note: Only 'replace all' allowed in this mode.")
        else:
            self.note_label.setText("Note: Only exact matches (entire field) will be found")

    def get_column_index(self):
        """Get the column index for the selected field"""
        field_name = self.field_combo.currentText()
        if field_name == "Tag":
            return 1  # Column 1 is Tag
        elif field_name == "Local Name":
            return 2  # Column 2 is Local Name
        return -1

    def find_matches(self):
        """Find all exact matches in the selected column or tags"""
        search_text = self.find_edit.text()
        if not search_text:
            return []

        field_name = self.field_combo.currentText()

        # Handle processed tags search
        if field_name == "Processed tags in all industries":
            return self.find_tag_matches(search_text)

        # Handle regular column search
        col_index = self.get_column_index()
        if col_index < 0:
            return []

        matches = []
        model = self.main_window.table_model

        for display_row in range(model.rowCount()):
            cell_value = model.data(model.index(display_row, col_index), Qt.ItemDataRole.DisplayRole)
            if cell_value == search_text:  # Exact match only
                # Store the original index, not the display row
                original_index = model.get_original_index(display_row)
                matches.append(original_index)

        return matches

    def find_tag_matches(self, search_text):
        """Find all exact tag matches across all industries"""
        import sys
        indFile1 = sys.modules['__main__'].indFile1

        matches = []
        for industry_idx, industry in enumerate(indFile1.industries):
            for producer_idx, producer in enumerate(industry.producer):
                # Only check tags if the producer has any
                if hasattr(producer, 'tags') and producer.num_tags > 0:
                    for tag_idx, tag in enumerate(producer.tags):
                        if tag.name == search_text:  # Exact match only
                            matches.append({
                                'industry_idx': industry_idx,
                                'producer_idx': producer_idx,
                                'tag_idx': tag_idx,
                                'industry_name': industry.name
                            })

        return matches

    def find_next(self):
        """Find the next occurrence"""
        search_text = self.find_edit.text()
        if not search_text:
            QMessageBox.warning(self, "Find", "Please enter text to find.")
            return

        # Get all matches if not already found
        if not self.matches:
            self.matches = self.find_matches()
            self.current_match_index = -1

        if not self.matches:
            QMessageBox.information(self, "Find", f"No exact matches found for '{search_text}'")
            return

        # Move to next match (circular)
        self.current_match_index = (self.current_match_index + 1) % len(self.matches)
        match = self.matches[self.current_match_index]

        field_name = self.field_combo.currentText()

        # Handle tag matches - open industry detail dialog
        if field_name == "Processed tags in all industries":
            import sys
            indFile1 = sys.modules['__main__'].indFile1
            cardict = sys.modules['__main__'].cardict

            industry = indFile1.industries[match['industry_idx']]

            # Import and open the industry detail dialog
            from industryDetailDialog import IndustryDetailDialog
            dialog = IndustryDetailDialog(industry, cardict, self.main_window)
            result = dialog.exec()

            # If user saved changes, refresh the table
            if result == IndustryDetailDialog.DialogCode.Accepted:
                industry_data = [ind.to_dict() for ind in indFile1.industries]
                self.main_window.table_model.update_data(industry_data)
                self.main_window.statusBar().showMessage(f'Updated: {industry.name}', 3000)

            # Enable replace button
            self.replace_button.setEnabled(True)

            # Update status
            self.main_window.statusBar().showMessage(
                f"Found tag match {self.current_match_index + 1} of {len(self.matches)} in '{match['industry_name']}'", 5000
            )
        else:
            # Handle regular column matches - select row in table
            original_index = match
            # Convert original index to display row
            display_row = self.main_window.table_model._original_indices.index(original_index)

            table_view = self.main_window.ui.tableView
            model_index = self.main_window.table_model.index(display_row, self.get_column_index())
            table_view.selectRow(display_row)
            table_view.scrollTo(model_index)

            # Enable replace button
            self.replace_button.setEnabled(True)

            # Update status
            self.main_window.statusBar().showMessage(
                f"Found match {self.current_match_index + 1} of {len(self.matches)}", 3000
            )

    def replace_current(self):
        """Replace the current selection"""
        if self.current_match_index < 0 or not self.matches:
            QMessageBox.warning(self, "Replace", "No match selected. Use Find Next first.")
            return

        replace_text = self.replace_edit.text()
        match = self.matches[self.current_match_index]
        field_name = self.field_combo.currentText()

        # Access indFile1 from globals (it's in the same running process)
        import sys
        indFile1 = sys.modules['__main__'].indFile1

        # Handle tag replacement
        if field_name == "Processed tags in all industries":
            industry = indFile1.industries[match['industry_idx']]
            producer = industry.producer[match['producer_idx']]

            if replace_text.strip():
                # Replace with new value
                tag = producer.tags[match['tag_idx']]
                tag.replaceName(replace_text)
                self.main_window.statusBar().showMessage(
                    f"Replaced tag in '{match['industry_name']}'", 3000
                )
            else:
                # Delete the tag if replacing with empty string
                tag_to_delete = producer.tags[match['tag_idx']]
                producer.deleteTag(tag_to_delete.name)
                self.main_window.statusBar().showMessage(
                    f"Deleted tag in '{match['industry_name']}'", 3000
                )
        else:
            # Handle regular column replacement
            original_index = match
            industry = indFile1.industries[original_index]

            if field_name == "Tag":
                industry.replaceSymbol(replace_text)
            elif field_name == "Local Name":
                industry.replaceLocalName(replace_text)

            self.main_window.statusBar().showMessage("Replaced 1 occurrence", 3000)

        # Refresh the main table to show the replacement
        industry_data = [ind.to_dict() for ind in indFile1.industries]
        self.main_window.table_model.update_data(industry_data)

        # Refresh the Industry Detail Dialog if it's open
        if self.main_window.open_detail_dialog is not None:
            self.main_window.open_detail_dialog.refresh()

        # Mark the row as dirty (unsaved changes)
        if field_name == "Processed tags in all industries":
            # Convert original index to display row
            display_row = self.main_window.table_model._original_indices.index(match['industry_idx'])
            self.main_window.table_model.mark_row_dirty(display_row)
        else:
            # Convert original index to display row
            display_row = self.main_window.table_model._original_indices.index(original_index)
            self.main_window.table_model.mark_row_dirty(display_row)

        # Remove this match from the list
        self.matches.pop(self.current_match_index)
        if self.current_match_index >= len(self.matches):
            self.current_match_index = -1

        # If there are more matches, find next
        if self.matches:
            self.find_next()
        else:
            self.replace_button.setEnabled(False)
            QMessageBox.information(self, "Replace", "No more matches to replace.")

    def replace_all(self):
        """Replace all occurrences"""
        search_text = self.find_edit.text()
        replace_text = self.replace_edit.text()

        if not search_text:
            QMessageBox.warning(self, "Replace All", "Please enter text to find.")
            return

        # Find all matches
        matches = self.find_matches()

        if not matches:
            QMessageBox.information(self, "Replace All", f"No exact matches found for '{search_text}'")
            return

        field_name = self.field_combo.currentText()

        # Confirm replace all
        if field_name == "Processed tags in all industries":
            # Count unique industries for better message
            unique_industries = len(set(m['industry_idx'] for m in matches))
            if replace_text.strip():
                message = f"Replace all {len(matches)} tag occurrences of '{search_text}' with '{replace_text}' across {unique_industries} industries?"
            else:
                message = f"Delete all {len(matches)} tag occurrences of '{search_text}' across {unique_industries} industries?"
            reply = QMessageBox.question(
                self,
                "Replace All",
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
        else:
            if replace_text.strip():
                message = f"Replace all {len(matches)} occurrences of '{search_text}' with '{replace_text}'?"
            else:
                message = f"Delete all {len(matches)} occurrences of '{search_text}'?"
            reply = QMessageBox.question(
                self,
                "Replace All",
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

        if reply == QMessageBox.StandardButton.No:
            return

        # Perform replacements
        import sys
        indFile1 = sys.modules['__main__'].indFile1

        if field_name == "Processed tags in all industries":
            # Replace or delete all tag occurrences
            affected_industries = set()
            if replace_text.strip():
                # Replace with new value
                for match in matches:
                    industry = indFile1.industries[match['industry_idx']]
                    producer = industry.producer[match['producer_idx']]
                    tag = producer.tags[match['tag_idx']]
                    tag.replaceName(replace_text)
                    affected_industries.add(match['industry_idx'])
            else:
                # Delete tags (use original search text)
                for match in matches:
                    industry = indFile1.industries[match['industry_idx']]
                    producer = industry.producer[match['producer_idx']]
                    producer.deleteTag(search_text)
                    affected_industries.add(match['industry_idx'])

            action = "Deleted" if not replace_text.strip() else "Replaced"

            # Refresh the table FIRST
            industry_data = [ind.to_dict() for ind in indFile1.industries]
            self.main_window.table_model.update_data(industry_data)

            # Refresh the Industry Detail Dialog if it's open
            if self.main_window.open_detail_dialog is not None:
                self.main_window.open_detail_dialog.refresh()

            # Mark all affected industries as dirty (after refresh)
            for industry_idx in affected_industries:
                display_row = self.main_window.table_model._original_indices.index(industry_idx)
                self.main_window.table_model.mark_row_dirty(display_row)

            QMessageBox.information(self, "Replace All",
                f"{action} {len(matches)} tag occurrences across {unique_industries} industries.")
            self.main_window.statusBar().showMessage(
                f"{action} {len(matches)} tag occurrences", 5000
            )
        else:
            # Replace all column occurrences
            for original_index in matches:
                industry = indFile1.industries[original_index]
                if field_name == "Tag":
                    industry.replaceSymbol(replace_text)
                elif field_name == "Local Name":
                    industry.replaceLocalName(replace_text)

            # Refresh the table FIRST
            industry_data = [ind.to_dict() for ind in indFile1.industries]
            self.main_window.table_model.update_data(industry_data)

            # Refresh the Industry Detail Dialog if it's open
            if self.main_window.open_detail_dialog is not None:
                self.main_window.open_detail_dialog.refresh()

            # Mark all affected rows as dirty (after refresh)
            for original_index in matches:
                display_row = self.main_window.table_model._original_indices.index(original_index)
                self.main_window.table_model.mark_row_dirty(display_row)

            QMessageBox.information(self, "Replace All", f"Replaced {len(matches)} occurrences.")
            self.main_window.statusBar().showMessage(f"Replaced {len(matches)} occurrences", 5000)

        # Reset search
        self.reset_search()
