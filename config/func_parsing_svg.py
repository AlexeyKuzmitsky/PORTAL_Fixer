import re
import json
import shutil

from os import path, listdir
from typing import Set, Dict, List
from math import ceil
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QProgressBar
from config.point_description import AnchorPoint
from config.general_functions import check_directory
from config.general_functions import (loading_data_kks_ana, loading_data_kks_bin, loading_data_kks_nary,
                                      loading_data_dict_kks_ana, loading_data_dict_kks_bin, creating_list_of_submodel)


async def actualizations_vk_svbu(print_log, name_directory: str, progress: QProgressBar) -> None:
    """Функция обновления видеокадров в папке SVBU_(1/2)/NPP_models из папки SVBU_(1/2)/NPP_models_new"""
    set_vis: Set[str] = set(listdir(path.join(name_directory, 'NPP_models')))
    set_vis_new: Set[str] = set(listdir(path.join(name_directory, 'NPP_models_new')))
    numbers_vis = len(set_vis)
    number = 1
    for i_vis in sorted(set_vis):
        progress.setValue(round(number / numbers_vis * 100))
        if i_vis in set_vis_new:
            shutil.copy2(path.join(name_directory, 'NPP_models_new', i_vis),
                         path.join(name_directory, 'NPP_models', i_vis))
            await print_log(text=f'[{number}/{numbers_vis}]   +++{i_vis} видеокадр обновлен+++')
        else:
            await print_log(text=f'[{number}/{numbers_vis}]   '
                                      f'---Видеокадра {i_vis} нет в {name_directory}/NPP_models_new ---',
                                 color='red')
        number += 1


async def new_start_parsing_svg_files(print_log, svg: Set[str], directory: str, progress: QProgressBar) -> bool:
    """
    Функция производит поиск всех подмоделей на видеокадрах после чего находит на подмоделях привязки (KKS).
    Проверяет наличие KKS в действующей базе и если не находит, подготавливает запись в файл замечаний.
    :param print_log: Функция записи лога в консоль
    :param svg: Список svg-файлов
    :param directory: Название системы в которой ведется поиск замечаний
    :param progress: Прогресс выполнения программы
    :return: None
    """
    set_kks_ana_data = await loading_data_kks_ana(directory=directory)
    set_kks_bin_data = await loading_data_kks_bin(directory=directory)
    set_kks_nary_data = await loading_data_kks_nary(directory=directory)
    dict_kks_ana_data = await loading_data_dict_kks_ana(directory=directory)
    dict_kks_bin_data = await loading_data_dict_kks_bin(directory=directory)

    if not await checking_data(print_log=print_log, name_system=directory,
                               data_ana=set_kks_ana_data, data_bin=set_kks_bin_data, data_nary=set_kks_nary_data,
                               dict_kks_ana_data=dict_kks_ana_data, dict_kks_bin_data=dict_kks_bin_data):
        msg = QMessageBox.question(QMainWindow(), 'Не все файлы базы есть в наличии',
                                   'Продолжить выполнение программы поиска замечаний, не смотря на то,'
                                   'что не все файлы базы есть в наличии?')
        if msg == QMessageBox.StandardButton.No:
            return False

    numbers = len(svg)
    number = 1
    for i_svg in sorted(svg):
        progress.setValue(round(number / numbers * 100))
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
            await print_log(text=text_log)
        else:
            text_log = f'{text_log:<55}Файл {i_svg} не svg!'
            await print_log(text=text_log, color='red')
        number += 1
    return True


async def checking_data(print_log, name_system, data_ana, data_bin, data_nary, dict_kks_ana_data, dict_kks_bin_data):
    """Функция проверяет наличие всех загруженных файлов"""
    flag = True
    if not data_ana:
        await print_log(f'Нет файла ANA_list_kks.txt в {name_system}\\data.\n'
                        f'Для его создания выполните пункт "обновления баз данных" для {name_system}\n', color='red')
        flag = False
    if not data_bin:
        await print_log(f'Нет файла BIN_list_kks.txt в {name_system}\\data.\n'
                        f'Для его создания выполните пункт "обновления баз данных" для {name_system}\n', color='red')
        flag = False
    if not data_nary:
        await print_log(f'Нет файла NARY_list_kks.txt в {name_system}\\data.\n'
                        f'Для его создания выполните пункт "обновления баз данных" для {name_system}\n', color='red')
        flag = False
    if not dict_kks_ana_data:
        await print_log(f'Нет файла ANA_json_kks.json в {name_system}\\data.\n'
                        f'Для его создания выполните пункт "обновления баз данных" для {name_system}\n', color='red')
        flag = False
    if not dict_kks_bin_data:
        await print_log(f'Нет файла BIN_json_kks.json в {name_system}\\data.\n'
                        f'Для его создания выполните пункт "обновления баз данных" для {name_system}\n', color='red')
        flag = False
    return flag


async def checking_kks_and_preparing_comment(kks_signal: str,
                                             list_error_kks: Set[str],
                                             name_submodel: str,
                                             set_svg: Set[str],
                                             set_kks_ana_data: Set[str],
                                             set_kks_bin_data: Set[str],
                                             set_kks_nary_data: Set[str],
                                             dict_kks_ana_data: Dict[str, Dict[str, str]],
                                             dict_kks_bin_data: Dict[str, Dict[str, str]]):
    """Функция проверки наличия в базе KKS и подготовки сообщения с замечанием в случае отсутствия сигнала в базе"""
    if re.search('_', kks_signal):
        if kks_signal in set_kks_ana_data:
            return
        elif kks_signal in set_kks_bin_data:
            return
        elif kks_signal in set_kks_nary_data:
            return
        text_search_similar_kks = await search_similar_kks(kks=kks_signal.split('_')[0],
                                                           dict_kks_ana_data=dict_kks_ana_data,
                                                           dict_kks_bin_data=dict_kks_bin_data)
    else:
        if f'{kks_signal}.svg' in set_svg or f'{kks_signal}.SVG' in set_svg:
            return
        kks_1 = f'{kks_signal}_F0'
        kks_2 = f'{kks_signal}_XQ01'
        if kks_1 in set_kks_nary_data or kks_2 in set_kks_ana_data:
            return
        text_search_similar_kks = await search_similar_kks(kks=kks_signal,
                                                           dict_kks_ana_data=dict_kks_ana_data,
                                                           dict_kks_bin_data=dict_kks_bin_data)
    list_error_kks.add(record_comment(kks=kks_signal,
                                      svg_constructor=name_submodel,
                                      text_search_similar_kks=text_search_similar_kks))


def recording_comments_to_a_file(directory: str, list_error_kks: Set[str], name_file: str):
    """Функция запись замечаний найденных на видеокадре в файл"""
    check_directory(path_directory=directory,
                    name_directory='Замечания по видеокадрам')
    with open(path.join(directory, 'Замечания по видеокадрам', f'{name_file}.txt'),
              'w', encoding='utf-8') as file:
        for i_kks in list_error_kks:
            file.write(f'{i_kks}\n')


def record_comment(kks: str, svg_constructor: str, text_search_similar_kks: str, text: str = 'нет в базе\t') -> str:
    """Добавляет запись о нахождении отсутствующего KKS в базе."""
    number_tyb = '\t' * ceil((24 - len(kks)) / 4)
    return f'{kks}{number_tyb}{text}{svg_constructor}{text_search_similar_kks}'


async def search_similar_kks(kks: str,
                             dict_kks_ana_data: Dict[str, Dict[str, str]],
                             dict_kks_bin_data: Dict[str, Dict[str, str]]) -> str:
    """
    Функция находящая в базе данных сигналы схожие с найденным основанием.
    :param kks: KKS найденного сигнала, по которому ищутся похожие.
    :param dict_kks_ana_data: Словарь аналоговых сигналов с описанием поделенных по KKS
    :param dict_kks_bin_data: Словарь бинарных сигналов с описанием поделенных по KKS
    :return: Все найденные сигналы с описанием.
    """
    text = ''
    if kks in dict_kks_ana_data:
        for i_kks in dict_kks_ana_data[kks]:
            text = f'{text}\n\t\tANA: {i_kks} - {dict_kks_ana_data[kks][i_kks]}'
    if kks in dict_kks_bin_data:
        for i_kks in dict_kks_bin_data[kks]:
            text = f'{text}\n\t\tBIN: {i_kks} - {dict_kks_bin_data[kks][i_kks]}'
    return text


async def dict_loading(print_log, number_bloc: str) -> Dict:
    """
    Функция принимает номер блока и в соответствующей папке находит json файл в котором распределены видеокадры
    по группам.
    :param print_log: Функция записи лога в консоль
    :param number_bloc: Номер блока.
    :return: Словарь, содержащий словарь с названием группы(ключ) и списком видеокадров относящихся к группе.
    """
    path_vis = path.join(number_bloc, 'data', 'kks_vis_groups.json')
    try:
        with open(path_vis, 'r', encoding='UTF-8') as file_json:
            data = json.load(file_json)
            return data
    except FileNotFoundError:
        await print_log(f'Нет файла "kks_vis_groups.json" в папке {path.join(number_bloc, "data")}')
        return {}

