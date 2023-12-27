from PyQt6.QtWidgets import QLabel
from modernization_objects.push_button import QPushButtonModified
from modernization_objects.q_widget import MainWindowModified
from typing import Set


class NameSystemWindow(MainWindowModified):
    def __init__(self, func, text: str, set_name_system: Set):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setting_window_size(width=400, height=200)
        self.func = func
        self.btn_maximized.setVisible(False)
        self.btn_minimized.setVisible(False)

        self.text_label = QLabel()
        self.text_label.setText(text)
        self.layout.addWidget(self.text_label)  # добавить надпись на подложку для виджетов

        if 'SVSU' in set_name_system:
            self.btn_update_data_svsu = QPushButtonModified('СВСУ', self.start_func_svsu)
            self.layout.addWidget(self.btn_update_data_svsu)  # добавить кнопку на подложку для виджетов

        if 'SVBU_1' in set_name_system:
            self.btn_update_data_svbu_1 = QPushButtonModified('СВБУ 1', self.start_func_svbu_1)
            self.layout.addWidget(self.btn_update_data_svbu_1)

        if 'SVBU_2' in set_name_system:
            self.btn_update_data_svbu_2 = QPushButtonModified('СВБУ 2', self.start_func_svbu_2)
            self.layout.addWidget(self.btn_update_data_svbu_2)

        if 'SKU_VP_1' in set_name_system:
            self.btn_update_data_sku_vp_1 = QPushButtonModified('СКУ ВП 1', self.start_func_sku_vp_1)
            self.layout.addWidget(self.btn_update_data_sku_vp_1)

        if 'SKU_VP_2' in set_name_system:
            self.btn_update_data_sku_vp_2 = QPushButtonModified('СКУ ВП 2', self.start_func_sku_vp_2)
            self.layout.addWidget(self.btn_update_data_sku_vp_2)

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
