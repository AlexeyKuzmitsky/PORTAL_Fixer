import json
import os
from os import path
import shutil
from typing import Dict
from .get_logger import log_info, log_error_print
from .general_functions import check_directory


def dict_loading(number_bloc: str) -> Dict:
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
        log_error_print.error(f'Нет файла "kks_vis_groups.json" в папке {path.join(number_bloc, "data")}')
        print('Нет файла "kks_vis_groups.json"')
        return {}


def del_file(path_file: str, name_file: str) -> None:
    """
    Проверяет наличие файла в заданной директории и при его наличии удаляет.
    :param path_file: Путь по которому проверяется файл.
    :param name_file: Имя проверяемого файла.
    :return: None
    """
    if path.isfile(path.join(path_file, name_file)):
        os.remove(path.join(path_file, name_file))
    else:
        print(f'Error (файла {name_file} нет по пути {path_file})')


def group_search_by_file_name(name_file: str, dict_groups: dict) -> str:
    """
    Функция принимающая имя файла и словарь с именами видеокадров распределенных по группам. Производит поиск
    принадлежности файла к определенной группе и возвращающей имя этой группы. Если в группах KKS видеокадра не
    был найден возвращает 'No_group'.
    :param name_file: Имя файла.
    :param dict_groups: Словарь групп с KKS видеокадров.
    :return: Имя группы
    """
    for i_type in dict_groups:
        for i_name_type in dict_groups[i_type]:
            if name_file in dict_groups[i_type][i_name_type]:
                return i_name_type
    else:
        return 'No_group'


def file_copy(start_path: str, end_path: str, name_file: str) -> None:
    """
    Функция получающая начальный и конечный путь файла копирует его и удаляет его из изначального пути.
    :param start_path: Начальная директория хранения файла.
    :param end_path: Путь к конечной директории (куда копируется файл).
    :param name_file: Имя копируемого файла.
    :return: None
    """
    try:
        shutil.copyfile(path.join(start_path, name_file), path.join(end_path, name_file))
        del_file(path_file=start_path, name_file=name_file)
        log_info.info(f'Файл "{name_file}" перенесен из папки "{start_path}" в папку "{end_path}"')
    except PermissionError:
        log_error_print.error(f'start_path={start_path}, end_path={end_path}, name_file={name_file}')
        exit()


def sort_files_into_groups(number_bloc: str, group_svg: dict):
    """
    Функция распределения замечаний по видеокадрам по соответствующим группам.
    :param number_bloc: Номер блока (папка в которой будет работать программа).
    :param group_svg: Словарь групп распределения видеокадров.
    :return: None
    """
    print('Подождите...')
    list_svg_file = os.listdir(path.join(number_bloc, 'Замечания по видеокадрам'))
    for i_kks in list_svg_file:
        if i_kks.endswith('.txt'):
            name_group = group_search_by_file_name(name_file=i_kks[:-4], dict_groups=group_svg)
            check_directory(path_directory=number_bloc,
                            name_directory='Замечания по видеокадрам')

            check_directory(path_directory=path.join(number_bloc, 'Замечания по видеокадрам'),
                            name_directory=name_group)

            file_copy(start_path=path.join(number_bloc, 'Замечания по видеокадрам'),
                      end_path=path.join(number_bloc, 'Замечания по видеокадрам', name_group),
                      name_file=i_kks)
        else:
            log_error_print.info(f'Файл {i_kks} имеет формат не txt')


if __name__ in '__main__':
    pass
