from config.func_checking_sources import (search_for_comments_in_a_ana_file_1, search_for_comments_in_a_bin_file_1,
                                          searching_for_comments_in_files_bin, new_start_parsing_svg_files)
from interface.window_name_system import NameSystemWindow
from interface.window_instruction import Instruction
from interface.window_table_data import TableData
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QHBoxLayout, QTextBrowser, QProgressBar, QTableView
from qasync import asyncSlot
from modernization_objects.push_button import QPushButtonModified, QPushButtonInstruction, QPushButtonMenu
from modernization_objects.q_widget import MainWindowModified
from config.get_logger import log_info


class WorkingData(MainWindowModified):
    def __init__(self, main_menu):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setting_window_size(width=750, height=650)
        self.instruction_window = Instruction()
        self.table_data = TableData(main_menu=self)
        self.main_menu = main_menu

        self.layout.addWidget(QPushButtonModified(text='Загрузить таблицу сигналов',
                                                  func_pressed=self.start_table_data_window))

        self.layout.addWidget(QPushButtonModified(text='Проверить файл ana_file-1.txt',
                                                  func_pressed=self.checking_file_ana_1_system))

        self.layout.addWidget(QPushButtonModified(text='Проверить файл bin_file-1.txt',
                                                  func_pressed=self.checking_file_bin_1_system))

        self.layout.addWidget(QPushButtonModified(text='Проверить файлы bin_file(00-13).rep',
                                                  func_pressed=self.checking_file_bin_rep_system))

        # self.data_table = QTableView()
        # self.layout.addWidget(self.data_table)  # добавить таблицу данных
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

        self.creating_file_alt_station = NameSystemWindow(
            func=self.start_creating_new_file_altstation,
            text='Для какой системы создать файл altstation?',
            set_name_system={'SVBU_1', 'SVBU_2', 'SVSU', 'SKU_VP_1', 'SKU_VP_2'}
        )

        self.checking_file_ana_1 = NameSystemWindow(func=self.start_checking_ana_file_1,
                                                    text='Файл какой системы проверить?',
                                                    set_name_system={'SVBU_1', 'SVBU_2', 'SVSU', 'SKU_VP_1', 'SKU_VP_2'}
                                                    )

        self.checking_file_bin_1 = NameSystemWindow(func=self.start_checking_bin_file_1,
                                                    text='Файл какой системы проверить?',
                                                    set_name_system={'SVBU_1', 'SVBU_2', 'SVSU', 'SKU_VP_1', 'SKU_VP_2'}
                                                    )

        self.checking_file_bin_rep = NameSystemWindow(func=self.start_checking_bin_file,
                                                      text='Файлы какой системы проверить?',
                                                      set_name_system={'SVBU_1', 'SVBU_2'})

    def creating_file_alt_station_system(self):
        self.creating_file_alt_station.show()

    def checking_file_ana_1_system(self):
        self.checking_file_ana_1.show()

    def checking_file_bin_1_system(self):
        self.checking_file_bin_1.show()

    def checking_file_bin_rep_system(self):
        self.checking_file_bin_rep.show()

    def main_menu_window(self):
        self.main_menu.show()
        self.close()

    @asyncSlot()
    async def start_creating_new_file_altstation(self, name_system: str) -> None:
        """Функция запускающая обновление файлов (или их создание если не было) с базами данных сигналов"""
        await self.print_log(f'Начало создания файла altstation {name_system}')
        self.progress.setVisible(True)
        self.progress.reset()
        await new_start_parsing_svg_files(print_log=self.print_log, name_system=name_system, progress=self.progress)
        await self.print_log(text=f'Создание файла altstation {name_system} завершено\n')

    @asyncSlot()
    async def start_checking_ana_file_1(self, name_system: str) -> None:
        """Функция запускающая проверку файла file_ana-1.txt"""
        await self.print_log(f'Начало проверки файла file_ana-1.txt {name_system}')
        self.progress.setVisible(True)
        self.progress.reset()
        await search_for_comments_in_a_ana_file_1(print_log=self.print_log, name_system=name_system,
                                                  progress=self.progress)
        await self.print_log(text=f'Поиск отсутствующих KKS в {name_system}/DbSrc/file_ana-1.txt завершен\n')

    @asyncSlot()
    async def start_checking_bin_file(self, name_system: str) -> None:
        """Функция запускающая проверку файлов c file_bin00.rep по file_bin13.rep"""
        await self.print_log(f'Начало проверки исходных файлов file_bin {name_system}')
        self.progress.setVisible(True)
        self.progress.reset()
        await searching_for_comments_in_files_bin(print_log=self.print_log, name_system=name_system,
                                                  progress=self.progress)
        await self.print_log(text=f'Поиск замечаний в {name_system}/DbSrc/file_bin завершен\n')

    @asyncSlot()
    async def start_checking_bin_file_1(self, name_system: str) -> None:
        """Функция запускающая проверку файла file_bin-1.txt"""
        await self.print_log(f'Начало проверки файла file_bin-1.txt {name_system}')
        self.progress.setVisible(True)
        self.progress.reset()
        await search_for_comments_in_a_bin_file_1(print_log=self.print_log, name_system=name_system,
                                                  progress=self.progress)
        await self.print_log(text=f'Поиск отсутствующих KKS в {name_system}/DbSrc/file_bin-1.txt завершен\n')

    @asyncSlot()
    async def print_log(self, text: str, color: str = 'white', level: str = 'INFO', a_new_line: bool = True) -> None:
        """
        Программа выводящая переданный текст в окно лога.
        Args:
            text: текст, который будет выводиться
            color: цвет текста (по умолчанию white)
            level: Уровень лога (по умолчанию INFO)
            a_new_line: Выводить с новой строки или продолжить старую (по умолчанию выводить с новой - True)
        Returns: None
        """
        dict_colors = {
            'white': QColor(169, 183, 198),
            'black': QColor(0, 0, 0),
            'red': QColor(255, 0, 0),
            'green': QColor(50, 155, 50),
            'yellow': QColor(255, 255, 0)
        }
        self.text_log.setTextColor(dict_colors[color])
        if a_new_line:
            self.text_log.append(text)
        else:
            self.text_log.textCursor().insertText(text)
        if level == 'INFO':
            log_info.info(text.replace('\n', ' '))
        elif level == 'ERROR':
            log_info.error(text.replace('\n', ' '))

    def start_instruction_window(self):
        self.instruction_window.add_text_instruction()
        self.instruction_window.show()

    def start_table_data_window(self):
        self.table_data.show()

    def close_program(self):
        """Функция закрытия программы"""
        self.instruction_window.close()
        self.creating_file_alt_station.close()
        self.checking_file_ana_1.close()
        self.checking_file_bin_1.close()
        self.checking_file_bin_rep.close()
        self.close()
