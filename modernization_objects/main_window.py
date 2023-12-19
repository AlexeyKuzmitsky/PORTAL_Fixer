from PyQt6.QtWidgets import QMainWindow
from os import path
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

import config.conf as conf


class MainWindowModified(QMainWindow):  # создаем класс на основе стандартного класса окна
    def __init__(self):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setWindowTitle(f'{conf.name_program} - v.{conf.version_program}')  # изменим текст заглавия
        if path.isfile(path.join('image', 'icon.ico')):
            self.setWindowIcon(QIcon(path.join('image', 'icon.ico')))

    def setting_window_size(self, width: int = 500, height: int = 330) -> None:
        """
        Функция устанавливает размер окна
        Args:
            width: Ширина окна
            height: Высота окна
        Returns: None
        """
        self.setMinimumSize(QSize(width, height))  # Устанавливаем минимальный размер окна 400(ширина) на 700(высота)