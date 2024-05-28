from PyQt6.QtWidgets import QWidget, QSpacerItem
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap, QPen, QColor, QPainter
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QToolBar, QFrame, QSizePolicy
from modernization_objects.push_button import QPushButtonModified, QPushButtonMinimize, QPushButtonExit
from config.style import style_window_black
from os import path

import config.conf as conf


class MainWindowModified(QWidget):
    def __init__(self):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.min_width = 500
        self.min_height = 330
        self.mPos = None
        toolbar = QToolBar()
        self.layout = QVBoxLayout()

        self.btn_minimized = QPushButtonMinimize(func_pressed=self.show_minimized)
        self.btn_maximized = QPushButtonModified(func_pressed=self.show_maximized)
        if path.exists(path.join('icon', 'maximum_size.svg')):
            self.btn_maximized.setIcon(QIcon(path.join('icon', 'maximum_size.svg')))
        else:
            self.btn_maximized.setText('□')
        self.btn_maximized.setFixedWidth(40)
        self.btn_maximized.setFixedHeight(40)

        self.btn_normal = QPushButtonModified(func_pressed=self.show_normal)
        if path.exists(path.join('icon', 'minimum_size.svg')):
            self.btn_normal.setIcon(QIcon(path.join('icon', 'minimum_size.svg')))
        else:
            self.btn_normal.setText('□')
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
        self.layout.addWidget(QFrame())
        self.setStyleSheet(style_window_black)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # отключение титула
        # self.setAttribute(Qt.WidgetAttribute.WA_TabletTracking)
        self.layout.addWidget(toolbar)
        self.setLayout(self.layout)

        self.setMouseTracking(True)  # Включаем отслеживание мыши
        self.resize_area = None
        self.arrow_type = None
        self.old_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(QColor('#43454a'), 2))
        painter.drawRect(self.rect())

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
        if event.buttons() == Qt.MouseButton.LeftButton:
            cursor_pos = event.globalPosition()
            window_rect = self.geometry()

            if cursor_pos.y() > window_rect.y() + window_rect.height() - 10:
                self.resize_area = Qt.Edge.BottomEdge
            elif cursor_pos.x() < window_rect.x() + 10:
                self.resize_area = Qt.Edge.LeftEdge
            elif cursor_pos.x() > window_rect.x() + window_rect.width() - 10:
                self.resize_area = Qt.Edge.RightEdge
            elif cursor_pos.y() < window_rect.y() + 60:
                self.resize_area = Qt.Edge.TopEdge
                self.mPos = event.pos()
            else:
                self.resize_area = None
            self.old_pos = cursor_pos

    def get_cursor_for_position(self):
        if self.arrow_type is None:
            return Qt.CursorShape.ArrowCursor
        elif self.arrow_type == Qt.Edge.BottomEdge:
            return Qt.CursorShape.SizeVerCursor
        else:
            return Qt.CursorShape.SizeHorCursor

    def mouseReleaseEvent(self, event):
        """ Мышь отпущена, удалить координаты
        :param event:
        """
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.mPos = None
        self.resize_area = None

    def check_cursor_pos(self, event) -> bool:
        cursor_pos = event.globalPosition()
        window_rect = self.geometry()

        if cursor_pos.y() > window_rect.y() + window_rect.height() - 10:
            self.arrow_type = Qt.Edge.BottomEdge
            return True
        elif cursor_pos.x() < window_rect.x() + 10:
            self.arrow_type = Qt.Edge.LeftEdge
            return True
        elif cursor_pos.x() > window_rect.x() + window_rect.width() - 10:
            self.arrow_type = Qt.Edge.RightEdge
            return True
        else:
            self.arrow_type = None
            return False

    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)  # Возврат стандартного курсора
        self.arrow_type = None

        event.accept()

    def mouseMoveEvent(self, event):
        """Отслеживание движения мыши в окне
        :param event:
        """
        if self.check_cursor_pos(event=event):
            self.setCursor(self.get_cursor_for_position())
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        # Изменение размера окна
        if self.resize_area is not None:
            self.change_to_non_full_screen_mode()
            cursor_pos = event.globalPosition()
            delta = cursor_pos - self.old_pos

            if self.resize_area == Qt.Edge.BottomEdge:
                number = round(max(self.height() + delta.y(), self.min_height))
                self.setFixedSize(self.width(), number)
            elif self.resize_area == Qt.Edge.LeftEdge:
                number = round(max(self.width() - delta.x(), self.min_width))
                if number > self.min_width:
                    self.move(self.pos().x() + round(delta.x()), self.pos().y())
                    self.setFixedSize(number, self.height())
            elif self.resize_area == Qt.Edge.RightEdge:
                number = round(max(self.width() + delta.x(), self.min_width))
                self.setFixedSize(number, self.height())
            self.old_pos = cursor_pos

        # Перемещение окна
        if self.mPos is not None:
            if self.isMaximized():
                self.show_normal()

            self.change_to_non_full_screen_mode()
            delta = event.position().toPoint() - self.mPos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )
        event.accept()

    def change_to_non_full_screen_mode(self):
        """При выходе из полноэкранного режима меняет местами кнопку режима, если она есть"""
        if self.btn_normal.isVisible():
            self.btn_normal.setVisible(False)
            self.btn_maximized.setVisible(True)

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
        self.setMinimumSize(QSize(width, height))  # Устанавливаем минимальный размер окна
        self.min_width = width
        self.min_height = height

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


class InformationWindow(QWidget):
    def __init__(self, text: str = '', message_type: str = ''):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.min_width = 500
        self.min_height = 330
        self.mPos = None
        self.message_type = message_type
        self.text_message = text

        # попытка вывести окно поверх всех остальных (не работает)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Информационное сообщение'))
        self.setting_icon()

        horizontal_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        horizontal_layout.addItem(spacer)
        horizontal_layout.addWidget(QPushButtonModified(func_pressed=self.close_program, text='Ок'))
        self.layout.addItem(horizontal_layout)
        self.setStyleSheet(style_window_black)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # отключение титула
        self.setLayout(self.layout)

        self.setMouseTracking(True)  # Включаем отслеживание мыши
        self.resize_area = None
        self.arrow_type = None
        self.old_pos = None

    def setting_icon(self):
        """Функция устанавливает иконку для всплывающего окна"""
        horizontal_layout_text_and_icon = QHBoxLayout()
        if path.exists(path.join('icon', f'{self.message_type}.svg')):
            icon_warning = QLabel()
            icon = QIcon(path.join('icon', f'{self.message_type}.svg'))
            if self.message_type == 'successfully':
                icon_warning.setPixmap(icon.pixmap(60, 60))
            else:
                icon_warning.setPixmap(icon.pixmap(100, 100))
            horizontal_layout_text_and_icon.addWidget(icon_warning)
        horizontal_layout_text_and_icon.addWidget(QLabel(self.text_message))
        self.layout.addItem(horizontal_layout_text_and_icon)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(QColor('#43454a'), 2))
        painter.drawRect(self.rect())

    def mousePressEvent(self, event):
        """ Координаты записи нажатия мышью
        :param event:
        """
        if event.buttons() == Qt.MouseButton.LeftButton:
            cursor_pos = event.globalPosition()
            window_rect = self.geometry()

            if cursor_pos.y() > window_rect.y() + window_rect.height() - 10:
                self.resize_area = Qt.Edge.BottomEdge
            elif cursor_pos.x() < window_rect.x() + 10:
                self.resize_area = Qt.Edge.LeftEdge
            elif cursor_pos.x() > window_rect.x() + window_rect.width() - 10:
                self.resize_area = Qt.Edge.RightEdge
            elif cursor_pos.y() < window_rect.y() + 60:
                self.resize_area = Qt.Edge.TopEdge
                self.mPos = event.pos()
            else:
                self.resize_area = None
            self.old_pos = cursor_pos

    def get_cursor_for_position(self):
        if self.arrow_type is None:
            return Qt.CursorShape.ArrowCursor
        elif self.arrow_type == Qt.Edge.BottomEdge:
            return Qt.CursorShape.SizeVerCursor
        else:
            return Qt.CursorShape.SizeHorCursor

    def mouseReleaseEvent(self, event):
        """ Мышь отпущена, удалить координаты
        :param event:
        """
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.mPos = None
        self.resize_area = None

    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)  # Возврат стандартного курсора
        self.arrow_type = None

        event.accept()

    def mouseMoveEvent(self, event):
        """Отслеживание движения мыши в окне
        :param event:
        """
        # Перемещение окна
        if self.mPos is not None:
            delta = event.position().toPoint() - self.mPos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )
        event.accept()

    def setting_window_size(self, width: int = 500, height: int = 330) -> None:
        """
        Функция устанавливает размер окна
        Args:
            width: Ширина окна
            height: Высота окна
        Returns: None
        """
        self.setMinimumSize(QSize(width, height))  # Устанавливаем минимальный размер окна
        self.min_width = width
        self.min_height = height

    def show_minimized(self):
        """Свернуть окно"""
        self.showMinimized()

    def close_program(self):
        """Функция закрытия программы"""
        self.close()
