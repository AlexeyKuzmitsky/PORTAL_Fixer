from PyQt6.QtWidgets import QVBoxLayout, QWidget, QTextBrowser
from os import path
from config.style import style_widget
from modernization_objects.main_window import MainWindowModified


class Instruction(MainWindowModified):
    def __init__(self):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setting_window_size(width=800, height=600)
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
