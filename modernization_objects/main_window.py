from PyQt6.QtWidgets import QMainWindow
from os import path
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from config.style import style_window
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from modernization_objects.push_button import QPushButtonModified

import config.conf as conf


class MainWindowModified(QMainWindow):  # создаем класс на основе стандартного класса окна
    def __init__(self):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setWindowTitle(f'{conf.name_program} - v.{conf.version_program}')  # изменим текст заглавия
        if path.isfile(path.join('image', 'icon.ico')):
            self.setWindowIcon(QIcon(path.join('image', 'icon.ico')))
        self.setStyleSheet(style_window)
        self.initial_pos = None

        self.layout = QVBoxLayout()
        title_bar = QHBoxLayout()
        title_bar.addWidget(QLabel(f'{conf.name_program} - v.{conf.version_program}'))
        title_bar.addWidget(QPushButtonModified(text='_', func_pressed=self.showMinimized))
        title_bar.addWidget(QPushButtonModified(text='□', func_pressed=self.showMaximized))

        title_bar.addWidget(QPushButtonModified(text='X', func_pressed=self.close_program))

        self.layout.addLayout(title_bar)

    def setting_window_size(self, width: int = 500, height: int = 330) -> None:
        """
        Функция устанавливает размер окна
        Args:
            width: Ширина окна
            height: Высота окна
        Returns: None
        """
        self.setMinimumSize(QSize(width, height))  # Устанавливаем минимальный размер окна 400(ширина) на 700(высота)

    def show_maximized(self):
        """Развернуть окно на весь экран"""
        self.showMaximized()

    def show_minimized(self):
        """Свернуть окно"""
        self.showMinimized()

    def close_program(self):
        """Функция закрытия программы"""
        self.close()
