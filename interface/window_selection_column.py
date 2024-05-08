from PyQt6.QtWidgets import QLabel, QMessageBox, QCheckBox, QTableWidget, QTableWidgetItem

from modernization_objects.push_button import QPushButtonModified
from modernization_objects.q_widget import MainWindowModified
from typing import List, Dict


class SelectionColumn(MainWindowModified):
    def __init__(self, func, list_column: List[str], name_file: str):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        print('Создание окна')
        self.setting_window_size(width=350, height=650)

        self.name_file: str = name_file
        self.list_name_column: List[str] = list_column
        self.func = func
        if name_file == 'PLS_ANA_CONF.dmp':
            self.list_number_columns: List[int] = [0, 30, 31, 32, 33, 34, 35, 36, 37, 38, 78, 79, 80]
        elif name_file == 'PLS_BIN_CONF.dmp':
            self.list_number_columns: List[int] = [0, 42, 43, 47]
        self.list_check_box = list()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setRowCount(len(list_column))
        self.table.setHorizontalHeaderLabels(['Check', 'Название столбца', 'Описание столбца'])

        for row in range(len(list_column)):
            check_widget = QCheckBox()
            check_widget.setStyleSheet("QCheckBox::indicator {width: 70px; height: 30px;}")
            self.table.setCellWidget(row, 0, check_widget)

            item = QTableWidgetItem(list_column[row])
            self.table.setItem(row, 1, item)

        self.layout.addWidget(self.table)  # добавить таблицу данных
        self.table.resizeColumnsToContents()

        self.layout.addWidget(QPushButtonModified(text='Загрузить выбранные столбцы',
                                                  func_pressed=self.apply_column_selection))

    def apply_column_selection(self):
        self.func(self.list_number_columns)
        self.close_program()

    def development_warning(self):
        QMessageBox.warning(self, 'Программа в разработке',
                            'На данный момент данная программа находится в разработке и не готова к выполнению '
                            'каких либо функций.\n'
                            'Следите за обновлениями, она скоро заработает!')

    def close_program(self):
        """Функция закрытия программы"""
        self.close()
