from config.general_functions import sort_files_into_groups, actualizations_vk
# from config.func_parsing_svg import new_start_parsing_svg_files, dict_loading
from interface.window_name_system import NameSystemWindow
from interface.window_instruction import Instruction
from os import path, listdir
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QTextBrowser, QHBoxLayout, QProgressBar
from modernization_objects.push_button import QPushButtonModified, QPushButtonMenu, QPushButtonInstruction
from modernization_objects.q_widget import MainWindowModified
from qasync import asyncSlot
from config.get_logger import log_info
from config.func_generation_passport import program_new_passport


class GenerationPassport(MainWindowModified):
    def __init__(self, main_menu):
        super().__init__()
        self.setting_window_size(width=850, height=650)
        self.instruction_window = Instruction()
        self.main_menu = main_menu

        self.layout.addWidget(QPushButtonModified(text='Обновить видеокадры',
                                                  func_pressed=self.update_vis_svbu))
        self.layout.addWidget(QPushButtonModified(text='Создание новый паспортов для видеокадров',
                                                  func_pressed=self.start_generation_passport))
        # self.layout.addWidget(QPushButtonModified(text='Сортировка найденных замечаний',
        #                                           func_pressed=self.start_sorting_comments))

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

        self.name_system_vk = NameSystemWindow(func=self.start_actualizations_vk,
                                               text='Видеокадры какогй системы обновить?',
                                               set_name_system={'SVBU_1', 'SVBU_2', 'SKU_VP_1', 'SKU_VP_1', 'SVSU'})

        self.name_system_gen_passport = NameSystemWindow(func=self.generation_new_passport,
                                                         text='Для какой системы сгенерировать паспорта?',
                                                         set_name_system={'SVBU_1', 'SVBU_2', 'SKU_VP_1',
                                                                          'SKU_VP_2', 'SVSU'})

        # self.name_system_sorting_comments = NameSystemWindow(func=self.sorting_notes_files,
        #                                                      text='Для какой системы распределить замечания?',
        #                                                      set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        self.setLayout(self.layout)

    def update_vis_svbu(self):
        self.name_system_vk.show()

    def start_generation_passport(self):
        self.name_system_gen_passport.show()

    # def start_sorting_comments(self):
    #     self.name_system_sorting_comments.show()

    def main_menu_window(self):
        self.main_menu.show()
        self.close()

    @asyncSlot()
    async def start_actualizations_vk(self, name_directory: str) -> None:
        """Функция запускающая обновление видеокадров (name_system)/NPP_models из папки (name_system)/NPP_models_new"""
        await self.print_log(text=f'Начато обновление видеокадров {name_directory}/NPP_models '
                                  f'из папки {name_directory}/NPP_models_new')
        self.progress.setVisible(True)
        self.progress.reset()
        await actualizations_vk(print_log=self.print_log, name_directory=name_directory, progress=self.progress)
        await self.print_log(text=f'Выполнение программы обновления видеокадров {name_directory} завершено\n')
        self.information_message(title='Завершение выполнения программы',
                                 text=f'Видеокадры {name_directory} были обновлены')
        self.progress.setVisible(False)

    @asyncSlot()
    async def generation_new_passport(self, name_system: str) -> None:
        """
        Функция запускающая поиск неверных привязок на видеокадрах соответствующей системы.
        :return: None
        """
        # set_svg = set(listdir(path.join(name_directory, 'NPP_models')))
        await self.print_log(text=f'Старт создания паспортов для {name_system}')
        self.progress.setVisible(True)
        self.progress.reset()
        await program_new_passport(name_system=name_system,
                                   print_log=self.print_log,
                                   progress=self.progress)
        # if await new_start_parsing_svg_files(print_log=self.print_log, svg=set_svg, directory=name_directory,
        #                                      progress=self.progress):
        #     await self.print_log(text='Поиск замечаний завершен\n', color='green')
        #     self.information_message(title='Завершение выполнения программы',
        #                              text=f'Завершен поиск замечаний для видеокадров {name_directory}')
        # else:
        #     await self.print_log(text='Выполнение поиска замечаний прервано пользователем\n',
        #                          color='red', level='ERROR')
        #     self.information_message(title='Завершение выполнения программы',
        #                              text='Выполнение поиска замечаний прервано пользователем')
        self.progress.setVisible(False)

    # @asyncSlot()
    # async def sorting_notes_files(self, name_directory: str) -> None:
    #     """
    #     Функция запускающая распределение файлов с замечаниями согласно списку принадлежности к группе.
    #     :return: None
    #     """
    #     await self.print_log(f'Старт сортировки файлов с замечаниями {name_directory}')
    #     self.progress.setVisible(True)
    #     self.progress.reset()
    #     vis_groups = await dict_loading(print_log=self.print_log, number_bloc=name_directory)
    #     if len(vis_groups):
    #         await sort_files_into_groups(number_bloc=name_directory, group_svg=vis_groups, progress=self.progress)
    #         await self.print_log(text='\tsuccessfully', color='green', a_new_line=False)
    #         self.information_message(title='Завершение выполнения программы',
    #                                  text=f'Замечания для {name_directory} распределены по группам')
    #     else:
    #         await self.print_log(text='Распределение невозможно!\n', color='red', level='ERROR')
    #         self.information_message(title='Завершение выполнения программы',
    #                                  text='Распределение замечаний к видеокадрам невозможно')
    #     self.progress.setVisible(False)

    @asyncSlot()
    async def print_log(self, text: str, color: str = 'white', level: str = 'INFO',
                        a_new_line: bool = True) -> None:
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

    def close_program(self):
        """Функция закрытия программы"""
        self.instruction_window.close()
        self.name_system_vk.close()
        self.name_system_gen_passport.close()
        # self.name_system_sorting_comments.close()
        self.close()
