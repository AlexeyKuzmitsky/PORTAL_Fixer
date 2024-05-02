import os.path

from interface.window_name_system import NameSystemWindow
from interface.window_instruction import Instruction
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QHBoxLayout, QTextBrowser, QTableView, QTableWidget, QLineEdit, QHeaderView, QLabel
from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex, QSortFilterProxyModel
from qasync import asyncSlot
from modernization_objects.push_button import QPushButtonModified, QPushButtonInstruction, QPushButtonMenu
from modernization_objects.q_widget import MainWindowModified
from config.get_logger import log_info
from csv import reader
from typing import List, Dict


class TableData(MainWindowModified):
    def __init__(self, main_menu):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setting_window_size(width=750, height=650)
        self.instruction_window = Instruction()
        self.main_menu = main_menu

        self.layout.addWidget(QPushButtonModified(text='Сгенерить базу',
                                                  func_pressed=self.generation_data))

        # Создаем строку для фильтрации данных
        horizontal_layout_filter = QHBoxLayout()
        horizontal_layout_filter.addWidget(QLabel('Поле для фильтрации: '))
        self.filter_input = QLineEdit()
        horizontal_layout_filter.addWidget(self.filter_input)

        self.text_number_records = QLabel()
        horizontal_layout_filter.addWidget(self.text_number_records)
        self.layout.addLayout(horizontal_layout_filter)

        self.filter_input.textChanged.connect(self.new_data_table)

        self.name_columns: Dict[int, str] = {}
        self.data_table = QTableView()
        self.data: List[List[str]] = list()

        self.last_filter_text: str = ''  # текст, который был в последнем запросе
        self.last_data: List[List[str]] = list()  # последняя база выведенная на экран

        self.layout.addWidget(self.data_table)  # добавить таблицу данных

        # self.progress = QProgressBar()
        # self.progress.setStyleSheet('text-align: center;')
        # self.layout.addWidget(self.progress)
        # self.progress.setVisible(False)

        horizontal_layout = QHBoxLayout()

        # horizontal_layout.addWidget(self.filter_input)
        horizontal_layout.addWidget(QPushButtonMenu(func_pressed=self.main_menu_window))
        horizontal_layout.addWidget(QPushButtonInstruction(func_pressed=self.start_instruction_window))

        self.layout.addLayout(horizontal_layout)

    def new_data_table(self, text):
        if self.check_text_filter(text=text):
            data = self.last_data
        else:
            data = self.data
        new_data = list()
        for i in data:
            if self.filter_line(text, i):
                # if i[0].startswith(filter_text):
                new_data.append(i)
        model = TableModel(new_data, self.name_columns)
        self.data_table.setModel(model)
        self.text_number_records.setText(f'Количество записей: {len(new_data)}')
        self.last_data = data

    def check_text_filter(self, text: str):
        if len(text) == 1:
            return False
        if len(text) > len(self.last_filter_text) and text.startswith(self.last_filter_text):
            return True
        return False

    def filter_line(self, text, list_element):
        for i in list_element:
            if text in i:
                return True
        return False

    # def on_filter_changed(self, text):
    #     proxy_model = self.data_table.model()
    #     proxy_model.setFilterFixedString(text)

    def generation_data(self):
        with open(os.path.join('SVBU_1', 'DbDumps', 'PLS_BIN_CONF.dmp'), 'r', encoding='windows-1251') as file_data:
            new_text = reader(file_data, delimiter='|', quotechar=' ')
            new_text.__next__()
            new_text.__next__()
            new_text.__next__()
            label = new_text.__next__()
            for i_num_column in range(len(label)):
                self.name_columns[i_num_column] = label[i_num_column]
            for i_line in new_text:
                self.data.append(i_line)

        model = TableModel(self.data[:-1], self.name_columns)
        self.data_table.setModel(model)

    def main_menu_window(self):
        self.main_menu.show()
        self.close()

    # @asyncSlot()
    # async def start_creating_new_file_altstation(self, name_system: str) -> None:
    #     """Функция запускающая обновление файлов (или их создание если не было) с базами данных сигналов"""
    #     await self.print_log(f'Начало создания файла altstation {name_system}')
    #     self.progress.setVisible(True)
    #     self.progress.reset()
    #     await new_start_parsing_svg_files(print_log=self.print_log, name_system=name_system, progress=self.progress)
    #     await self.print_log(text=f'Создание файла altstation {name_system} завершено\n')

    # @asyncSlot()
    # async def start_checking_ana_file_1(self, name_system: str) -> None:
    #     """Функция запускающая проверку файла file_ana-1.txt"""
    #     await self.print_log(f'Начало проверки файла file_ana-1.txt {name_system}')
    #     self.progress.setVisible(True)
    #     self.progress.reset()
    #     await search_for_comments_in_a_ana_file_1(print_log=self.print_log, name_system=name_system,
    #                                               progress=self.progress)
    #     await self.print_log(text=f'Поиск отсутствующих KKS в {name_system}/DbSrc/file_ana-1.txt завершен\n')

    # @asyncSlot()
    # async def start_checking_bin_file(self, name_system: str) -> None:
    #     """Функция запускающая проверку файлов c file_bin00.rep по file_bin13.rep"""
    #     await self.print_log(f'Начало проверки исходных файлов file_bin {name_system}')
    #     self.progress.setVisible(True)
    #     self.progress.reset()
    #     await searching_for_comments_in_files_bin(print_log=self.print_log, name_system=name_system,
    #                                               progress=self.progress)
    #     await self.print_log(text=f'Поиск замечаний в {name_system}/DbSrc/file_bin завершен\n')

    # @asyncSlot()
    # async def start_checking_bin_file_1(self, name_system: str) -> None:
    #     """Функция запускающая проверку файла file_bin-1.txt"""
    #     await self.print_log(f'Начало проверки файла file_bin-1.txt {name_system}')
    #     self.progress.setVisible(True)
    #     self.progress.reset()
    #     await search_for_comments_in_a_bin_file_1(print_log=self.print_log, name_system=name_system,
    #                                               progress=self.progress)
    #     await self.print_log(text=f'Поиск отсутствующих KKS в {name_system}/DbSrc/file_bin-1.txt завершен\n')

    # @asyncSlot()
    # async def print_log(self, text: str, color: str = 'white', level: str = 'INFO', a_new_line: bool = True) -> None:
    #     """
    #     Программа выводящая переданный текст в окно лога.
    #     Args:
    #         text: текст, который будет выводиться
    #         color: цвет текста (по умолчанию white)
    #         level: Уровень лога (по умолчанию INFO)
    #         a_new_line: Выводить с новой строки или продолжить старую (по умолчанию выводить с новой - True)
    #     Returns: None
    #     """
    #     dict_colors = {
    #         'white': QColor(169, 183, 198),
    #         'black': QColor(0, 0, 0),
    #         'red': QColor(255, 0, 0),
    #         'green': QColor(50, 155, 50),
    #         'yellow': QColor(255, 255, 0)
    #     }
    #     self.text_log.setTextColor(dict_colors[color])
    #     if a_new_line:
    #         self.text_log.append(text)
    #     else:
    #         self.text_log.textCursor().insertText(text)
    #     if level == 'INFO':
    #         log_info.info(text.replace('\n', ' '))
    #     elif level == 'ERROR':
    #         log_info.error(text.replace('\n', ' '))

    def start_instruction_window(self):
        self.instruction_window.add_text_instruction()
        self.instruction_window.show()

    def close_program(self):
        """Функция закрытия программы"""
        self.instruction_window.close()
        # self.creating_file_alt_station.close()
        # self.checking_file_ana_1.close()
        # self.checking_file_bin_1.close()
        # self.checking_file_bin_rep.close()
        self.close()


class TableModel(QAbstractTableModel):
    def __init__(self, data, name_columns):
        super(TableModel, self).__init__()
        self._data = data
        self.name_columns = name_columns
        self.items = []

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        """
        Заполнение таблицы данными
        """
        if not index.isValid():
            return
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        """
        Формирование подписей столбцов и строк
        """
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.name_columns.get(section)
            elif orientation == Qt.Orientation.Vertical:
                return section + 1

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

    # def setItems(self, items):
    #     self.items = items
