from config.general_functions import actualizations_vk
from config.func_generation_tcp_gate_file import generation_tcp_gate
from interface.window_name_system import NameSystemWindow
from interface.window_instruction import Instruction
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QTextBrowser, QHBoxLayout, QProgressBar
from qasync import asyncSlot
from modernization_objects.push_button import QPushButtonModified, QPushButtonInstruction, QPushButtonMenu
from modernization_objects.q_widget import MainWindowModified
from config.get_logger import log_info


class GenerationTcpGate(MainWindowModified):
    def __init__(self, main_menu):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setting_window_size(width=750, height=650)
        self.instruction_window = Instruction()
        self.main_menu = main_menu

        self.layout.addWidget(QPushButtonModified(text='Обновление видеокадров',
                                                  func_pressed=self.update_vis_system))

        self.layout.addWidget(QPushButtonModified(text='Создание файла ZPUPD.cfg',
                                                  func_pressed=self.tcp_gate_system))

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
                                               text='Видеокадры какой системы обновить?',
                                               set_name_system={'SVBU_1', 'SVBU_2', 'SVSU'})

        self.name_system_tcp_gate = NameSystemWindow(func=self.start_generation_tcp_gate,
                                                     text='Для какой системы создать файл ZPUPD.cfg?',
                                                     set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

    def update_vis_system(self):
        self.name_system_vk.show()

    def tcp_gate_system(self):
        self.name_system_tcp_gate.show()

    def main_menu_window(self):
        self.main_menu.show()
        self.close()

    @asyncSlot()
    async def start_generation_tcp_gate(self, name_directory: str) -> None:
        """
        Функция запускающая создание файла ZPUPD.cfg.
        :return: None
        """
        self.progress.setVisible(True)
        self.progress.reset()
        await self.print_log(text=f'Старт создания файла ZPUPD.cfg для {name_directory}')
        if await generation_tcp_gate(name_system=name_directory, print_log=self.print_log, progress=self.progress):
            await self.print_log(text='\nСоздание файла ZPUPD.cfg завершено успешно\n', color='green')
        else:
            await self.print_log(text='Создание файла ZPUPD.cfg прекращено. Устраните все недочеты и повторите\n',
                                 color='red', level='ERROR')
        self.progress.setVisible(False)

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

    @asyncSlot()
    async def start_actualizations_vk(self, name_directory: str) -> None:
        """Функция запускающая обновление видеокадров SVBU"""
        await self.print_log(text=f'Начало обновления видеокадров {name_directory}')
        self.progress.setVisible(True)
        self.progress.reset()
        await actualizations_vk(print_log=self.print_log, name_directory=name_directory, progress=self.progress)
        await self.print_log(text=f'Обновление видеокадров {name_directory} завершено\n')

    def start_instruction_window(self):
        self.instruction_window.add_text_instruction()
        self.instruction_window.show()

    def close_program(self):
        """Функция закрытия программы"""
        self.instruction_window.close()
        self.name_system_vk.close()
        self.name_system_tcp_gate.close()
        self.close()
