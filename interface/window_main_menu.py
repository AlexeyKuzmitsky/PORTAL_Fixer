from interface.window_svsu_import import SvsuImport
from interface.window_parsing_svg import ParsingSvg
from interface.window_instruction import Instruction
from interface.window_generation_tcp_gate import GenerationTcpGate
# from modernization_objects.main_window import MainWindowModified
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QMessageBox, QHBoxLayout
from modernization_objects.push_button import QPushButtonModified, QPushButtonInstruction

from modernization_objects.q_widget import QWidgetModified, MainWindowModified


class MainWindow(MainWindowModified):  # создаем класс на основе стандартного класса окна
    def __init__(self):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setting_window_size(width=500, height=330)
        self.svsu_window = SvsuImport(main_menu=self)
        self.parsing_svg = ParsingSvg(main_menu=self)
        self.generation_tcp_gate = GenerationTcpGate(main_menu=self)

        self.instruction_window = Instruction()


        # layout = QVBoxLayout()

        self.layout.addWidget(QPushButtonModified(text='Запуск программы создания файла SVSU_Import',
                                             func_pressed=self.start_svsu_import_window))

        self.layout.addWidget(QPushButtonModified(text='Запуск программы поиска замечаний на видеокадрах',
                                             func_pressed=self.start_parsing_svg_window))

        self.layout.addWidget(QPushButtonModified(text='Запуск программы создания файла altStation',
                                             func_pressed=self.development_warning))

        self.layout.addWidget(QPushButtonModified(text='Запуск программы создания новых паспортов для видеокадров',
                                             func_pressed=self.development_warning))

        self.layout.addWidget(QPushButtonModified(text='Запуск программы создания файлов для TcpGate',
                                             func_pressed=self.start_generation_tcp_gate_window))

        self.layout.addWidget(QPushButtonInstruction(func_pressed=self.start_instruction_window))

        # horizontal_layout = QHBoxLayout()
        #
        # horizontal_layout.addWidget(QPushButtonInstruction(func_pressed=self.start_instruction_window))
        # horizontal_layout.addWidget(QPushButtonModified(text='Закрыть программу',
        #                                                 func_pressed=self.close_program))
        #
        # self.layout.addLayout(horizontal_layout)

        # widget = QWidget()
        # widget.setLayout(self.layout)
        self.setLayout(self.layout)
        self.layout.addStretch()
        # self.setCentralWidget(widget)  # Разместим кнопку в окне

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
