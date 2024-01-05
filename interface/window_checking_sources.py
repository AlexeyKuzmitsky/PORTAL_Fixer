from config.general_functions import new_file_data_ana_bin_nary
# import config.func_checking_sources
from config.func_checking_sources import search_for_comments_in_a_ana_file_1, search_for_comments_in_a_bin_file_1
from interface.window_name_system import NameSystemWindow
from interface.window_instruction import Instruction
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QHBoxLayout, QTextBrowser, QProgressBar
from qasync import asyncSlot
from modernization_objects.push_button import QPushButtonModified, QPushButtonInstruction, QPushButtonMenu
from modernization_objects.q_widget import MainWindowModified
from config.get_logger import log_info


class CheckingSources(MainWindowModified):
    def __init__(self, main_menu):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setting_window_size(width=750, height=650)
        self.instruction_window = Instruction()
        self.main_menu = main_menu

        self.layout.addWidget(QPushButtonModified(text='Обновление баз данных сигналов',
                                             func_pressed=self.update_data_system))

        self.layout.addWidget(QPushButtonModified(text='Проверить файл ana_file-1.txt',
                                             func_pressed=self.checking_file_ana_1_system))

        self.layout.addWidget(QPushButtonModified(text='Проверить файл bin_file-1.txt',
                                             func_pressed=self.checking_file_bin_1_system))

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

        self.update_data = NameSystemWindow(func=self.start_new_data_ana_bin_nary,
                                            text='Базу какой из систем обновить?',
                                            set_name_system={'SVBU_1', 'SVBU_2', 'SVSU'})

        self.checking_file_ana_1 = NameSystemWindow(func=self.start_checking_ana_file_1,
                                                    text='Файл какой системы проверить?',
                                                    set_name_system={'SVBU_1', 'SVBU_2', 'SVSU'})

        self.checking_file_bin_1 = NameSystemWindow(func=self.start_checking_ana_file_1,
                                                    text='Файл какой системы проверить?',
                                                    set_name_system={'SVBU_1', 'SVBU_2', 'SVSU'})


    def update_data_system(self):
        self.update_data.show()

    def checking_file_ana_1_system(self):
        self.checking_file_ana_1.show()

    def checking_file_bin_1_system(self):
        self.checking_file_bin_1.show()

    def main_menu_window(self):
        self.main_menu.show()
        self.close()

    @asyncSlot()
    async def start_new_data_ana_bin_nary(self, name_system: str) -> None:
        """Функция запускающая обновление файлов (или их создание если не было) с базами данных сигналов"""
        await self.print_log(f'Начало обновления базы данных сигналов {name_system}')
        self.progress.setVisible(True)
        self.progress.reset()
        await new_file_data_ana_bin_nary(print_log=self.print_log, name_system=name_system, progress=self.progress)
        await self.print_log(text=f'Обновление базы данных сигналов {name_system} завершено\n')

    @asyncSlot()
    async def start_checking_ana_file_1(self, name_system: str) -> None:
        """Функция запускающая проверку файла file_ana-1.txt"""
        await self.print_log(f'Начало проверки файла file_ana-1.txt {name_system}')
        self.progress.setVisible(True)
        self.progress.reset()
        await search_for_comments_in_a_bin_file_1(print_log=self.print_log, name_system=name_system,
                                                  progress=self.progress)
        await self.print_log(text=f'Поиск отсутствующих KKS в {name_system}/DbSrc/file_ana-1.txt завершен\n')

    @asyncSlot()
    async def start_checking_bin_file_1(self, name_system: str) -> None:
        """Функция запускающая проверку файла file_ana-1.txt"""
        await self.print_log(f'Начало проверки файла file_ana-1.txt {name_system}')
        self.progress.setVisible(True)
        self.progress.reset()
        await search_for_comments_in_a_ana_file_1(print_log=self.print_log, name_system=name_system,
                                                  progress=self.progress)
        await self.print_log(text=f'Поиск отсутствующих KKS в {name_system}/DbSrc/file_ana-1.txt завершен\n')


    @asyncSlot()
    # @log_entry
    async def print_log(self, text: str, color: str = 'white', level: str = 'INFO') -> None:
        """Программа выводящая переданный текст в окно лога. Цвета можно использовать зеленый - green, красный - red"""
        dict_colors = {
            'white': QColor(169, 183, 198),
            'black': QColor(0, 0, 0),
            'red': QColor(255, 0, 0),
            'green': QColor(50, 155, 50),
            'yellow': QColor(255, 255, 0)
        }
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
