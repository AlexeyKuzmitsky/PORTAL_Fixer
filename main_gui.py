from os import path, mkdir

if not path.isdir('logs'):
    mkdir('logs')

from interface.window_main_menu import MainWindow
from qasync import QEventLoop
from config.checking_all_directories import checking_the_program_operating_environment
from PyQt6.QtWidgets import QApplication
from config.style import style_app

import config.conf as conf
import asyncio

try:
    if __name__ == '__main__':
        checking_the_program_operating_environment(directory_map=conf.program_directory_map)
        app = QApplication([])
        # app.setStyleSheet(style_app)

        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)

        windows = MainWindow()
        windows.show()
        app.exec()
except Exception as e:
    print(e)
