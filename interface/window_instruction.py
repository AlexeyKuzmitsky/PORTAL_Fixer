import config.conf as conf
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextBrowser
from os import path
from config.style import style_widget


class Instruction(QMainWindow):
    def __init__(self):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setWindowTitle(f'Инструкция {conf.name_program} - v.{conf.version_program}')  # изменим текст заглавия
        self.setMinimumSize(QSize(800, 600))  # Устанавливаем минимальный размер окна 400(ширина) на 700(высота)

        layout = QVBoxLayout()

        self.text_instruction = QTextBrowser()

        layout.addWidget(self.text_instruction)  # добавить QTextEdit на подложку для виджетов
        widget = QWidget()
        widget.setStyleSheet(style_widget)
        widget.setLayout(layout)
        self.setCentralWidget(widget)  # Разместим подложку в окне

    def add_text_instruction(self):
        try:
            with open(path.join('config', 'Инструкция.txt'), mode='r', encoding='windows-1251') as file_instruction:
                for i_line in file_instruction:
                    self.text_instruction.append(i_line[:-1])
        except FileNotFoundError:
            try:
                with open('Инструкция.txt', mode='r', encoding='windows-1251') as file_instruction:
                    for i_line in file_instruction:
                        self.text_instruction.append(i_line[:-1])
            except FileNotFoundError:
                self.text_instruction.append('Файла "Инструкция.txt" нет ни в папке config ни в корне')
