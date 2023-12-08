from config.general_functions import sort_files_into_groups, new_file_data_ana_bin_nary
from config.func_parsing_svg import new_start_parsing_svg_files, dict_loading, actualizations_vk_svbu
from interface.window_name_system import NameSystemWindow
from os import path, listdir
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextBrowser
from qasync import asyncSlot

import config.conf as conf


class ParsingSvg(QMainWindow):
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

        self.btn_update_vis_svbu = QPushButton('Обновить видеокадры SVBU')
        self.btn_update_vis_svbu.setMinimumHeight(50)
        self.btn_update_vis_svbu.setFont(font)
        self.btn_update_vis_svbu.clicked.connect(self.update_vis_svbu)
        layout.addWidget(self.btn_update_vis_svbu)  # добавить кнопку на подложку для виджетов

        self.btn_update_data_sig = QPushButton('Обновление баз данных сигналов')
        self.btn_update_data_sig.setMinimumHeight(50)
        self.btn_update_data_sig.setFont(font)
        self.btn_update_data_sig.clicked.connect(self.update_data_system)
        layout.addWidget(self.btn_update_data_sig)  # добавить кнопку на подложку для виджетов

        self.btn_parsing_svg = QPushButton('Поиск замечаний на видеокадрах')
        self.btn_parsing_svg.setMinimumHeight(50)
        self.btn_parsing_svg.setFont(font)
        self.btn_parsing_svg.clicked.connect(self.start_parsing_svg)
        layout.addWidget(self.btn_parsing_svg)  # добавить кнопку на подложку для виджетов

        self.btn_sorting_comments = QPushButton('Сортировка найденных замечаний')
        self.btn_sorting_comments.setMinimumHeight(50)
        self.btn_sorting_comments.setFont(font)
        self.btn_sorting_comments.clicked.connect(self.start_sorting_comments)
        layout.addWidget(self.btn_sorting_comments)  # добавить кнопку на подложку для виджетов

        self.text_log = QTextBrowser()
        layout.addWidget(self.text_log)  # добавить QTextBrowser на подложку для виджетов

        self.btn_main_menu = QPushButton('Вернуться в главное меню')
        self.btn_main_menu.setMinimumHeight(50)
        self.btn_main_menu.setFont(font)
        self.btn_main_menu.clicked.connect(self.main_menu_window)  # задать действие при нажатии
        layout.addWidget(self.btn_main_menu)  # добавить кнопку на подложку для виджетов

        self.name_system_vk = NameSystemWindow(func=self.start_actualizations_vk_svbu,
                                               text='Видеокадры какого блока обновить?',
                                               set_name_system={'SVBU_1', 'SVBU_2'})

        self.update_data = NameSystemWindow(func=self.start_new_data_ana_bin_nary,
                                            text='Базу какой из систем обновить?',
                                            set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        self.name_system_parsing_svg = NameSystemWindow(func=self.checking_svg_files,
                                                        text='На каких видеокадрах найти замечания?',
                                                        set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        self.name_system_sorting_comments = NameSystemWindow(func=self.sorting_notes_files,
                                                             text='Для какой системы распределить замечания?',
                                                             set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)  # Разместим подложку в окне

    def update_vis_svbu(self):
        self.name_system_vk.show()

    def update_data_system(self):
        self.update_data.show()

    def start_parsing_svg(self):
        self.name_system_parsing_svg.show()

    def start_sorting_comments(self):
        self.name_system_sorting_comments.show()

    def main_menu_window(self):
        self.main_menu.show()
        self.close()

    @asyncSlot()
    async def start_actualizations_vk_svbu(self, name_directory: str) -> None:
        """Функция запускающая обновление видеокадров SVBU_(1/2)/NPP_models из папки SVBU_(1/2)/NPP_models_new"""
        await self.print_log(text=f'Начато обновление видеокадров {name_directory}/NPP_models '
                                  f'из папки {name_directory}/NPP_models_new')
        await actualizations_vk_svbu(print_log=self.print_log, name_directory=name_directory)
        await self.print_log(text=f'Выполнение программы обновления видеокадров {name_directory} завершено\n')

    @asyncSlot()
    async def start_new_data_ana_bin_nary(self, name_system: str) -> None:
        """Функция запускающая обновление файлов (или их создание если не было) с базами данных сигналов"""
        await self.print_log(f'Начало обновления базы данных сигналов {name_system}')
        await new_file_data_ana_bin_nary(print_log=self.print_log, name_system=name_system)
        await self.print_log(text=f'Обновление базы данных сигналов {name_system} завершено\n')

    @asyncSlot()
    async def checking_svg_files(self, name_directory: str) -> None:
        """
        Функция запускающая поиск неверных привязок на видеокадрах соответствующей системы.
        :return: None
        """
        set_svg = set(listdir(path.join(name_directory, 'NPP_models')))
        await self.print_log(text=f'Старт проверки видеокадров {name_directory}')
        await new_start_parsing_svg_files(print_log=self.print_log, svg=set_svg, directory=name_directory)
        await self.print_log(text='Поиск замечаний завершен\n', color='green')

    @asyncSlot()
    async def sorting_notes_files(self, name_directory: str) -> None:
        """
        Функция запускающая распределение файлов с замечаниями согласно списку принадлежности к группе.
        :return: None
        """
        if name_directory != '0':
            await self.print_log(f'Старт распределения файлов с замечаниями {name_directory} '
                                 f'согласно списку принадлежности к группе')
            vis_groups = await dict_loading(print_log=self.print_log, number_bloc=name_directory)

            if len(vis_groups):
                await sort_files_into_groups(number_bloc=name_directory, group_svg=vis_groups)
                await self.print_log(text='Распределено успешно!\n', color='green')
            else:
                await self.print_log(text='Распределение невозможно!\n', color='red')

    @asyncSlot()
    async def print_log(self, text: str, color: str = 'black') -> None:
        """Программа выводящая переданный текст в окно лога. Цвета можно использовать зеленый - green, красный - red"""
        dict_colors = {'black': QColor(0, 0, 0),
                       'red': QColor(255, 0, 0),
                       'green': QColor(50, 155, 50)}
        self.text_log.setTextColor(dict_colors[color])
        self.text_log.append(text)
