from PyQt6.QtWidgets import QLabel
from modernization_objects.push_button import QPushButtonModified
from modernization_objects.q_widget import MainWindowModified


class NameFileWindow(MainWindowModified):
    def __init__(self, func, text: str):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setting_window_size(width=400, height=200)
        self.func = func
        self.btn_maximized.setVisible(False)
        self.btn_minimized.setVisible(False)

        self.text_label = QLabel()
        self.text_label.setText(text)
        self.layout.addWidget(self.text_label)  # добавить надпись на подложку для виджетов

        self.layout.addWidget(QPushButtonModified('PLS_ANA_CONF.dmp', self.start_func_pls_ana))
        self.layout.addWidget(QPushButtonModified('PLS_BIN_CONF.dmp', self.start_func_pls_bin))

    def start_func_pls_ana(self):
        self.func('PLS_ANA_CONF.dmp')
        self.close()

    def start_func_pls_bin(self):
        self.func('PLS_BIN_CONF.dmp')
        self.close()

