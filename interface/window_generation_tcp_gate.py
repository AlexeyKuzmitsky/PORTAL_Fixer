from config.general_functions import new_file_data_ana_bin_nary
from config.func_generation_tcp_gate_file import generation_tcp_gate, add_data_file_bin_nary
from interface.window_name_system import NameSystemWindow
from interface.window_instruction import Instruction
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QTextBrowser, QHBoxLayout, QProgressBar
from config.style import style_widget, style_text_browser
from qasync import asyncSlot
from modernization_objects.push_button import QPushButtonModified
from modernization_objects.main_window import MainWindowModified
from config.get_logger import log_info


class GenerationTcpGate(MainWindowModified):
    def __init__(self, main_menu):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setting_window_size(width=750, height=650)
        self.instruction_window = Instruction()
        self.main_menu = main_menu

        layout = QVBoxLayout()
        layout.addWidget(QPushButtonModified(text='Обновление баз данных сигналов',
                                             func_pressed=self.update_data_system))
        layout.addWidget(QPushButtonModified(text='Создание файла ZPUPD.cfg',
                                             func_pressed=self.tcp_gate_system))

        self.text_log = QTextBrowser()
        self.text_log.setStyleSheet(style_text_browser)
        layout.addWidget(self.text_log)  # добавить QTextBrowser на подложку для виджетов

        self.progress = QProgressBar()
        self.progress.setStyleSheet('text-align: center;')
        layout.addWidget(self.progress)
        self.progress.setVisible(False)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(QPushButtonModified(text='⏪ Вернуться в главное меню',
                                                        func_pressed=self.main_menu_window))
        horizontal_layout.addWidget(QPushButtonModified(text='Открыть инструкцию ❗',
                                                        func_pressed=self.start_instruction_window))
        horizontal_layout.addWidget(QPushButtonModified(text='Закрыть программу',
                                                        func_pressed=self.close_program))

        layout.addLayout(horizontal_layout)

        self.update_data = NameSystemWindow(func=self.start_new_data_ana_bin_nary,
                                            text='Базу какой из систем обновить?',
                                            set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        self.name_system_tcp_gate = NameSystemWindow(func=self.start_generation_tcp_gate,
                                                     text='Для какой системы создать файл ZPUPD.cfg?',
                                                     set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        widget = QWidget()
        widget.setLayout(layout)
        widget.setStyleSheet(style_widget)
        self.setCentralWidget(widget)  # Разместим подложку в окне

    def update_data_system(self):
        self.update_data.show()

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
        await self.print_log(text=f'Старт создания файла ZPUPD.cfg для {name_directory}')
        if await generation_tcp_gate(name_system=name_directory, print_log=self.print_log):
            await self.print_log(text='\nСоздание файла ZPUPD.cfg завершено успешно\n', color='green')
        else:
            await self.print_log(text='Создание файла ZPUPD.cfg прекращено. Устраните все недочеты и повторите\n',
                                 color='red', level='ERROR')
        self.progress.setVisible(False)

    @asyncSlot()
    async def start_new_data_ana_bin_nary(self, name_system: str) -> None:
        """Функция запускающая обновление файлов (или их создание если не было) с базами данных сигналов"""
        await self.print_log(f'Начало обновления базы данных сигналов {name_system}')
        self.progress.setVisible(True)
        self.progress.reset()
        await new_file_data_ana_bin_nary(print_log=self.print_log, name_system=name_system, progress=self.progress,
                                         min_progress=0, max_progress=50)
        await add_data_file_bin_nary(print_log=self.print_log, name_system=name_system, progress=self.progress,
                                     min_progress=50, max_progress=100)
        await self.print_log(text=f'Обновление базы данных сигналов {name_system} завершено\n')
        self.progress.setVisible(False)

    @asyncSlot()
    async def print_log(self, text: str, color: str = 'black', level: str = 'INFO') -> None:
        """Программа выводящая переданный текст в окно лога. Цвета можно использовать зеленый - green, красный - red"""
        dict_colors = {'black': QColor(0, 0, 0),
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
