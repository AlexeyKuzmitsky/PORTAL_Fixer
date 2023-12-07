import re
from config.general_functions import (check_directory, check_file, new_file_data_ana_bin_nary,
                                      creating_list_of_submodel,
                                      loading_data_kks_ana, loading_data_kks_bin, loading_data_kks_nary)
from config.func_svsu_import import compiling_list_of_kks, list_of_signals_on_video_frame, bloc_button
from interface.window_name_system import NameSystemWindow

import config.conf as conf
from config.point_description import AnchorPoint
from os import getcwd, path, listdir, rename, remove
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextBrowser, QMessageBox

import shutil
from typing import Set, Dict, List
from qasync import asyncSlot


class SvsuImport(QMainWindow):
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

        self.btn_update_vis_svsu = QPushButton('Обновить видеокадры SVSU из самых актуальных видеокадров SVBU')
        self.btn_update_vis_svsu.setMinimumHeight(50)
        self.btn_update_vis_svsu.setFont(font)
        self.btn_update_vis_svsu.clicked.connect(self.update_vis_svsu)
        layout.addWidget(self.btn_update_vis_svsu)  # добавить кнопку на подложку для виджетов

        self.btn_block_button_svg = QPushButton('Сделать неактивными кнопки на кадрах с несуществующими ссылками')
        self.btn_block_button_svg.setMinimumHeight(50)
        self.btn_block_button_svg.setFont(font)
        self.btn_block_button_svg.clicked.connect(self.start_bloc_button)
        layout.addWidget(self.btn_block_button_svg)  # добавить кнопку на подложку для виджетов

        self.btn_update_data_sig = QPushButton('Обновление баз данных сигналов')
        self.btn_update_data_sig.setMinimumHeight(50)
        self.btn_update_data_sig.setFont(font)
        self.btn_update_data_sig.clicked.connect(self.update_data_system)
        layout.addWidget(self.btn_update_data_sig)  # добавить кнопку на подложку для виджетов

        self.btn_add_file_svsu_import = QPushButton('Создать файл SVSU_IMPORT.txt')
        self.btn_add_file_svsu_import.setMinimumHeight(50)
        self.btn_add_file_svsu_import.setFont(font)
        self.btn_add_file_svsu_import.clicked.connect(self.update_file_svsu_import)
        layout.addWidget(self.btn_add_file_svsu_import)  # добавить кнопку на подложку для виджетов

        self.text_log = QTextBrowser()
        layout.addWidget(self.text_log)  # добавить QTextBrowser на подложку для виджетов

        self.btn_main_menu = QPushButton('Вернуться в главное меню')
        self.btn_main_menu.setMinimumHeight(50)
        self.btn_main_menu.setFont(font)
        self.btn_main_menu.clicked.connect(self.main_menu_window)  # задать действие при нажатии
        layout.addWidget(self.btn_main_menu)  # добавить кнопку на подложку для виджетов

        self.name_system_vk_svbu = NameSystemWindow(func=self.actualizations_vk_svbu,
                                                    text='Видеокадры какого блока обновить?',
                                                    set_name_system={'SVBU_1', 'SVBU_2'})
        self.name_system_vk_svsu = NameSystemWindow(func=self.actualizations_vk_svsu,
                                                    text='Видеокадры какого блока обновить?',
                                                    set_name_system={'SVBU_1', 'SVBU_2'})
        self.update_data = NameSystemWindow(func=self.start_new_data_ana_bin_nary,
                                            text='Базу какой из систем обновить?',
                                            set_name_system={'SVBU_1', 'SVBU_2', 'SVSU'})
        self.name_system_svsu_import = NameSystemWindow(func=self.start_svsu_import,
                                                        text='Для какого блока создать файл SVSU_IMPORT.txt?',
                                                        set_name_system={'SVBU_1', 'SVBU_2'})

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)  # Разместим подложку в окне

    def add_text(self):
        text = getcwd()
        self.text_log.append(f'Нажата одна их кнопок {text}')

    def update_vis_svbu(self):
        self.name_system_vk_svbu.show()

    def update_vis_svsu(self):
        self.name_system_vk_svsu.show()

    def update_data_system(self):
        self.update_data.show()

    def update_file_svsu_import(self):
        self.name_system_svsu_import.show()

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
        await self.print_log(text=f'Выполнение программы обновления видеокадров {name_directory} завершено',
                             color='green')

    @asyncSlot()
    async def actualizations_vk_svsu(self, name_directory: str) -> None:
        """Функция обновления видеокадров в папке SVSU/NPP_models из папки SVBU_(1/2)/NPP_models"""
        if name_directory == 'SVBU_1':
            number = '1'
        elif name_directory == 'SVBU_2':
            number = '2'
        else:
            return
        kks_dict_new: Dict[str, str] = {'MKA01': f'{number}0MKA01',
                                        'MKA02': f'{number}0MKA02',
                                        'MKA03': f'{number}0MKA03',
                                        'mkc': f'{number}0mkc',
                                        'ALL_STKTG': f'{number}0ALL_STKTG',
                                        'AKNP_RD2': f'{number}0AKNP_RD2'}

        renaming_kks: Dict[str, str] = {f'{number}0ALL_STKTG.svg': 'ALL_STKTG.svg',
                                        f'{number}0MKA01.svg': 'MKA01.svg',
                                        f'{number}0MKA02.svg': 'MKA02.svg',
                                        f'{number}0MKA03.svg': 'MKA03.svg',
                                        f'{number}0mkc.svg': 'mkc.svg',
                                        f'{number}0AKNP_RD2.svg': 'AKNP_RD2.svg'}

        set_vis: Set[str] = set(listdir(path.join('SVSU', 'NPP_models')))
        set_vis.discard('diag_PPD.svg')

        set_vis_bloc: Set[str] = set(listdir(path.join(name_directory, 'NPP_models')))

        num = 1
        numbers_vis = len(set_vis)
        for i_vis in sorted(set_vis):
            if i_vis == '10MKA03.svg':
                pass
            if i_vis in renaming_kks:
                # тут пойдет замена файла
                with (open(path.join(name_directory, 'NPP_models', renaming_kks[i_vis]), 'r',
                           encoding='windows-1251') as file,
                      open(path.join('SVSU', 'NPP_models', i_vis), 'w',
                           encoding='windows-1251') as new_file):
                    for i_line in file:
                        for vis in kks_dict_new:
                            if f'&quot;{vis}' in i_line:
                                result = re.split(fr'{vis}', i_line)
                                result = f'{result[0]}{kks_dict_new[vis]}{result[1]}'
                                new_file.write(result)
                                break
                        else:
                            new_file.write(i_line)
                await self.print_log(text=f'[{num}/{numbers_vis}]   +++{i_vis} видеокадр обновлен+++')

            elif i_vis in set_vis_bloc:
                # тут пойдет замена файла
                with open(path.join(name_directory, 'NPP_models', i_vis), 'r', encoding='windows-1251') as file, \
                        open(path.join('SVSU', 'NPP_models', i_vis), 'w', encoding='windows-1251') as new_file:
                    for i_line in file:
                        for vis in kks_dict_new:
                            if f'&quot;{vis}' in i_line:
                                result = re.split(fr'{vis}', i_line)
                                result = f'{result[0]}{kks_dict_new[vis]}{result[1]}'
                                new_file.write(result)
                                break
                        else:
                            new_file.write(i_line)
                await self.print_log(text=f'[{num}/{numbers_vis}]   +++{i_vis} видеокадр обновлен+++')
            else:
                await self.print_log(text=f'[{num}/{numbers_vis}]   '
                                          f'---Видеокадра {i_vis} нет в папке {name_directory}\\NPP_models---',
                                     color='red')
            num += 1
        await self.print_log(text=f'Выполнение программы обновления видеокадров SVSU из {name_directory} завершено\n',
                             color='green')

    @asyncSlot()
    async def start_bloc_button(self) -> None:
        """
        Функция берущая из папки NPP_models видеокадры и запускает функцию bloc_button в которую передает по
        оному видеокадру.
        :return: None
        """
        set_vis = set(listdir(path.join('SVSU', 'NPP_models')))
        set_kks_vis_npp_models = set()
        for i_vis in set_vis:
            if i_vis.endswith('.svg'):
                set_kks_vis_npp_models.add(i_vis[:-4])

        num = 1
        len_num = len(set_vis)
        for i_svg in sorted(set_vis):
            if i_svg.endswith('.svg'):
                await bloc_button(svg=i_svg, set_kks_name_svg=set_kks_vis_npp_models)
                await self.print_log(text=f'[{num}/{len_num}] Проверен видеокадр {i_svg}')
            else:
                await self.print_log(text=f'[{num}/{len_num}] Файл {i_svg} не является svg',
                                     color='red')
            num += 1
        await self.print_log(text=f'Выполнение программы блокировки кнопок вызова видеокадров которых нет завершено\n',
                             color='green')

    @asyncSlot()
    async def start_new_data_ana_bin_nary(self, name_system: str) -> None:
        """Функция запускающая обновление файлов (или их создание если не было) с базами данных сигналов"""
        await self.print_log(f'Начало обновления базы данных сигналов {name_system}')
        await new_file_data_ana_bin_nary(print_log=self.print_log, name_system=name_system)
        await self.print_log(text=f'Обновление базы данных сигналов {name_system} завершено\n')

    @asyncSlot()
    async def start_svsu_import(self, name_system: str) -> None:
        """Функция подготовки файла SVSU_IMPORT.txt"""
        await self.print_log(text=f'Стар программы создания файла SVSU_IMPORT.txt для {name_system}')
        check_directory(path_directory='SVSU', name_directory='NPP_models')
        list_name_svg_svsu = listdir(path.join('SVSU', 'NPP_models'))

        msg = QMessageBox.question(self, 'Сохранение старого файла SVSU_IMPORT?',
                                         'Забэкапить старый файл SVSU_IMPORT?\n'
                                         '(файл SVSU_IMPORT.txt будет переименован в SVSU_IMPORT_bck.txt)')

        if msg == QMessageBox.StandardButton.Yes:
            await self.renaming_old_file_svsu_import(name_system=name_system)

        if not await self.check_all_files(name_system=name_system):
            return

        data_ana = await loading_data_kks_ana(directory=name_system)
        data_bin = await loading_data_kks_bin(directory=name_system)
        data_nary = await loading_data_kks_nary(directory=name_system)

        set_ana_signal: Set[str] = set()
        set_bin_signal: Set[str] = set()
        set_nary_signal: Set[str] = set()

        num = 1
        number_name_svg = len(list_name_svg_svsu)
        for name_svg in list_name_svg_svsu:
            if name_svg.endswith('.svg'):
                list_submodel: List[AnchorPoint] = await creating_list_of_submodel(name_system=name_system,
                                                                                   name_svg=name_svg)
                await compiling_list_of_kks(list_submodel=list_submodel,
                                            data_ana=data_ana, data_bin=data_bin, data_nary=data_nary)

                set_ana, set_bin, set_nary = await list_of_signals_on_video_frame(list_submodel=list_submodel)

                await self.print_log(text=f'[{num: <4}/{number_name_svg: <4}] Проверка {name_svg: <25}\t\t'
                                          f'Найдено KKS: ANA - {len(set_ana): <4}, BIN - {len(set_bin): <4}, '
                                          f'NARY - {len(set_nary): <4}')

                set_ana_signal.update(set_ana)
                set_bin_signal.update(set_bin)
                set_nary_signal.update(set_nary)
            else:
                await self.print_log(text=f'[{num: <4}/{number_name_svg: <4}] Файл {name_svg} не является svg',
                                     color='red')
            num += 1

        await self.writing_signals_to_a_file(name_system=name_system,
                                             set_ana_signal=set_ana_signal,
                                             set_bin_signal=set_bin_signal,
                                             set_nary_signal=set_nary_signal)
        if check_file(path_directory=name_system, name_file='SVSU_IMPORT_bck.txt'):
            msg = QMessageBox.question(self, 'Вывод внесенных изменений',
                                       'Произвести сравнение старого файла SVSU_IMPORT с новым?')

            if msg == QMessageBox.StandardButton.Yes:
                await self.file_svsu_import_comparison(name_system=name_system)

        await self.print_log(text=f'Выполнение программы создания файла SVSU_IMPORT.txt завершено', color='green')

    async def file_svsu_import_comparison(self, name_system: str):
        """Функция сравнения двух файлов SVSU_IMPORT.txt и SVSU_IMPORT_bck.txt и вывода отчета"""
        list_kks_svsu_import: Set[str] = set()
        list_kks_svsu_import_bck: Set[str] = set()
        with open(path.join(name_system, 'SVSU_IMPORT.txt'), encoding='UTF-8') as file_svsu:
            for i_line in file_svsu:
                list_kks_svsu_import.add(i_line[:-1])
        with open(path.join(name_system, 'SVSU_IMPORT_bck.txt'), encoding='UTF-8') as file_svsu_bck:
            for i_line in file_svsu_bck:
                list_kks_svsu_import_bck.add(i_line[:-1])

        del_kks = list_kks_svsu_import_bck.difference(list_kks_svsu_import)
        add_kks = list_kks_svsu_import.difference(list_kks_svsu_import_bck)

        await self.print_log(text=f'Удалены KKS в новом ({len(del_kks)} шт.):', color='red')
        num = 1
        for i_kks in sorted(del_kks):
            await self.print_log(text=f'{num}. {i_kks}', color='red')
            num += 1
        await self.print_log(text='')

        await self.print_log(text=f'Добавлены KKS в новом ({len(add_kks)} шт.):', color='green')
        num = 1
        for i_kks in sorted(add_kks):
            await self.print_log(text=f'{num}. {i_kks}', color='green')
            num += 1
        await self.print_log(text='')

    async def writing_signals_to_a_file(self, name_system: str,
                                        set_ana_signal: Set[str],
                                        set_bin_signal: Set[str],
                                        set_nary_signal: Set[str]):
        """Функция записывающая в файл SVSU_import.txt найденные сигналы"""
        with open(path.join(name_system, 'SVSU_IMPORT.txt'), 'w', encoding='utf-8') as file_import:
            file_import.write('signum\ttype\tfunction\tcycle\n')
            await self.print_log(text=f'KKS записано в файл SVSU_IMPORT.txt:')

            for i_kks in sorted(set_ana_signal):
                file_import.write(f'\tA\t{i_kks}\t\n')
            await self.print_log(text=f'ANA - {len(set_ana_signal)}')

            for i_kks in sorted(set_bin_signal):
                file_import.write(f'\tB\t{i_kks}\t\n')
            await self.print_log(text=f'BIN - {len(set_bin_signal)}')

            for i_kks in sorted(set_nary_signal):
                file_import.write(f'\tN\t{i_kks}\t\n')
            await self.print_log(text=f'NARY - {len(set_nary_signal)}')

    async def check_all_files(self, name_system: str):
        """Функция проверяет наличие всех файлов (ANA_list_kks.txt, BIN_list_kks.txt, NARY_list_kks.txt)
         для работы программы по созданию файла SVSU_IMPORT.txt"""

        if not check_file(path_directory=path.join(name_system, 'data'), name_file='ANA_list_kks.txt'):
            msg = QMessageBox.question(self, 'Нет файла ANA_list_kks.txt',
                                       f'Не найден файл {name_system}/data/ANA_list_kks.txt\n '
                                       f'Для создания файла ANA_list_kks.txt выберите пункт "Обновление базы данных"'
                                       f' и систему {name_system}.\n'
                                       f'Продолжить выполнение программы без файла ANA_list_kks.txt?')

            if msg == QMessageBox.StandardButton.No:
                await self.print_log(text=f'Программа создания файла SVSU_IMPORT.txt прервана пользователем\n',
                                     color='red')
                return False

        if not check_file(path_directory=path.join(name_system, 'data'), name_file='BIN_list_kks.txt'):
            msg = QMessageBox.question(self, 'Нет файла BIN_list_kks.txt',
                                       f'Не найден файл {name_system}/data/BIN_list_kks.txt\n '
                                       f'Для создания файла BIN_list_kks.txt выберите пункт "Обновление базы данных"'
                                       f' и систему {name_system}.\n'
                                       f'Продолжить выполнение программы без файла BIN_list_kks.txt?')

            if msg == QMessageBox.StandardButton.No:
                await self.print_log(text=f'Программа создания файла SVSU_IMPORT.txt прервана пользователем\n',
                                     color='red')
                return False

        if not check_file(path_directory=path.join(name_system, 'data'), name_file='NARY_list_kks.txt'):
            msg = QMessageBox.question(self, 'Нет файла NARY_list_kks.txt',
                                       f'Не найден файл {name_system}/data/NARY_list_kks.txt\n '
                                       f'Для создания файла NARY_list_kks.txt выберите пункт "Обновление базы данных"'
                                       f' и систему {name_system}.\n'
                                       f'Продолжить выполнение программы без файла NARY_list_kks.txt?')

            if msg == QMessageBox.StandardButton.No:
                await self.print_log(text=f'Программа создания файла SVSU_IMPORT.txt прервана пользователем\n',
                                     color='red')
                return False
        return True

    async def renaming_old_file_svsu_import(self, name_system: str):
        """Функция переименовывает файл SVSU_IMPORT.txt в SVSU_IMPORT_bck.txt"""
        if check_file(path_directory=name_system, name_file='SVSU_IMPORT.txt'):
            if check_file(path_directory=name_system, name_file='SVSU_IMPORT_bck.txt'):
                remove(path.join(name_system, 'SVSU_IMPORT_bck.txt'))
            rename(path.join(name_system, 'SVSU_IMPORT.txt'), path.join(name_system, 'SVSU_IMPORT_bck.txt'))
            await self.print_log(text=f'Файл {name_system}/SVSU_IMPORT.txt переименован в '
                                      f'{name_system}/SVSU_IMPORT_bck.txt', color='green')
        else:
            await self.print_log(text=f'Файл {name_system}/SVSU_IMPORT.txt не найден', color='red')

    @asyncSlot()
    async def print_log(self, text: str, color: str = 'black') -> None:
        """Программа выводящая переданный текст в окно лога. Цвета можно использовать зеленый - green, красный - red"""
        dict_colors = {'black': QColor(0, 0, 0),
                       'red': QColor(255, 0, 0),
                       'green': QColor(50, 155, 50)}
        self.text_log.setTextColor(dict_colors[color])
        self.text_log.append(text)
