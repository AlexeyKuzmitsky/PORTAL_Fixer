import config.conf as conf

from os import path
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel

from typing import Set


class NameSystemWindow(QMainWindow):
    def __init__(self, func, text: str, set_name_system: Set):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setWindowTitle(f'{conf.name_program} - v.{conf.version_program}')  # изменим текст заглавия
        self.setMinimumSize(QSize(400, 200))  # Устанавливаем минимальный размер окна 400(ширина) на 700(высота)
        self.setWindowIcon(QIcon(path.join('image', 'icon.png')))

        self.name_system = ''
        self.func = func
        font = QFont()
        font.setFamily('MS Shell Dlg 2')
        font.setPointSize(12)

        layout = QVBoxLayout()

        self.text_label = QLabel()
        self.text_label.setText(text)
        self.text_label.setFont(font)
        layout.addWidget(self.text_label)  # добавить кнопку на подложку для виджетов

        if 'SVSU' in set_name_system:
            self.btn_update_data_svsu = QPushButton('СВСУ')
            self.btn_update_data_svsu.setMinimumHeight(50)
            self.btn_update_data_svsu.setFont(font)
            self.btn_update_data_svsu.clicked.connect(self.start_func_svsu)
            layout.addWidget(self.btn_update_data_svsu)  # добавить кнопку на подложку для виджетов

        if 'SVBU_1' in set_name_system:
            self.btn_update_data_svbu_1 = QPushButton('СВБУ 1')
            self.btn_update_data_svbu_1.setMinimumHeight(50)
            self.btn_update_data_svbu_1.setFont(font)
            self.btn_update_data_svbu_1.clicked.connect(self.start_func_svbu_1)
            layout.addWidget(self.btn_update_data_svbu_1)  # добавить кнопку на подложку для виджетов

        if 'SVBU_2' in set_name_system:
            self.btn_update_data_svbu_2 = QPushButton('СВБУ 2')
            self.btn_update_data_svbu_2.setMinimumHeight(50)
            self.btn_update_data_svbu_2.setFont(font)
            self.btn_update_data_svbu_2.clicked.connect(self.start_func_svbu_2)
            layout.addWidget(self.btn_update_data_svbu_2)  # добавить кнопку на подложку для виджетов

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)  # Разместим кнопку в окне

    def start_func_svbu_1(self):
        self.func('SVBU_1')
        self.close()

    def start_func_svbu_2(self):
        self.func('SVBU_2')
        self.close()

    def start_func_svsu(self):
        self.func('SVSU')
        self.close()

    def get_name_system(self):
        return self.name_system
