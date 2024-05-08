from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import Any


class TableModel(QAbstractTableModel):
    def __init__(self, data, name_columns=None):
        super(TableModel, self).__init__()
        self._data = data
        self.name_columns = name_columns

    def data(self, index: QModelIndex, role: int = None):
        """
        Заполнение таблицы данными
        """
        if not index.isValid():
            return
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = None) -> Any:
        """
        Формирование подписей столбцов и строк
        """
        if role == Qt.ItemDataRole.DisplayRole:
            try:
                if orientation == Qt.Orientation.Horizontal:
                    return self.name_columns.get(section)
                elif orientation == Qt.Orientation.Vertical:
                    return section + 1
            except AttributeError:
                return ''

    def rowCount(self, index: int = None):
        """
        Поиск количество строк. Берет количество строк в данных.
        """
        return len(self._data)

    def columnCount(self, index: int = None):
        """
        Поиск количество столбцов. Берет первую строку данных и подсчитывает его длину.
        Работает только если одинаковое количество столбцов
        """
        try:
            return len(self._data[0])
        except IndexError:
            return 0
