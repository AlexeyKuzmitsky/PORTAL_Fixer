from config.point_description import AnchorPoint
from config.general_functions import (sort_files_into_groups, new_file_data_ana_bin_nary,
                                      loading_data_kks_ana, loading_data_kks_bin, loading_data_kks_nary,
                                      loading_data_dict_kks_ana, loading_data_dict_kks_bin, creating_list_of_submodel)

from config.func_parsing_svg import checking_kks_and_preparing_comment, recording_comments_to_a_file
from interface.window_name_system import NameSystemWindow
import json

import config.conf as conf
from os import path, listdir
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextBrowser

import shutil
from typing import Set, Dict, List
from qasync import asyncSlot


class ParsingSvg(QMainWindow):
    def __init__(self, main_menu):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setWindowTitle(f'{conf.name_program} - v.{conf.version_program}')  # изменим текст заглавия
        self.setMinimumSize(QSize(750, 350))  # Устанавливаем минимальный размер окна 750(ширина) на 350(высота)
        self.setWindowIcon(QIcon(path.join('image', 'icon.png')))

        self.main_menu = main_menu
        font = QFont()
        font.setFamily('MS Shell Dlg 2')
        font.setPointSize(12)

        layout = QVBoxLayout()

        self.btn_update_vis_svbu = QPushButton('Обновить видеокадры SVBU')
        self.btn_update_vis_svbu.setMinimumHeight(50)
        self.btn_update_vis_svbu.setFont(font)
        self.btn_update_vis_svbu.clicked.connect(self.update_vis_svbu)
        layout.addWidget(self.btn_update_vis_svbu)  # добавить кнопку на подложку для виджетов

        self.btn_update_data_sig = QPushButton('Обновление баз данных сигналов')
        self.btn_update_data_sig.setMinimumHeight(50)
        self.btn_update_data_sig.setFont(font)
        self.btn_update_data_sig.clicked.connect(self.update_data_system)
        layout.addWidget(self.btn_update_data_sig)  # добавить кнопку на подложку для виджетов

        self.btn_parsing_svg = QPushButton('Поиск замечаний на видеокадрах')
        self.btn_parsing_svg.setMinimumHeight(50)
        self.btn_parsing_svg.setFont(font)
        self.btn_parsing_svg.clicked.connect(self.start_parsing_svg)
        layout.addWidget(self.btn_parsing_svg)  # добавить кнопку на подложку для виджетов

        self.btn_sorting_comments = QPushButton('Сортировка найденных замечаний')
        self.btn_sorting_comments.setMinimumHeight(50)
        self.btn_sorting_comments.setFont(font)
        self.btn_sorting_comments.clicked.connect(self.start_sorting_comments)
        layout.addWidget(self.btn_sorting_comments)  # добавить кнопку на подложку для виджетов

        self.text_log = QTextBrowser()
        layout.addWidget(self.text_log)  # добавить QTextBrowser на подложку для виджетов

        self.btn_main_menu = QPushButton('Вернуться в главное меню')
        self.btn_main_menu.setMinimumHeight(50)
        self.btn_main_menu.setFont(font)
        self.btn_main_menu.clicked.connect(self.main_menu_window)  # задать действие при нажатии
        layout.addWidget(self.btn_main_menu)  # добавить кнопку на подложку для виджетов

        self.name_system_vk = NameSystemWindow(func=self.actualizations_vk_svbu,
                                               text='Видеокадры какого блока обновить?',
                                               set_name_system={'SVBU_1', 'SVBU_2'})

        self.update_data = NameSystemWindow(func=self.start_new_data_ana_bin_nary,
                                            text='Базу какой из систем обновить?',
                                            set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        self.name_system_parsing_svg = NameSystemWindow(func=self.checking_svg_files,
                                                        text='На каких видеокадрах найти замечания?',
                                                        set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        self.name_system_sorting_comments = NameSystemWindow(func=self.sorting_notes_files,
                                                             text='Для какой системы распределить замечания?',
                                                             set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)  # Разместим подложку в окне

    def update_vis_svbu(self):
        self.name_system_vk.show()

    def update_data_system(self):
        self.update_data.show()

    def start_parsing_svg(self):
        self.name_system_parsing_svg.show()

    def start_sorting_comments(self):
        self.name_system_sorting_comments.show()

    def main_menu_window(self):
        self.main_menu.show()
        self.close()

    @asyncSlot()
    async def actualizations_vk_svbu(self, name_directory: str) -> None:
        """Функция обновления видеокадров в папке SVBU_(1/2)/NPP_models из папки SVBU_(1/2)/NPP_models_new"""
        set_vis: Set[str] = set(listdir(path.join(name_directory, 'NPP_models')))
        set_vis_new: Set[str] = set(listdir(path.join(name_directory, 'NPP_models_new')))
        numbers_vis = len(set_vis)
        number = 1
        for i_vis in sorted(set_vis):
            if i_vis in set_vis_new:
                shutil.copy2(path.join(name_directory, 'NPP_models_new', i_vis),
                             path.join(name_directory, 'NPP_models', i_vis))
                await self.print_log(text=f'[{number}/{numbers_vis}]   +++{i_vis} видеокадр обновлен+++')
            else:
                await self.print_log(text=f'[{number}/{numbers_vis}]   '
                                          f'---Видеокадра {i_vis} нет в {name_directory}/NPP_models_new ---',
                                     color='red')
            number += 1
        await self.print_log(text=f'Выполнение программы обновления видеокадров {name_directory} завершено\n',
                             color='green')

    @asyncSlot()
    async def start_new_data_ana_bin_nary(self, name_system: str) -> None:
        """Функция запускающая обновление файлов (или их создание если не было) с базами данных сигналов"""
        await self.print_log(f'Начало обновления базы данных сигналов {name_system}')
        await new_file_data_ana_bin_nary(print_log=self.print_log, name_system=name_system)
        await self.print_log(text=f'Обновление базы данных сигналов {name_system} завершено\n')

    @asyncSlot()
    async def checking_svg_files(self, name_directory: str) -> None:
        """
        Функция запускающая поиск неверных привязок на видеокадрах соответствующей системы.
        :return: None
        """
        set_svg = set(listdir(path.join(name_directory, 'NPP_models')))
        await self.print_log(text=f'Старт проверки видеокадров {name_directory}')
        await self.new_start_parsing_svg_files(svg=set_svg, directory=name_directory)
        await self.print_log(text='Поиск замечаний завершен\n', color='green')

    async def new_start_parsing_svg_files(self, svg: Set[str], directory: str) -> None:
        """
        Функция производит поиск всех подмоделей на видеокадрах после чего находит на подмоделях привязки (KKS).
        Проверяет наличие KKS в действующей базе и если не находит, подготавливает запись в файл замечаний.
        :param svg: Список svg-файлов
        :param directory: Название системы в которой ведется поиск замечаний
        :return: None
        """
        set_kks_ana_data = await loading_data_kks_ana(directory=directory)
        set_kks_bin_data = await loading_data_kks_bin(directory=directory)
        set_kks_nary_data = await loading_data_kks_nary(directory=directory)
        dict_kks_ana_data = await loading_data_dict_kks_ana(directory=directory)
        dict_kks_bin_data = await loading_data_dict_kks_bin(directory=directory)

        numbers = len(svg)
        number = 1
        for i_svg in sorted(svg):
            text_log = f'[{number}/{numbers}]\t Проверка {i_svg}'
            if i_svg.endswith('.svg') or i_svg.endswith('.SVG'):
                list_submodel: List[AnchorPoint] = await creating_list_of_submodel(name_system=directory,
                                                                                   name_svg=i_svg)
                dict_errors: Dict[str, str] = dict()

                for i_submodel in list_submodel:
                    dict_errors.update(i_submodel.check_error_kks_database(data_ana=set_kks_ana_data,
                                                                           data_bin=set_kks_bin_data,
                                                                           data_nary=set_kks_nary_data))

                list_error_kks: Set = set()  # список записей о замечаниях
                for i_kks in dict_errors:
                    await checking_kks_and_preparing_comment(kks_signal=i_kks,
                                                             list_error_kks=list_error_kks,
                                                             name_submodel=dict_errors[i_kks],
                                                             set_svg=svg,
                                                             set_kks_ana_data=set_kks_ana_data,
                                                             set_kks_bin_data=set_kks_bin_data,
                                                             set_kks_nary_data=set_kks_nary_data,
                                                             dict_kks_ana_data=dict_kks_ana_data,
                                                             dict_kks_bin_data=dict_kks_bin_data)

                if len(list_error_kks):
                    recording_comments_to_a_file(directory=directory,
                                                 list_error_kks=list_error_kks,
                                                 name_file=i_svg[:-4])
                text_log = f'{text_log:<55}Кривых KKS: {len(list_error_kks)}'
                await self.print_log(text=text_log)
            else:
                text_log = f'{text_log:<55}Файл {i_svg} не svg!'
                await self.print_log(text=text_log, color='red')
            number += 1

    @asyncSlot()
    async def sorting_notes_files(self, name_directory: str) -> None:
        """
        Функция запускающая распределение файлов с замечаниями согласно списку принадлежности к группе.
        :return: None
        """
        if name_directory != '0':
            await self.print_log(f'Старт распределения файлов с замечаниями {name_directory} '
                                 f'согласно списку принадлежности к группе')
            vis_groups = await self.dict_loading(number_bloc=name_directory)

            if len(vis_groups):
                await sort_files_into_groups(number_bloc=name_directory, group_svg=vis_groups)
                await self.print_log(text='Распределено успешно!\n', color='green')
            else:
                await self.print_log(text='Распределение невозможно!\n', color='red')

    @asyncSlot()
    async def dict_loading(self, number_bloc: str) -> Dict:
        """
        Функция принимает номер блока и в соответствующей папке находит json файл в котором распределены видеокадры
        по группам.
        :param number_bloc: Номер блока.
        :return: Словарь, содержащий словарь с названием группы(ключ) и списком видеокадров относящихся к группе.
        """
        path_vis = path.join(number_bloc, 'data', 'kks_vis_groups.json')
        try:
            with open(path_vis, 'r', encoding='UTF-8') as file_json:
                data = json.load(file_json)
                return data
        except FileNotFoundError:
            await self.print_log(f'Нет файла "kks_vis_groups.json" в папке {path.join(number_bloc, "data")}')
            return {}

    @asyncSlot()
    async def print_log(self, text: str, color: str = 'black') -> None:
        """Программа выводящая переданный текст в окно лога. Цвета можно использовать зеленый - green, красный - red"""
        dict_colors = {'black': QColor(0, 0, 0),
                       'red': QColor(255, 0, 0),
                       'green': QColor(50, 155, 50)}
        self.text_log.setTextColor(dict_colors[color])
        self.text_log.append(text)
