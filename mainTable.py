from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QBrush, QColor


class DictTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []
        self._headers = list(self._data[0].keys()) if self._data else []
        self._dirty_rows = set()  # Track rows with unsaved changes
        self._original_indices = []  # Map display row to original data structure index

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
        """Replace all data and sort by industry name"""
        self.beginResetModel()

        # Create list of (index, data) tuples to preserve original indices
        indexed_data = list(enumerate(new_data))

        # Sort by industry name (first column, key 'Industry Name')
        if indexed_data and 'Industry Name' in indexed_data[0][1]:
            indexed_data.sort(key=lambda x: x[1]['Industry Name'].lower())

        # Separate the sorted data and original indices
        self._original_indices = [idx for idx, _ in indexed_data]
        self._data = [data for _, data in indexed_data]

        self._headers = list(new_data[0].keys()) if new_data else []

        # Remap dirty rows to new display positions
        if self._dirty_rows:
            # Create reverse mapping: original_index -> display_row
            reverse_map = {orig_idx: display_row for display_row, orig_idx in enumerate(self._original_indices)}
            # Update dirty rows to use display row indices
            self._dirty_rows = {reverse_map[orig_idx] for orig_idx in self._dirty_rows if orig_idx in reverse_map}

        self.endResetModel()

    def get_original_index(self, display_row):
        """Get the original data structure index for a display row"""
        if 0 <= display_row < len(self._original_indices):
            return self._original_indices[display_row]
        return display_row  # Fallback to display row if mapping doesn't exist

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