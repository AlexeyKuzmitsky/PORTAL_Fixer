from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QSize, Qt, QEvent, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QColor
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QToolBar
from modernization_objects.push_button import QPushButtonModified, QPushButtonExit
from config.style import style_window, style_window_black
from os import path

import config.conf as conf


class QWidgetModified(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('test')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TabletTracking)
        print('Создан')

    def mouse_press_event(self, event):
        self.drag_pos = event.globalPosition().toPoint()
        print('1')

    def mouse_move_event(self, event):
        self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
        self.drag_pos = event.globalPosition().toPoint()
        event.accept()
        print('2')


class MainWindowModified(QWidget):
    def __init__(self):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.mPos = None
        toolbar = QToolBar()
        self.layout = QVBoxLayout()


        self.btn_minimized = QPushButtonModified(func_pressed=self.show_minimized)
        self.btn_minimized.setIcon(QIcon(path.join('icon', 'minimize.svg')))
        self.btn_minimized.setFixedWidth(40)
        self.btn_minimized.setFixedHeight(40)

        self.btn_maximized = QPushButtonModified(func_pressed=self.show_maximized)
        self.btn_maximized.setIcon(QIcon(path.join('icon', 'maximum_size.svg')))
        self.btn_maximized.setFixedWidth(40)
        self.btn_maximized.setFixedHeight(40)

        self.btn_normal = QPushButtonModified(func_pressed=self.show_normal)
        self.btn_normal.setIcon(QIcon(path.join('icon', 'minimum_size.svg')))
        self.btn_normal.setFixedWidth(40)
        self.btn_normal.setFixedHeight(40)
        self.btn_normal.setVisible(False)

        title_bar = QHBoxLayout()
        icon_program = QLabel()
        icon_program.setPixmap(QPixmap(path.join('image', 'icon.ico')).scaled(30, 30))
        title_bar.addWidget(icon_program)
        title_bar.addWidget(QLabel(f'{conf.name_program} - v.{conf.version_program}'))

        title_bar.addStretch()
        title_bar.addWidget(self.btn_minimized)
        title_bar.addWidget(self.btn_maximized)
        title_bar.addWidget(self.btn_normal)
        title_bar.addWidget(QPushButtonExit(func_pressed=self.close_program))

        self.layout.addLayout(title_bar)
        self.layout.addStretch()
        self.setStyleSheet(style_window_black)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # отключение титула
        # self.setAttribute(Qt.WidgetAttribute.WA_TabletTracking)
        self.layout.addWidget(toolbar)

    def mouseDoubleClickEvent(self, event):
        """ Дважды щелкните строку заголовка
        :param event:
        """
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()


    def mousePressEvent(self, event):
        """ Координаты записи нажатия мышью
        :param event:
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.mPos = event.pos()

    def mouseReleaseEvent(self, event):
        """ Мышь отпущена, удалить координаты
        :param event:
        """
        self.mPos = None

    def mouseMoveEvent(self, event):
        """ Мышь двигает окно
        :param event:
        """
        if self.isMaximized():
            self.show_normal()
            print(self.geometry())
            delta = event.position().toPoint() + self.mPos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )
            self.mPos = QPoint(250, 10)
            # super().mouseMoveEvent(event)
            # event.accept()
        if self.mPos is not None:
            delta = event.position().toPoint() - self.mPos

            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )
        super().mouseMoveEvent(event)
        event.accept()

    def correct_position(self):
        """Корректирует расположение окна относительно мыши"""
        self.window().move(
            self.window().x() + 1000,
            self.window().y() + 100,
        )

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
        self.btn_maximized.setVisible(False)
        self.showMaximized()
        self.btn_normal.setVisible(True)

    def show_minimized(self):
        """Свернуть окно"""
        self.showMinimized()


    def show_normal(self):
        """Возвращает окно в стандартное состояние"""
        self.btn_normal.setVisible(False)
        self.showNormal()
        self.btn_maximized.setVisible(True)

    def close_program(self):
        """Функция закрытия программы"""
        self.close()
