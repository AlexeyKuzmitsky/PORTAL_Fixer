from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont, QIcon, QPixmap
from os import path


class QPushButtonModified(QPushButton):  # создаем класс на основе стандартного класса кнопки
    def __init__(self, text: str = '', func_pressed=None):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек

        font = QFont()
        font.setFamily('MS Shell Dlg 2')

        self.setMinimumHeight(50)
        self.setMinimumWidth(50)
        self.setFont(font)
        self.setText(text)
        if func_pressed:
            self.clicked.connect(func_pressed)


class QPushButtonExit(QPushButton):
    def __init__(self, func_pressed=None):
        super().__init__()

        font = QFont()
        font.setFamily('MS Shell Dlg 2')
        self.setFixedWidth(40)
        self.setFixedHeight(40)
        self.setIcon(QIcon(path.join('icon', 'close_red.svg')))
        self.setFont(font)
        if func_pressed:
            self.clicked.connect(func_pressed)


class QPushButtonInstruction(QPushButton):
    def __init__(self, func_pressed=None):
        super().__init__()

        font = QFont()
        font.setFamily('MS Shell Dlg 2')
        self.setMinimumHeight(50)
        self.setMinimumWidth(50)
        self.setText('Открыть инструкцию')
        # self.setIcon(QPixmap(path.join('image', 'icon.ico')).scaled(30, 30))
        # self.setIcon(QIcon(path.join('icon', 'book.svg')))
        self.setIcon(QIcon(QPixmap(path.join('icon', 'book.svg'))))
        self.setFont(font)
        if func_pressed:
            self.clicked.connect(func_pressed)


class QPushButtonMenu(QPushButton):
    def __init__(self, func_pressed=None):
        super().__init__()

        font = QFont()
        font.setFamily('MS Shell Dlg 2')
        self.setMinimumHeight(50)
        self.setMinimumWidth(50)
        self.setText('Вернуться в главное меню')
        self.setIcon(QIcon(path.join('icon', 'home.svg')))
        self.setFont(font)
        if func_pressed:
            self.clicked.connect(func_pressed)
