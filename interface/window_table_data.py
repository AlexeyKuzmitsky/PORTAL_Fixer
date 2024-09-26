from os import path
from interface.window_selection_name_file import NameFileWindow
from interface.window_name_system import NameSystemWindow
from interface.window_instruction import Instruction
from interface.window_selection_column import SelectionColumn
from PyQt6.QtWidgets import QHBoxLayout, QTableView, QLineEdit, QLabel, QMessageBox, QFileDialog
from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt6.QtGui import QIcon
from qasync import asyncSlot
from modernization_objects.push_button import QPushButtonModified
from modernization_objects.q_widget import MainWindowModified
from csv import reader
from typing import List, Dict, Any
from config.func_table_data import save_data_to_txt_file, save_data_to_xlsx_file
from multiprocessing import Process
# import pandas as pd


class TableData(MainWindowModified):
    def __init__(self, main_menu):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setting_window_size(width=850, height=650)
        self.instruction_window = Instruction()
        self.main_menu = main_menu

        self.layout.addWidget(QPushButtonModified(text='Загрузить данные из файла',
                                                  func_pressed=self.start_window_choice_system))

        self.name_system: str = ''
        self.name_file: str = ''
        self.list_name_column: Dict[int, str] = dict()
        self.window_choice_system = NameSystemWindow(func=self.start_generation_data,
                                                     text='Файл какой системы загрузить?',
                                                     set_name_system={'SVBU_1', 'SVBU_2', 'SVSU', 'SKU_VP_1', 'SKU_VP_2'}
                                                     )

        self.window_selection_name_file = NameFileWindow(func=self.loading_the_database,
                                                         text='Какой файл загрузить?')

        self.selection_column = None
        self.list_number_columns: List[int] = list()

        # Создаем строку для фильтрации данных
        horizontal_layout_filter = QHBoxLayout()
        horizontal_layout_filter.addWidget(QLabel('Поле для фильтрации: '))
        label = QLabel()
        label.setPixmap(QIcon(path.join('icon', 'filter.svg')).pixmap(35, 35))
        horizontal_layout_filter.addWidget(label)
        self.filter_input = QLineEdit()
        horizontal_layout_filter.addWidget(self.filter_input)

        self.text_number_records = QLabel()
        horizontal_layout_filter.addWidget(self.text_number_records)
        self.layout.addLayout(horizontal_layout_filter)

        self.filter_input.textChanged.connect(self.new_data_table)

        self.name_columns: Dict[int, str] = {}
        self.data_table = QTableView()
        self.data_table.horizontalHeader().sectionDoubleClicked.connect(self.sorted_data_table)
        self.data: List[List[str]] = list()

        self.last_filter_text: str = ''  # текст, который был в последнем запросе
        self.last_data: List[List[str]] = list()  # последняя база выведенная на экран

        self.layout.addWidget(self.data_table)  # добавить таблицу данных

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(QPushButtonModified(func_pressed=self.save_data_to_xlsx_file,
                                                        text=' Импорт в Excel',
                                                        path_icon=path.join('icon', 'excel.svg')))
        horizontal_layout.addWidget(QPushButtonModified(func_pressed=self.save_data_to_text_file,
                                                        text=' Импорт в TXT',
                                                        path_icon=path.join('icon', 'txt.svg')))

        self.layout.addLayout(horizontal_layout)

    def new_data_table(self, text):
        """
        Функция производящая подготовку и вывод новых данных в таблицу
        """
        new_data: List[List[str]] = self.filter_data(text)
        model = TableModel(new_data, self.name_columns)
        self.data_table.setModel(model)
        self.text_number_records.setText(f'Количество записей: {len(new_data)}')
        self.last_data = new_data[:]
        self.data_table.resizeColumnsToContents()

    def check_text_filter(self, text: str):
        if len(text) < 2:
            return False
        if len(text) > len(self.last_filter_text) and text.startswith(self.last_filter_text):
            return True
        return False

    def filter_data(self, text) -> List[List[str]]:
        """
        Функция фильтрации данных в таблице согласно поисковому запросу
        """
        if self.check_text_filter(text=text):
            data = self.last_data[:]
        else:
            data = self.data[:]
        self.last_filter_text = text
        new_data: List[List[str]] = list()
        for i_line in data:
            for i_element in i_line:
                if text in i_element:
                    new_data.append(i_line)
                    break
        return new_data

    @asyncSlot()
    async def start_generation_data(self, name_system: str):
        self.name_system = name_system
        self.window_selection_name_file.show()

    def loading_the_database(self, name_file: str):
        if not path.isfile(path.join(self.name_system, 'DbDumps', name_file)):
            self.error_message(title=f'Нет файла {name_file}',
                               text=f'Невозможно загрузить содержимое файла {self.name_system}/DbDumps/{name_file} '
                                    f'т.к. его нет')
            return
        self.name_file = name_file

        with open(path.join(self.name_system, 'DbDumps', name_file), 'r', encoding='windows-1251') as file_data:
            for __ in range(3):
                next(file_data)
            list_name_column = next(file_data)[2:-1].split('|')
        self.listing_columns(list_name_column=list_name_column)

        self.selection_column = SelectionColumn(func=self.set_list_of_columns,
                                                list_column=list_name_column,
                                                name_file=name_file)
        self.selection_column.show()

    def set_list_of_columns(self, list_column: List[int]):
        if list_column:
            self.list_number_columns = list_column

        self.data_output()

    def data_output(self):
        self.data.clear()
        self.last_data.clear()
        self.name_columns.clear()
        with open(path.join(self.name_system, 'DbDumps', self.name_file), 'r', encoding='windows-1251') as file_data:
            new_text = reader(file_data, delimiter='|', quotechar=' ')
            for __ in range(4):
                new_text.__next__()
            number_column = 0
            for i_num in self.list_number_columns:
                self.name_columns[number_column] = self.list_name_column[i_num]
                number_column += 1
            for i_line in new_text:
                try:
                    self.data.append([i_line[num] for num in self.list_number_columns])
                except IndexError:
                    pass

        ####################
        # df = pd.read_csv(path.join('SKU_VP_2', 'DbDumps', 'PLS_ANA_CONF.dmp'), encoding='windows-1251', sep='|',
        #                  header=3, skipfooter=1, engine='python', dtype='str')
        # number_column = 0
        # print(self.list_name_column)
        #
        # for i_num in self.list_number_columns:
        #     self.name_columns[number_column] = self.list_name_column[i_num]
        #     number_column += 1
        # model = TableModel(df[:], self.name_columns)
        # print(self.name_columns)
        #######################

        self.last_data = self.data
        model = TableModel(self.data, self.name_columns)
        self.data_table.setModel(model)
        self.data_table.resizeColumnsToContents()
        self.text_number_records.setText(f'Количество записей: {len(self.data)}')

    def listing_columns(self, list_name_column):
        num = 0
        for i_name in list_name_column:
            self.list_name_column[num] = i_name
            num += 1

    def start_window_choice_system(self):
        self.window_choice_system.show()

    def main_menu_window(self):
        self.main_menu.show()
        self.close()

    def start_instruction_window(self):
        self.instruction_window.add_text_instruction()
        self.instruction_window.show()

    def development_warning(self):
        QMessageBox.warning(self, 'Функция в разработке',
                            'На данный момент данная функция находится в разработке и не готова к выполнению '
                            'каких либо задачи.\n'
                            'Следите за обновлениями, она скоро заработает!')

    def save_data_to_text_file(self):
        """Функция сохраняющая последнюю базу из таблицы в текстовый файл"""
        if self.last_data:
            data = self.last_data
        elif self.data and not self.filter_input.text():
            data = self.data
        else:
            self.message_empty_database()
            return
        file_name, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл', f'{self.name_file[:-4]}.txt',
                                                   "All Files (*);;Text Files (*.txt)")
        if not file_name:
            return
        file_saving_process = Process(target=save_data_to_txt_file,
                                      args=(data, list(self.name_columns.values()), file_name))
        file_saving_process.start()

    def save_data_to_xlsx_file(self):
        """Функция сохраняющая последнюю базу из таблицы в файл XLSX"""
        if self.last_data:
            data = self.last_data
        elif self.data and not self.filter_input.text():
            data = self.data
        else:
            self.message_empty_database()
            return
        file_name, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл', f'{self.name_file[:-4]}.xlsx',
                                                   "All Files (*);;Книга Excel (*.xlsx)")
        if not file_name:
            return
        file_saving_process = Process(target=save_data_to_xlsx_file,
                                      args=(data, list(self.name_columns.values()), file_name))
        file_saving_process.start()

    def sorted_data_table(self, index: int):
        """
        Функция сортирующая данные по выбранному столбцу
        Args:
            index: номер столбца по которому ведется сортировка
        Returns: None
        """
        new_data: List[List[str]] = list()
        data = sorted(self.last_data[:], key=lambda x: x[index])
        for i_line in data:
            new_data.append(i_line)
        model = TableModel(new_data, self.name_columns)
        self.data_table.setModel(model)
        self.last_data = new_data[:]
        self.data_table.resizeColumnsToContents()

    def message_empty_database(self):
        """Функция выводящая окно с предупреждением """
        QMessageBox.warning(self, 'Нечего сохранять',
                            'В данный момент таблица пуста. Для добавления данных нажмите "Загрузить данные из файла"')

    def error_message(self, title: str, text: str):
        """Сообщение с текстом"""
        QMessageBox.warning(self, title, text)

    def close_program(self):
        """Функция закрытия программы"""
        self.instruction_window.close()
        self.close()


class TableModel(QAbstractTableModel):
    def __init__(self, data: List[List[str]], name_columns: Dict[int, str]):
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
            # return self._data.iloc[index.row(), index.column()]
            return self._data[index.row()][index.column()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = None) -> Any:
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
            # return self._data.shape[1]
            return len(self._data[0])
        except IndexError:
            return 0


#  ↑ ↓ 🠉 🠋  🢁  🢃