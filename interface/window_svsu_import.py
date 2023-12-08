from config.general_functions import new_file_data_ana_bin_nary
from config.func_svsu_import import enumeration_of_svg, actualizations_vk_svbu, actualizations_vk_svsu
from interface.window_name_system import NameSystemWindow
from os import getcwd, path
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextBrowser
from qasync import asyncSlot

import config.conf as conf

class SvsuImport(QMainWindow):
    def __init__(self, main_menu):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setWindowTitle(f'{conf.name_program} - v.{conf.version_program}')  # изменим текст заглавия
        self.setMinimumSize(QSize(750, 350))  # Устанавливаем минимальный размер окна 750(ширина) на 350(высота)
        # self.setWindowIcon(QIcon(path.join('image', 'icon.png')))

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

        self.btn_update_vis_svsu = QPushButton('Обновить видеокадры SVSU из самых актуальных видеокадров SVBU')
        self.btn_update_vis_svsu.setMinimumHeight(50)
        self.btn_update_vis_svsu.setFont(font)
        self.btn_update_vis_svsu.clicked.connect(self.update_vis_svsu)
        layout.addWidget(self.btn_update_vis_svsu)  # добавить кнопку на подложку для виджетов

        self.btn_block_button_svg = QPushButton('Сделать неактивными кнопки на кадрах с несуществующими ссылками')
        self.btn_block_button_svg.setMinimumHeight(50)
        self.btn_block_button_svg.setFont(font)
        self.btn_block_button_svg.clicked.connect(self.start_bloc_button)
        layout.addWidget(self.btn_block_button_svg)  # добавить кнопку на подложку для виджетов

        self.btn_update_data_sig = QPushButton('Обновление баз данных сигналов')
        self.btn_update_data_sig.setMinimumHeight(50)
        self.btn_update_data_sig.setFont(font)
        self.btn_update_data_sig.clicked.connect(self.update_data_system)
        layout.addWidget(self.btn_update_data_sig)  # добавить кнопку на подложку для виджетов

        self.btn_add_file_svsu_import = QPushButton('Создать файл SVSU_IMPORT.txt')
        self.btn_add_file_svsu_import.setMinimumHeight(50)
        self.btn_add_file_svsu_import.setFont(font)
        self.btn_add_file_svsu_import.clicked.connect(self.update_file_svsu_import)
        layout.addWidget(self.btn_add_file_svsu_import)  # добавить кнопку на подложку для виджетов

        self.text_log = QTextBrowser()
        layout.addWidget(self.text_log)  # добавить QTextBrowser на подложку для виджетов

        self.btn_main_menu = QPushButton('Вернуться в главное меню')
        self.btn_main_menu.setMinimumHeight(50)
        self.btn_main_menu.setFont(font)
        self.btn_main_menu.clicked.connect(self.main_menu_window)  # задать действие при нажатии
        layout.addWidget(self.btn_main_menu)  # добавить кнопку на подложку для виджетов

        self.name_system_vk_svbu = NameSystemWindow(func=self.start_actualizations_vk_svbu,
                                                    text='Видеокадры какого блока обновить?',
                                                    set_name_system={'SVBU_1', 'SVBU_2'})
        self.name_system_vk_svsu = NameSystemWindow(func=self.start_actualizations_vk_svsu,
                                                    text='Видеокадры какого блока обновить?',
                                                    set_name_system={'SVBU_1', 'SVBU_2'})
        self.update_data = NameSystemWindow(func=self.start_new_data_ana_bin_nary,
                                            text='Базу какой из систем обновить?',
                                            set_name_system={'SVBU_1', 'SVBU_2', 'SVSU'})
        self.name_system_svsu_import = NameSystemWindow(func=self.start_add_file_svsu_import,
                                                        text='Для какого блока создать файл SVSU_IMPORT.txt?',
                                                        set_name_system={'SVBU_1', 'SVBU_2'})

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)  # Разместим подложку в окне

    def add_text(self):
        text = getcwd()
        self.text_log.append(f'Нажата одна их кнопок {text}')

    def update_vis_svbu(self):
        self.name_system_vk_svbu.show()

    def update_vis_svsu(self):
        self.name_system_vk_svsu.show()

    def update_data_system(self):
        self.update_data.show()

    def update_file_svsu_import(self):
        self.name_system_svsu_import.show()

    def main_menu_window(self):
        self.main_menu.show()
        self.close()

    @asyncSlot()
    async def start_actualizations_vk_svbu(self, name_directory: str) -> None:
        """Функция запускающая обновление видеокадров SVBU"""
        await self.print_log(f'Начало обновления видеокадров {name_directory}')
        await actualizations_vk_svbu(print_log=self.print_log, name_directory=name_directory)
        await self.print_log(text=f'Обновление видеокадров {name_directory} завершено\n')

    @asyncSlot()
    async def start_actualizations_vk_svsu(self, name_directory: str) -> None:
        """Функция запускающая обновление видеокадров SVSU"""
        await self.print_log(f'Начало обновления видеокадров SVSU из {name_directory}')
        await actualizations_vk_svsu(print_log=self.print_log, name_directory=name_directory)
        await self.print_log(text=f'Обновление видеокадров SVSU из {name_directory} завершено\n')

    @asyncSlot()
    async def start_bloc_button(self) -> None:
        """Функция запускающая блокировку кнопок на видеокадре которые не имеют файла для вызова"""
        await self.print_log('Начало блокировки кнопок вызова видеокадров SVSU')
        await enumeration_of_svg(print_log=self.print_log)
        await self.print_log(text=f'Блокировка кнопок завершена\n')

    @asyncSlot()
    async def start_new_data_ana_bin_nary(self, name_system: str) -> None:
        """Функция запускающая обновление файлов (или их создание если не было) с базами данных сигналов"""
        await self.print_log(f'Начало обновления базы данных сигналов {name_system}')
        await new_file_data_ana_bin_nary(print_log=self.print_log, name_system=name_system)
        await self.print_log(text=f'Обновление базы данных сигналов {name_system} завершено\n')

    @asyncSlot()
    async def start_add_file_svsu_import(self, name_directory: str) -> None:
        """Функция запускающая обновление видеокадров SVSU"""
        await self.print_log(f'Начало создания файла SVSU_IMPORT.txt для {name_directory}')
        await actualizations_vk_svsu(print_log=self.print_log, name_directory=name_directory)
        await self.print_log(text=f'Создание файла SVSU_IMPORT.txt для {name_directory} завершено\n')

    @asyncSlot()
    async def print_log(self, text: str, color: str = 'black') -> None:
        """Программа выводящая переданный текст в окно лога. Цвета можно использовать зеленый - green, красный - red"""
        dict_colors = {'black': QColor(0, 0, 0),
                       'red': QColor(255, 0, 0),
                       'green': QColor(50, 155, 50)}
        self.text_log.setTextColor(dict_colors[color])
        self.text_log.append(text)
