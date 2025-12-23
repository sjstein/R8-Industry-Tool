from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QBrush, QColor


class DictTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []
        self._headers = list(self._data[0].keys()) if self._data else []
        self._dirty_rows = set()  # Track rows with unsaved changes
        self._original_indices = []  # Map display row to original data structure index
        self._sort_column = -1  # Track current sort column
        self._sort_order = Qt.SortOrder.AscendingOrder  # Track current sort order

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):  # Changed here
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:  # Changed here
            row = self._data[index.row()]
            column_key = self._headers[index.column()]
            return str(row.get(column_key, ''))

        elif role == Qt.ItemDataRole.BackgroundRole:
            # Highlight dirty (unsaved) rows with yellow background
            if index.row() in self._dirty_rows:
                return QBrush(QColor(255, 255, 200))  # Light yellow

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):  # Changed here
        if role == Qt.ItemDataRole.DisplayRole:  # Changed here
            if orientation == Qt.Orientation.Horizontal:  # Also changed this
                return self._headers[section]
            else:
                return str(section + 1)
        return None

    def add_record(self, record_dict):
        """Add a new record to the table"""
        position = len(self._data)
        self.beginInsertRows(QModelIndex(), position, position)
        self._data.append(record_dict)
        self.endInsertRows()

    def update_data(self, new_data):
        """Replace all data and re-apply current sort"""
        # Convert dirty rows from display indices to original indices BEFORE resetting
        dirty_original_indices = set()
        for display_row in self._dirty_rows:
            if display_row < len(self._original_indices):
                dirty_original_indices.add(self._original_indices[display_row])

        self.beginResetModel()

        # Initialize with original order
        self._data = new_data
        self._original_indices = list(range(len(new_data)))
        self._headers = list(new_data[0].keys()) if new_data else []

        # Restore dirty rows as original indices (which are now also display indices since unsorted)
        self._dirty_rows = dirty_original_indices

        self.endResetModel()

        # Re-apply the current sort if one was set
        if self._sort_column >= 0 and self._sort_column < len(self._headers):
            # Use the internal sort logic without emitting signals again
            self._apply_sort(self._sort_column, self._sort_order)

    def _apply_sort(self, column, order):
        """Internal method to apply sort after update_data"""
        if not self._data or column < 0 or column >= len(self._headers):
            return

        # Get the column key
        column_key = self._headers[column]

        # Save dirty rows as original indices before sorting
        dirty_original_indices = set()
        for display_row in self._dirty_rows:
            if display_row < len(self._original_indices):
                dirty_original_indices.add(self._original_indices[display_row])

        # Create list of (original_index, data) tuples
        indexed_data = list(zip(self._original_indices, self._data))

        # Define sort key function that handles different data types
        def sort_key(item):
            value = item[1].get(column_key, '')
            # Convert to string and lowercase for consistent sorting
            if isinstance(value, str):
                return value.lower()
            elif isinstance(value, (int, float)):
                # For numbers, return them as-is (will sort numerically)
                return value
            else:
                return str(value).lower()

        # Sort the data
        indexed_data.sort(key=sort_key, reverse=(order == Qt.SortOrder.DescendingOrder))

        # Separate the sorted data and original indices
        self._original_indices = [idx for idx, _ in indexed_data]
        self._data = [data for _, data in indexed_data]

        # Remap dirty rows from original indices to new display positions
        if dirty_original_indices:
            reverse_map = {orig_idx: display_row for display_row, orig_idx in enumerate(self._original_indices)}
            self._dirty_rows = {reverse_map[orig_idx] for orig_idx in dirty_original_indices if orig_idx in reverse_map}

    def get_original_index(self, display_row):
        """Get the original data structure index for a display row"""
        if 0 <= display_row < len(self._original_indices):
            return self._original_indices[display_row]
        return display_row  # Fallback to display row if mapping doesn't exist

    def sort(self, column, order):
        """Sort the table by the specified column"""
        if not self._data or column < 0 or column >= len(self._headers):
            return

        # Remember the current sort settings
        self._sort_column = column
        self._sort_order = order

        self.layoutAboutToBeChanged.emit()

        # Get the column key
        column_key = self._headers[column]

        # Create list of (original_index, data) tuples
        indexed_data = list(zip(self._original_indices, self._data))

        # Define sort key function that handles different data types
        def sort_key(item):
            value = item[1].get(column_key, '')
            # Convert to string and lowercase for consistent sorting
            if isinstance(value, str):
                return value.lower()
            elif isinstance(value, (int, float)):
                # For numbers, return them as-is (will sort numerically)
                return value
            else:
                return str(value).lower()

        # Sort the data
        indexed_data.sort(key=sort_key, reverse=(order == Qt.SortOrder.DescendingOrder))

        # Separate the sorted data and original indices
        self._original_indices = [idx for idx, _ in indexed_data]
        self._data = [data for _, data in indexed_data]

        # Remap dirty rows to new display positions
        if self._dirty_rows:
            # Convert dirty rows from old display positions to original indices
            old_dirty_original = {self._original_indices[row] for row in self._dirty_rows if row < len(self._original_indices)}
            # Create reverse mapping: original_index -> new display_row
            reverse_map = {orig_idx: display_row for display_row, orig_idx in enumerate(self._original_indices)}
            # Update dirty rows to use new display row indices
            self._dirty_rows = {reverse_map[orig_idx] for orig_idx in old_dirty_original if orig_idx in reverse_map}

        self.layoutChanged.emit()

    def mark_row_dirty(self, row):
        """Mark a row as having unsaved changes"""
        self._dirty_rows.add(row)
        # Notify the view that this row needs to be repainted
        left_index = self.index(row, 0)
        right_index = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(left_index, right_index, [Qt.ItemDataRole.BackgroundRole])

    def clear_dirty_flags(self):
        """Clear all dirty row flags (after saving)"""
        if self._dirty_rows:
            # Get the range of rows that were dirty
            min_row = min(self._dirty_rows)
            max_row = max(self._dirty_rows)
            self._dirty_rows.clear()
            # Notify the view that these rows need to be repainted
            left_index = self.index(min_row, 0)
            right_index = self.index(max_row, self.columnCount() - 1)
            self.dataChanged.emit(left_index, right_index, [Qt.ItemDataRole.BackgroundRole])