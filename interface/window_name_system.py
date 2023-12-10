import config.conf as conf

from PyQt6.QtGui import QFont
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel
from modernization_objects.push_button import QPushButtonModified
from typing import Set
from config.style import style_widget


class NameSystemWindow(QMainWindow):
    def __init__(self, func, text: str, set_name_system: Set):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setWindowTitle(f'{conf.name_program} - v.{conf.version_program}')  # изменим текст заглавия
        self.setMinimumSize(QSize(400, 200))  # Устанавливаем минимальный размер окна 400(ширина) на 700(высота)

        self.name_system = ''
        self.func = func
        font = QFont()
        font.setFamily('MS Shell Dlg 2')
        font.setPointSize(12)

        layout = QVBoxLayout()

        self.text_label = QLabel()
        self.text_label.setText(text)
        self.text_label.setFont(font)
        layout.addWidget(self.text_label)  # добавить надпись на подложку для виджетов

        if 'SVSU' in set_name_system:
            self.btn_update_data_svsu = QPushButtonModified('СВСУ', self.start_func_svsu)
            layout.addWidget(self.btn_update_data_svsu)  # добавить кнопку на подложку для виджетов

        if 'SVBU_1' in set_name_system:
            self.btn_update_data_svbu_1 = QPushButtonModified('СВБУ 1', self.start_func_svbu_1)
            layout.addWidget(self.btn_update_data_svbu_1)

        if 'SVBU_2' in set_name_system:
            self.btn_update_data_svbu_2 = QPushButtonModified('СВБУ 2', self.start_func_svbu_2)
            layout.addWidget(self.btn_update_data_svbu_2)

        if 'SKU_VP_1' in set_name_system:
            self.btn_update_data_sku_vp_1 = QPushButtonModified('СКУ ВП 1', self.start_func_sku_vp_1)
            layout.addWidget(self.btn_update_data_sku_vp_1)

        if 'SKU_VP_2' in set_name_system:
            self.btn_update_data_sku_vp_2 = QPushButtonModified('СКУ ВП 2', self.start_func_sku_vp_2)
            layout.addWidget(self.btn_update_data_sku_vp_2)

        widget = QWidget()
        widget.setStyleSheet(style_widget)
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

    def start_func_sku_vp_1(self):
        self.func('SKU_VP_1')
        self.close()

    def start_func_sku_vp_2(self):
        self.func('SKU_VP_2')
        self.close()
