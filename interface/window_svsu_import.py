from config.general_functions import new_file_data_ana_bin_nary
from config.func_svsu_import import (enumeration_of_svg, actualizations_vk_svbu, actualizations_vk_svsu,
                                     add_file_svsu_import)
from interface.window_name_system import NameSystemWindow
from interface.window_instruction import Instruction
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QHBoxLayout, QTextBrowser, QProgressBar
from qasync import asyncSlot
from modernization_objects.push_button import QPushButtonModified, QPushButtonInstruction, QPushButtonMenu
from modernization_objects.q_widget import MainWindowModified
from config.get_logger import log_info


class SvsuImport(MainWindowModified):
    def __init__(self, main_menu):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setting_window_size(width=750, height=650)
        self.instruction_window = Instruction()
        self.main_menu = main_menu

        self.layout.addWidget(QPushButtonModified(text='Обновить видеокадры SVBU',
                                             func_pressed=self.update_vis_svbu))

        self.layout.addWidget(QPushButtonModified(text='Обновить видеокадры SVSU из самых актуальных видеокадров SVBU',
                                             func_pressed=self.update_vis_svsu))

        self.layout.addWidget(QPushButtonModified(text='Сделать неактивными кнопки на кадрах с несуществующими ссылками',
                                             func_pressed=self.start_bloc_button))

        self.layout.addWidget(QPushButtonModified(text='Обновление баз данных сигналов',
                                             func_pressed=self.update_data_system))

        self.layout.addWidget(QPushButtonModified(text='Создать файл SVSU_IMPORT.txt',
                                             func_pressed=self.update_file_svsu_import))

        self.text_log = QTextBrowser()
        self.layout.addWidget(self.text_log)  # добавить QTextBrowser на подложку для виджетов

        self.progress = QProgressBar()
        self.progress.setStyleSheet('text-align: center;')
        self.layout.addWidget(self.progress)
        self.progress.setVisible(False)

        horizontal_layout = QHBoxLayout()

        horizontal_layout.addWidget(QPushButtonMenu(func_pressed=self.main_menu_window))
        horizontal_layout.addWidget(QPushButtonInstruction(func_pressed=self.start_instruction_window))

        self.layout.addLayout(horizontal_layout)

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
        await self.print_log(text=f'Начало обновления видеокадров {name_directory}')
        self.progress.setVisible(True)
        self.progress.reset()
        await actualizations_vk_svbu(print_log=self.print_log, name_directory=name_directory, progress=self.progress)
        await self.print_log(text=f'Обновление видеокадров {name_directory} завершено\n')

    @asyncSlot()
    async def start_actualizations_vk_svsu(self, name_directory: str) -> None:
        """Функция запускающая обновление видеокадров SVSU"""
        await self.print_log(f'Начало обновления видеокадров SVSU из {name_directory}')
        self.progress.setVisible(True)
        self.progress.reset()
        await actualizations_vk_svsu(print_log=self.print_log, name_directory=name_directory, progress=self.progress)
        await self.print_log(text=f'Обновление видеокадров SVSU из {name_directory} завершено\n')

    @asyncSlot()
    async def start_bloc_button(self) -> None:
        """Функция запускающая блокировку кнопок на видеокадре которые не имеют файла для вызова"""
        await self.print_log('Начало блокировки кнопок вызова видеокадров SVSU')
        self.progress.setVisible(True)
        self.progress.reset()
        await enumeration_of_svg(print_log=self.print_log, progress=self.progress)
        await self.print_log(text=f'Блокировка кнопок завершена\n')

    @asyncSlot()
    async def start_new_data_ana_bin_nary(self, name_system: str) -> None:
        """Функция запускающая обновление файлов (или их создание если не было) с базами данных сигналов"""
        await self.print_log(f'Начало обновления базы данных сигналов {name_system}')
        self.progress.setVisible(True)
        self.progress.reset()
        await new_file_data_ana_bin_nary(print_log=self.print_log, name_system=name_system, progress=self.progress)
        await self.print_log(text=f'Обновление базы данных сигналов {name_system} завершено\n')

    @asyncSlot()
    async def start_add_file_svsu_import(self, name_directory: str) -> None:
        """Функция запускающая создание файла SVSU_IMPORT.txt"""
        await self.print_log(f'Начало создания файла SVSU_IMPORT.txt для {name_directory}')
        self.progress.setVisible(True)
        self.progress.reset()
        await add_file_svsu_import(print_log=self.print_log, name_system=name_directory, progress=self.progress)
        await self.print_log(text=f'Создание файла SVSU_IMPORT.txt для {name_directory} завершено\n')

    @asyncSlot()
    # @log_entry
    async def print_log(self, text: str, color: str = 'white', level: str = 'INFO') -> None:
        """Программа выводящая переданный текст в окно лога. Цвета можно использовать зеленый - green, красный - red"""
        dict_colors = {
            'white': QColor(169, 183, 198),
            'black': QColor(0, 0, 0),
            'red': QColor(255, 0, 0),
            'green': QColor(50, 155, 50)}
        self.text_log.setTextColor(dict_colors[color])
        self.text_log.append(text)
        if level == 'INFO':
            log_info.info(text.replace('\n', ' '))
        elif level == 'ERROR':
            log_info.error(text.replace('\n', ' '))

    def start_instruction_window(self):
        self.instruction_window.add_text_instruction()
        self.instruction_window.show()

    def close_program(self):
        """Функция закрытия программы"""
        self.instruction_window.close()
        self.close()
