import config.conf as conf

from interface.window_svsu_import import SvsuImport
from interface.window_parsing_svg import ParsingSvg
from interface.window_instruction import Instruction
from interface.window_generation_tcp_gate import GenerationTcpGate
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout
from modernization_objects.push_button import QPushButtonModified
from config.style import style_widget


class MainWindow(QMainWindow):  # создаем класс на основе стандартного класса окна
    def __init__(self):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.svsu_window = SvsuImport(main_menu=self)
        self.parsing_svg = ParsingSvg(main_menu=self)
        self.generation_tcp_gate = GenerationTcpGate(main_menu=self)

        self.instruction_window = Instruction()
        self.setWindowTitle(f'{conf.name_program} - v.{conf.version_program}')  # изменим текст заглавия
        # self.setFixedSize(QSize(400, 700))  # Фиксируем размер окна 400(ширина) на 700(высота)
        self.setMinimumSize(QSize(500, 300))  # Устанавливаем минимальный размер окна 400(ширина) на 700(высота)

        layout = QVBoxLayout()

        layout.addWidget(QPushButtonModified(text='Запуск программы создания файла SVSU_Import',
                                             func_pressed=self.start_svsu_import_window))

        layout.addWidget(QPushButtonModified(text='Запуск программы поиска замечаний на видеокадрах',
                                             func_pressed=self.start_parsing_svg_window))

        layout.addWidget(QPushButtonModified(text='Запуск программы создания файла altStation',
                                             func_pressed=self.development_warning))

        layout.addWidget(QPushButtonModified(text='Запуск программы создания новых паспортов для видеокадров',
                                             func_pressed=self.development_warning))

        layout.addWidget(QPushButtonModified(text='Запуск программы создания файлов для TcpGate',
                                             func_pressed=self.start_generation_tcp_gate_window))

        horizontal_layout = QHBoxLayout()

        horizontal_layout.addWidget(QPushButtonModified(text='Открыть инструкцию ❗',
                                                        func_pressed=self.start_instruction_window))

        horizontal_layout.addWidget(QPushButtonModified(text='Выйти из программы',
                                                        func_pressed=self.close_program))

        layout.addLayout(horizontal_layout)

        widget = QWidget()
        widget.setStyleSheet(style_widget)
        widget.setLayout(layout)
        self.setCentralWidget(widget)  # Разместим кнопку в окне

    def start_instruction_window(self):
        self.instruction_window.add_text_instruction()
        self.instruction_window.show()

    def start_svsu_import_window(self):
        self.svsu_window.show()
        self.close()

    def start_parsing_svg_window(self):
        self.parsing_svg.show()
        self.close()

    def start_generation_tcp_gate_window(self):
        self.generation_tcp_gate.show()
        self.close()

    def development_warning(self):
        QMessageBox.warning(self, 'Программа в разработке',
                            'На данный момент данная программа находится в разработке и не готова к выполнению '
                            'каких либо функций.\n'
                            'Следите за обновлениями, она скоро заработает!')

    def close_program(self):
        """Функция закрытия программы"""
        self.instruction_window.close()
        self.close()
