from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont
from config.style import style_button


class QPushButtonModified(QPushButton):  # создаем класс на основе стандартного класса окна
    def __init__(self, text: str = '', func_pressed=None):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек

        font = QFont()
        font.setFamily('MS Shell Dlg 2')
        font.setPointSize(12)

        self.setMinimumHeight(50)
        self.setFont(font)
        self.setText(text)
        self.setStyleSheet(style_button)
        if func_pressed:
            self.clicked.connect(func_pressed)
