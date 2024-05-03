from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import QSize
from os import path


class QPushButtonModified(QPushButton):  # создаем класс на основе стандартного класса кнопки
    def __init__(self, text: str = '', func_pressed=None, path_icon=None):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек

        font = QFont()
        font.setFamily('MS Shell Dlg 2')

        self.setMinimumHeight(50)
        self.setMinimumWidth(50)
        self.setFont(font)
        self.setText(text)
        if func_pressed:
            self.clicked.connect(func_pressed)
        if path_icon:
            if path.exists(path_icon):
                icon = QIcon(path_icon)
                self.setIcon(icon)
                self.setIconSize(QSize(50, 40))


class QPushButtonExit(QPushButton):
    def __init__(self, func_pressed=None):
        super().__init__()

        self.setFixedWidth(40)
        self.setFixedHeight(40)
        if path.exists(path.join('icon', 'close_red.svg')):
            self.setIcon(QIcon(path.join('icon', 'close_red.svg')))
        else:
            font = QFont()
            font.setFamily('MS Shell Dlg 2')
            self.setFont(font)
            self.setText('X')
        if func_pressed:
            self.clicked.connect(func_pressed)


class QPushButtonMinimize(QPushButton):
    def __init__(self, func_pressed=None):
        super().__init__()

        self.setFixedWidth(40)
        self.setFixedHeight(40)
        if path.exists(path.join('icon', 'minimize.svg')):
            self.setIcon(QIcon(path.join('icon', 'minimize.svg')))
        else:
            font = QFont()
            font.setFamily('MS Shell Dlg 2')
            self.setFont(font)
            self.setText('_')
        if func_pressed:
            self.clicked.connect(func_pressed)


class QPushButtonInstruction(QPushButton):
    def __init__(self, func_pressed=None):
        super().__init__()

        font = QFont()
        font.setFamily('MS Shell Dlg 2')
        self.setMinimumHeight(50)
        self.setMinimumWidth(50)
        self.setText(' Открыть инструкцию')
        if path.exists(path.join('icon', 'book.svg')):
            icon = QIcon(path.join('icon', 'book.svg'))
            self.setIcon(icon)
            self.setIconSize(QSize(50, 40))
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
        self.setText(' Вернуться в главное меню')
        if path.exists(path.join('icon', 'home.svg')):
            icon = QIcon(path.join('icon', 'home.svg'))
            self.setIcon(icon)
            self.setIconSize(QSize(50, 40))
        self.setFont(font)
        if func_pressed:
            self.clicked.connect(func_pressed)
