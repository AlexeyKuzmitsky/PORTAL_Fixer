from PyQt6.QtWidgets import QCheckBox, QTableWidget, QTableWidgetItem
from config.conf import column_descriptions_ana, column_descriptions_bin
from modernization_objects.push_button import QPushButtonModified
from modernization_objects.q_widget import MainWindowModified
from typing import List, Dict


class SelectionColumn(MainWindowModified):
    def __init__(self, func, list_column: List[str], name_file: str):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setting_window_size(width=700, height=750)
        self.name_file: str = name_file
        self.func = func
        self.list_column = list_column
        if name_file == 'PLS_ANA_CONF.dmp':
            self.list_number_columns: List[int] = [0, 6, 17, 19, 20, 42, 60, 61, 62, 78, 79, 83]
            self.dict_column_descriptions: Dict[str, str] = column_descriptions_ana
        elif name_file == 'PLS_BIN_CONF.dmp':
            self.list_number_columns: List[int] = [0, 42, 43, 47]
            self.dict_column_descriptions: Dict[str, str] = column_descriptions_bin
        self.dict_check_box = dict()

        self.table = QTableWidget(len(list_column), 3)

        self.table.setHorizontalHeaderItem(0, QTableWidgetItem('Check'))
        self.table.setHorizontalHeaderItem(1, QTableWidgetItem('Название столбца'))
        self.table.setHorizontalHeaderItem(2, QTableWidgetItem('Описание столбца'))
        self.filling_the_table_with_data(list_column=list_column)
        self.table.horizontalHeader().sectionDoubleClicked.connect(self.on_header_double_clicked)
        self.layout.addWidget(self.table)  # добавить таблицу данных
        self.table.resizeColumnsToContents()

        self.layout.addWidget(QPushButtonModified(text='Загрузить выбранные столбцы',
                                                  func_pressed=self.apply_column_selection))

    def on_header_double_clicked(self, index):
        """
        Функция выбора в таблице всех пунктов или отмена выбора
        """
        if index == 0:
            flag = True
            for row in range(len(self.list_column)):
                checkbox = self.table.cellWidget(row, 0)
                if not checkbox.isChecked():
                    flag = False
                    break
            if flag:
                for row in range(len(self.list_column)):
                    self.table.cellWidget(row, 0).setChecked(False)
            else:
                for row in range(len(self.list_column)):
                    self.table.cellWidget(row, 0).setChecked(True)

    def filling_the_table_with_data(self, list_column: List[str]):
        """
        Функция заполнения таблицы данными
        """
        for row in range(len(list_column)):
            check_widget = QCheckBox()
            self.dict_check_box[row] = check_widget
            check_widget.setObjectName(str(row))
            if row in self.list_number_columns:
                check_widget.setChecked(True)
            self.table.setCellWidget(row, 0, check_widget)
            name_column = list_column[row]
            self.table.setItem(row, 1, QTableWidgetItem(name_column))
            if name_column in self.dict_column_descriptions:
                self.table.setItem(row, 2, QTableWidgetItem(self.dict_column_descriptions[name_column]))

    def apply_column_selection(self):
        data = list()
        for row, check in self.dict_check_box.items():
            if check.isChecked():
                data.append(row)
        self.func(data)
        self.close_program()

    def close_program(self):
        """Функция закрытия программы"""
        self.close()
