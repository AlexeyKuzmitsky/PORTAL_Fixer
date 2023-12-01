import sys
import time
from os import path
import interface.conf as conf

from threading import Thread
from interface.window_svsu_import import SvsuImport
from interface.window_parsing_svg import ParsingSvg
from interface.window_instruction import Instruction
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import asyncio
from qasync import QEventLoop, asyncSlot


class MainWindow(QMainWindow):  # создаем класс на основе стандартного класса окна
    def __init__(self):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.svsu_window = SvsuImport(main_menu=self)
        self.parsing_svg = ParsingSvg(main_menu=self)
        self.instruction_window = Instruction()
        self.setWindowTitle(f'{conf.name_program} - v.{conf.version_program}')  # изменим текст заглавия
        # self.setFixedSize(QSize(400, 700))  # Фиксируем размер окна 400(ширина) на 700(высота)
        self.setMinimumSize(QSize(500, 300))  # Устанавливаем минимальный размер окна 400(ширина) на 700(высота)
        self.setWindowIcon(QIcon(path.join('image', 'icon.png')))

        font = QFont()
        font.setFamily('MS Shell Dlg 2')
        font.setPointSize(12)

        layout = QVBoxLayout()

        self.btn_svsu_import_start = QPushButton('Запуск программы создания файла SVSU_Import')  # Добавим на окно виджет кнопки
        # self.btn_svsu_import_start.setMinimumSize(QSize(400, 50))
        self.btn_svsu_import_start.setMinimumHeight(50)
        self.btn_svsu_import_start.setFont(font)
        self.btn_svsu_import_start.clicked.connect(self.start_svsu_import_window)  # задать действие при нажатии
        layout.addWidget(self.btn_svsu_import_start)  # добавить кнопку на подложку для виджетов

        self.btn_parsing_svg = QPushButton('Запуск программы поиска замечаний на видеокадрах')
        self.btn_parsing_svg.setMinimumHeight(50)
        self.btn_parsing_svg.setFont(font)
        self.btn_parsing_svg.clicked.connect(self.start_parsing_svg_window)  # задать действие при нажатии
        layout.addWidget(self.btn_parsing_svg)  # добавить кнопку на подложку для виджетов

        self.btn_alt_station = QPushButton('Запуск программы создания файла altSation')
        self.btn_alt_station.setMinimumHeight(50)
        self.btn_alt_station.setFont(font)
        self.btn_alt_station.clicked.connect(self.the_button_was_clicked)  # задать действие при нажатии
        layout.addWidget(self.btn_alt_station)  # добавить кнопку на подложку для виджетов

        self.btn_new_passport = QPushButton('Запуск программы создания новых паспортов для видеокадров')
        self.btn_new_passport.setMinimumHeight(50)
        self.btn_new_passport.setFont(font)
        self.btn_new_passport.clicked.connect(self.the_button_was_clicked)  # задать действие при нажатии
        layout.addWidget(self.btn_new_passport)  # добавить кнопку на подложку для виджетов

        self.btn_tsp_gate = QPushButton('Запуск программы создания файлов для TcpGate')
        self.btn_tsp_gate.setMinimumHeight(50)
        self.btn_tsp_gate.setFont(font)
        self.btn_tsp_gate.clicked.connect(self.the_button_was_clicked)  # задать действие при нажатии
        layout.addWidget(self.btn_tsp_gate)  # добавить кнопку на подложку для виджетов

        self.btn_instruction = QPushButton('Открыть инструкцию ❗')
        self.btn_instruction.setMinimumHeight(50)
        self.btn_instruction.setFont(font)
        self.btn_instruction.clicked.connect(self.start_instruction_window)  # задать действие при нажатии
        layout.addWidget(self.btn_instruction)  # добавить кнопку на подложку для виджетов

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)  # Разместим кнопку в окне
        # self.setCentralWidget(self.button)  # Разместим кнопку в окне

    def start_instruction_window(self):
        self.instruction_window.add_text_instruction()
        self.instruction_window.show()

    def start_svsu_import_window(self):
        self.svsu_window.show()
        self.close()

    def start_parsing_svg_window(self):
        self.parsing_svg.show()
        self.close()

    def the_button_was_clicked(self):
        # new_process = Process(target=fun_text, args=())
        # new_process.start()
        new_thread = Thread(target=self.fn)
        new_thread.start()

    def fn(self):
        self.btn_svsu_import_start.setText('Кто-то на меня нажал,\n Но больше не получится!')
        self.btn_svsu_import_start.setEnabled(False)
        time.sleep(5)
        self.btn_svsu_import_start.setText('Ладно, нажимай!')
        self.btn_svsu_import_start.setEnabled(True)


try:
    if __name__ == '__main__':
        app = QApplication(sys.argv)

        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)

        windows = MainWindow()
        windows.show()
        app.exec()
except Exception as e:
    print(e)
