from config.general_functions import check_directory

from interface.window_name_system import NameSystemWindow
from csv import reader

import interface.conf as conf
from os import getcwd, path, listdir, rename, remove
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextBrowser, QLabel, QMessageBox

from qasync import asyncSlot


class GenerationTcpGate(QMainWindow):
    def __init__(self, main_menu):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setWindowTitle(f'{conf.name_program} - v.{conf.version_program}')  # изменим текст заглавия
        self.setMinimumSize(QSize(750, 350))  # Устанавливаем минимальный размер окна 750(ширина) на 350(высота)
        self.setWindowIcon(QIcon(path.join('image', 'icon.png')))

        self.main_menu = main_menu
        font = QFont()
        font.setFamily('MS Shell Dlg 2')
        font.setPointSize(12)

        layout = QVBoxLayout()

        self.btn_update_data_sig = QPushButton('Обновление баз данных сигналов')
        self.btn_update_data_sig.setMinimumHeight(50)
        self.btn_update_data_sig.setFont(font)
        self.btn_update_data_sig.clicked.connect(self.update_data_system)
        layout.addWidget(self.btn_update_data_sig)  # добавить кнопку на подложку для виджетов

        self.btn_parsing_svg = QPushButton('Создание файла ZPUPD.cfg')
        self.btn_parsing_svg.setMinimumHeight(50)
        self.btn_parsing_svg.setFont(font)
        self.btn_parsing_svg.clicked.connect(self.tcp_gate_system)
        layout.addWidget(self.btn_parsing_svg)  # добавить кнопку на подложку для виджетов

        self.text_log = QTextBrowser()
        layout.addWidget(self.text_log)  # добавить QTextBrowser на подложку для виджетов

        self.btn_main_menu = QPushButton('Вернуться в главное меню')
        self.btn_main_menu.setMinimumHeight(50)
        self.btn_main_menu.setFont(font)
        self.btn_main_menu.clicked.connect(self.main_menu_window)  # задать действие при нажатии
        layout.addWidget(self.btn_main_menu)  # добавить кнопку на подложку для виджетов

        self.update_data = NameSystemWindow(func=self.new_data_ana_bin_nary,
                                            text='Базу какой из систем обновить?',
                                            set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        self.name_system_tcp_gate = NameSystemWindow(func=self.checking_svg_files,
                                                     text='Для какой системы создать файл ZPUPD.cfg?',
                                                     set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)  # Разместим подложку в окне

    def update_data_system(self):
        self.update_data.show()

    def tcp_gate_system(self):
        self.name_system_tcp_gate.show()

    @asyncSlot()
    async def checking_svg_files(self, name_directory: str) -> None:
        """
        Функция запускающая создание файла ZPUPD.cfg.
        :return: None
        """
        await self.print_log(text=f'Старт создания файла ZPUPD.cfg для {name_directory}')
        await self.generation_tcp_gate(directory=name_directory)
        await self.print_log(text='Поиск замечаний завершен\n', color='green')

    @asyncSlot()
    async def new_data_ana_bin_nary(self, name_system: str) -> None:
        """
        Функция обновления файлов со списком KKS сигналов. По завершению обновляются (создаются если не было) 3 файла:
        BIN_list_kks.txt со списком бинарных сигналов
        NARY_list_kks.txt со списком много битовых сигналов
        ANA_list_kks.txt со списков аналоговых сигналов
        :param name_system: папка в которой будут обновления.
        :return: None
        """
        check_directory(path_directory=name_system, name_directory='DbDumps')
        check_directory(path_directory=name_system, name_directory='data')

        set_kks_bin_date = set()
        set_kks_nary_date = set()
        set_kks_ana_date = set()

        await self.print_log(text='Сбор BIN сигналов')

        with open(path.join(name_system, 'DbDumps', 'PLS_BIN_CONF.dmp'), 'r', encoding='windows-1251') as file:
            new_text = reader(file, delimiter='|')
            for i_line in new_text:
                try:
                    full_kks = i_line[42]
                    if i_line[14] == '-1':

                        set_kks_bin_date.add(full_kks)
                    else:
                        set_kks_nary_date.add(full_kks)
                except IndexError:
                    ...

        with open(path.join(name_system, 'data', 'BIN_list_kks.txt'), 'w', encoding='UTF-8') as file:
            for i_kks in sorted(set_kks_bin_date):
                file.write(f'{i_kks}\n')

        with open(path.join(name_system, 'data', 'NARY_list_kks.txt'), 'w', encoding='UTF-8') as file:
            for i_kks in sorted(set_kks_nary_date):
                file.write(f'{i_kks}\n')

        await self.print_log(text='Сигналы BIN собраны успешно', color='green')

        await self.print_log(text='Сбор ANA сигналов')

        with open(path.join(name_system, 'DbDumps', 'PLS_ANA_CONF.dmp'), 'r', encoding='windows-1251') as file:
            new_text = reader(file, delimiter='|', quotechar=' ')
            for i_line in new_text:
                try:
                    set_kks_ana_date.add(i_line[78])
                except IndexError:
                    pass

        with open(path.join(name_system, 'data', 'ANA_list_kks.txt'), 'w', encoding='UTF-8') as file:
            for i_kks in sorted(set_kks_ana_date):
                file.write(f'{i_kks}\n')
        await self.print_log(text='Сигналы ANA собраны успешно', color='green')
        await self.print_log(text=f'Обновление базы данных сигналов {name_system} завершено\n', color='green')

    def main_menu_window(self):
        self.main_menu.show()
        self.close()

    @asyncSlot()
    async def print_log(self, text: str, color: str = 'black') -> None:
        """Программа выводящая переданный текст в окно лога. Цвета можно использовать зеленый - green, красный - red"""
        dict_colors = {'black': QColor(0, 0, 0),
                       'red': QColor(255, 0, 0),
                       'green': QColor(50, 155, 50)}
        self.text_log.setTextColor(dict_colors[color])
        self.text_log.append(text)
