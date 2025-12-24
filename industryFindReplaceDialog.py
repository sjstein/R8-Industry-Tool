from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QGroupBox,
                               QFormLayout, QMessageBox)
from PySide6.QtCore import Qt


class IndustryFindReplaceDialog(QDialog):
    def __init__(self, industry, producers_table, parent=None, main_window=None, industry_row=None, cardict=None):
        super().__init__(parent)
        self.setWindowTitle(f"Find and Replace Tags - {industry.name}")
        self.setModal(False)  # Allow interaction with parent dialog
        self.resize(400, 200)

        # Store references
        self.industry = industry
        self.producers_table = producers_table
        self.parent_dialog = parent
        self.main_window = main_window
        self.industry_row = industry_row
        self.cardict = cardict or {}
        self.current_match_index = -1
        self.matches = []

        # Main layout
        main_layout = QVBoxLayout(self)

        # Search criteria group
        criteria_group = QGroupBox("Search in Processed Tags")
        criteria_layout = QFormLayout()

        # Find what
        self.find_edit = QLineEdit()
        self.find_edit.setPlaceholderText("Enter exact tag to find")
        criteria_layout.addRow("Find what:", self.find_edit)

        # Replace with
        self.replace_edit = QLineEdit()
        self.replace_edit.setPlaceholderText("Enter replacement tag")
        criteria_layout.addRow("Replace with:", self.replace_edit)

        criteria_group.setLayout(criteria_layout)
        main_layout.addWidget(criteria_group)

        # Note about exact matching
        note_label = QLabel("Note: Only exact tag matches (entire tag) will be found")
        note_label.setStyleSheet("color: gray; font-style: italic;")
        main_layout.addWidget(note_label)

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

        # Connect text changes to reset search
        self.find_edit.textChanged.connect(self.reset_search)

    def reset_search(self):
        """Reset search state when criteria changes"""
        self.current_match_index = -1
        self.matches = []
        self.replace_button.setEnabled(False)

    def find_table_row_for_producer(self, bIndex):
        """Find the table row for a producer with the given bIndex (car type ID)"""
        # Search through table rows to find the one with matching bIndex in column 0
        for row in range(self.producers_table.rowCount()):
            item = self.producers_table.item(row, 0)  # Column 0 contains bIndex
            if item and int(item.text()) == bIndex:
                return row
        return -1  # Not found

    def find_tag_matches(self, search_text):
        """Find all exact tag matches in this industry"""
        matches = []
        for producer_idx, producer in enumerate(self.industry.producer):
            # Only check tags if the producer has any
            if hasattr(producer, 'tags') and producer.num_tags > 0:
                for tag_idx, tag in enumerate(producer.tags):
                    if tag.name == search_text:  # Exact match only
                        matches.append({
                            'producer_idx': producer_idx,
                            'tag_idx': tag_idx
                        })

        # Sort matches by car type name (same order as table display)
        matches.sort(key=lambda m: self.cardict.get(
            str(self.industry.producer[m['producer_idx']].bIndex),
            "Unknown"
        ).lower())

        return matches

    def find_next(self):
        """Find the next occurrence"""
        search_text = self.find_edit.text()
        if not search_text:
            QMessageBox.warning(self, "Find", "Please enter a tag to find.")
            return

        # Get all matches if not already found
        if not self.matches:
            self.matches = self.find_tag_matches(search_text)
            self.current_match_index = -1

        if not self.matches:
            QMessageBox.information(self, "Find", f"No exact matches found for tag '{search_text}'")
            return

        # Move to next match (circular)
        self.current_match_index = (self.current_match_index + 1) % len(self.matches)
        match = self.matches[self.current_match_index]

        # Find the table row for this producer (table is sorted, so row != producer_idx)
        producer = self.industry.producer[match['producer_idx']]
        table_row = self.find_table_row_for_producer(producer.bIndex)

        if table_row >= 0:
            # Select the producer row in the table and the tags cell
            self.producers_table.setCurrentCell(table_row, 2)  # Column 2 is tags
            self.producers_table.scrollToItem(
                self.producers_table.item(table_row, 0)
            )

            # Enter edit mode and highlight just the search text
            self.producers_table.editItem(self.producers_table.item(table_row, 2))

            # Delay selection to run after the delegate has set up the editor
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self._select_found_tag(table_row, search_text))

        # Enable replace button
        self.replace_button.setEnabled(True)

        # Update parent status
        if self.parent_dialog:
            self.parent_dialog.statusBar().showMessage(
                f"Found tag match {self.current_match_index + 1} of {len(self.matches)}", 3000
            ) if hasattr(self.parent_dialog, 'statusBar') else None

    def replace_current(self):
        """Replace the current selection"""
        if self.current_match_index < 0 or not self.matches:
            QMessageBox.warning(self, "Replace", "No match selected. Use Find Next first.")
            return

        replace_text = self.replace_edit.text()
        match = self.matches[self.current_match_index]

        # Replace or delete the tag
        producer = self.industry.producer[match['producer_idx']]

        if replace_text.strip():
            # Replace with new value
            tag = producer.tags[match['tag_idx']]
            tag.replaceName(replace_text)
        else:
            # Delete the tag if replacing with empty string
            tag_to_delete = producer.tags[match['tag_idx']]
            producer.deleteTag(tag_to_delete.name)

        # Refresh the producers table display
        self.refresh_producer_row(match['producer_idx'])

        # Mark the industry as dirty in the main window
        if self.main_window and self.industry_row is not None:
            # Convert original index to display row
            display_row = self.main_window.table_model._original_indices.index(self.industry_row)
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
        """Replace all occurrences in this industry"""
        search_text = self.find_edit.text()
        replace_text = self.replace_edit.text()

        if not search_text:
            QMessageBox.warning(self, "Replace All", "Please enter a tag to find.")
            return

        # Find all matches
        matches = self.find_tag_matches(search_text)

        if not matches:
            QMessageBox.information(self, "Replace All", f"No exact matches found for tag '{search_text}'")
            return

        # Confirm replace all
        if replace_text.strip():
            message = f"Replace all {len(matches)} occurrences of tag '{search_text}' with '{replace_text}' in this industry?"
        else:
            message = f"Delete all {len(matches)} occurrences of tag '{search_text}' in this industry?"
        reply = QMessageBox.question(
            self,
            "Replace All",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # Track which producer rows need refreshing
        affected_producers = set()

        # Perform replacements or deletions
        if replace_text.strip():
            # Replace with new value
            for match in matches:
                producer = self.industry.producer[match['producer_idx']]
                tag = producer.tags[match['tag_idx']]
                tag.replaceName(replace_text)
                affected_producers.add(match['producer_idx'])
        else:
            # Delete tags (use original search text since all matches have this name)
            for match in matches:
                producer = self.industry.producer[match['producer_idx']]
                producer.deleteTag(search_text)
                affected_producers.add(match['producer_idx'])

        # Refresh affected producer rows
        for producer_idx in affected_producers:
            self.refresh_producer_row(producer_idx)

        # Also refresh the parent detail dialog to ensure everything updates
        if self.parent_dialog is not None:
            self.parent_dialog.load_producers()

        # Mark the industry as dirty in the main window
        if self.main_window and self.industry_row is not None:
            # Convert original index to display row
            display_row = self.main_window.table_model._original_indices.index(self.industry_row)
            self.main_window.table_model.mark_row_dirty(display_row)

        # Reset search
        self.reset_search()

        action = "Deleted" if not replace_text.strip() else "Replaced"
        QMessageBox.information(self, "Replace All", f"{action} {len(matches)} tag occurrences.")

    def _select_found_tag(self, table_row, search_text):
        """Select only the found tag in the editor, not the entire cell"""
        from PySide6.QtWidgets import QLineEdit

        # Get the cell editor
        editor = self.producers_table.cellWidget(table_row, 2)
        if editor is None:
            editor = self.producers_table.findChild(QLineEdit)

        if editor and isinstance(editor, QLineEdit):
            # Find position of search text in comma-separated tags
            tags_text = self.producers_table.item(table_row, 2).text()
            tags_list = [tag.strip() for tag in tags_text.split(',')]

            pos = 0
            for tag in tags_list:
                if tag == search_text:
                    # Found it - select this tag only
                    editor.setSelection(pos, len(search_text))
                    break
                pos += len(tag) + 2  # +2 for ", " separator

    def refresh_producer_row(self, producer_idx):
        """Refresh the tags display for a specific producer row"""
        producer = self.industry.producer[producer_idx]
        tags_str = producer.returnTags() if producer.num_tags > 0 else ""

        # Find the table row for this producer (table is sorted, so row != producer_idx)
        table_row = self.find_table_row_for_producer(producer.bIndex)

        if table_row >= 0:
            # Update the tags cell (column 2)
            from PySide6.QtWidgets import QTableWidgetItem
            self.producers_table.setItem(table_row, 2, QTableWidgetItem(tags_str))
