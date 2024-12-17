import shutil
import os

from os import path, listdir
from typing import Set, Dict, List
from config.point_description import AnchorPoint
from PyQt6.QtWidgets import QProgressBar
from config.checking_all_directories import check_directory


from csv import reader


async def creating_list_of_submodel(name_system: str, name_svg: str, name_submodel: str = None) -> List[AnchorPoint]:
    """
    Функция составляющая список подмоделей на видеокадре.
    :param name_system: Файл svg проверяемого видеокадра.
    :param name_svg: Название svg файла.
    :param name_submodel: Название подмодели которую ищем. Если None, ведется поиск всех подмоделей.
    :return: Список найденных подмоделей.
    """
    with open(path.join(name_system, 'NPP_models', name_svg), 'r', encoding='windows-1251') as svg_file:
        list_submodel: List[AnchorPoint] = list()
        list_constructor: List[str] = list()
        flag_constructor = False

        for i_line in svg_file:
            if flag_constructor:
                if '</image>' in i_line:
                    list_constructor.append(i_line)
                    await new_submodel(list_constructor=list_constructor,
                                       list_submodel=list_submodel,
                                       name_svg=name_svg,
                                       name_submodel=name_submodel)
                    flag_constructor = False
                    list_constructor.clear()
                else:
                    list_constructor.append(i_line)
            else:
                if '<image' in i_line and '</image>' in i_line or '<image' in i_line and '/>' in i_line:
                    list_constructor.append(i_line)
                    await new_submodel(list_constructor=list_constructor,
                                       list_submodel=list_submodel,
                                       name_svg=name_svg,
                                       name_submodel=name_submodel)
                    list_constructor.clear()
                elif '<image' in i_line:
                    flag_constructor = True
                    list_constructor.clear()
                    list_constructor.append(i_line)
    return list_submodel


async def new_submodel(list_constructor, list_submodel, name_svg: str, name_submodel: str) -> None:
    """
    Функция создания новой точки на видеокадре.
    :param list_constructor: Характеристики подмодели.
    :param list_submodel: Список точек уже найденных на видеокадре.
    :param name_svg: Название svg файла на котором находится подмодель.
    :param name_submodel: Название подмодели которую ищем. Если None, ведется поиск всех подмоделей.
    :return: None
    """
    submodel = AnchorPoint(full_description_of_the_submodel=list_constructor, name_svg=name_svg)
    if name_submodel:
        if submodel.set_name_submodel() != name_submodel:
            return
    else:
        submodel.set_name_submodel()
    if submodel.name_submodel:
        try:
            submodel.search_kks_on_submodel()
        except IndexError as e:
            print(submodel.name_svg)
            print(submodel.full_description_of_the_submodel)
            print(e)
        list_submodel.append(submodel)


def check_file(path_directory: str, name_file: str) -> bool:
    """
    Функция проверяет наличие файла по указанному адресу.
    :param path_directory: Путь к файлу.
    :param name_file: Имя файла.
    :return: True - файл есть, False - файла нет
    """
    if path.exists(path.join(path_directory, name_file)):
        return True
    return False


async def loading_data_kks_ana(name_system: str = '', print_log=None) -> Set[str] | bool:
    """
    Функция считывающая базу аналоговых сигналов.
    :return: Множество аналоговых сигналов
    """
    set_kks_ana_data: Set[str] = set()

    await print_log(text=f'Сбор списка сигналов ANA ({name_system})')
    if not check_file(path_directory=path.join(name_system, 'DbDumps'), name_file='PLS_ANA_CONF.dmp'):
        await print_log(f'Нет файла PLS_ANA_CONF.dmp в {name_system}\\DbDumps.\n'
                        f'Сбор аналоговых сигналов невозможен', color='red', level='ERROR')
        return set_kks_ana_data
    with open(path.join(name_system, 'DbDumps', 'PLS_ANA_CONF.dmp'), 'r', encoding='windows-1251') as file:
        new_text = reader(file, delimiter='|', quotechar=' ')
        for i_line in new_text:
            try:
                full_kks = i_line[78]
                set_kks_ana_data.add(full_kks)
            except IndexError:
                pass
    await print_log(text='\tsuccessfully', color='green', a_new_line=False)
    return set_kks_ana_data


async def loading_data_kks_bin(name_system: str, print_log) -> Set[str]:
    """
    Функция считывающая базу бинарных сигналов.
    :return: Множество бинарных сигналов
    """
    set_kks_bin_date: Set[str] = set()
    await print_log(text=f'Сбор списка сигналов BIN ({name_system})')
    if not check_file(path_directory=path.join(name_system, 'DbDumps'), name_file='PLS_BIN_CONF.dmp'):
        await print_log(f'Нет файла PLS_BIN_CONF.dmp в {name_system}\\DbDumps.\n'
                        f'Сбор сигналов BIN невозможен', color='red', level='ERROR')
        return set_kks_bin_date
    with open(path.join(name_system, 'DbDumps', 'PLS_BIN_CONF.dmp'), 'r', encoding='windows-1251') as file:
        new_text = reader(file, delimiter='|')
        for i_line in new_text:
            try:
                full_kks = i_line[42]
                if i_line[18] == '1':
                    set_kks_bin_date.add(full_kks)
            except IndexError:
                pass
    await print_log(text='\tsuccessfully', color='green', a_new_line=False)
    return set_kks_bin_date


async def loading_data_dict_kks_ana_description(name_system: str, print_log) -> Dict[str, Dict[str, str]]:
    """
    Функция составляющая словарь сигналов, в котором ключ - KKS сигнала без суффикса,
    значение - словарь (где ключ - KKS сигнала с суффиксом, значение - описание сигнала)
    """
    dict_kks_ana_data: Dict[str, Dict[str, str]] = dict()
    await print_log(text=f'Сбор описания сигналов ANA ({name_system})')
    if not check_file(path_directory=path.join(name_system, 'DbDumps'), name_file='PLS_ANA_CONF.dmp'):
        await print_log(f'Нет файла PLS_ANA_CONF.dmp в {name_system}\\DbDumps.\n'
                        f'Сбор описания сигналов ANA невозможен', color='red', level='ERROR')
        return dict_kks_ana_data

    with open(path.join(name_system, 'DbDumps', 'PLS_ANA_CONF.dmp'), 'r', encoding='windows-1251') as file:
        new_text = reader(file, delimiter='|', quotechar=' ')
        for i_line in new_text:
            try:
                full_kks = i_line[78]
                kks = full_kks.partition('_')[0]
                description = i_line[79]
                if kks in dict_kks_ana_data:
                    dict_kks_ana_data[kks][full_kks] = description
                else:
                    dict_kks_ana_data[kks] = {full_kks: description}
            except IndexError:
                pass
    await print_log(text='\tsuccessfully', color='green', a_new_line=False)
    return dict_kks_ana_data


async def loading_data_dict_kks_bin_description(name_system: str, print_log) -> Dict[str, Dict[str, str]]:
    """
    Функция считывающая базу бинарных сигналов с описанием сигналов.
    :return: Словарь бинарных сигналов с описанием
    """
    dict_kks_bin_data: Dict[str, Dict[str, str]] = dict()

    await print_log(text=f'Сбор описания сигналов BIN ({name_system})')
    if not check_file(path_directory=path.join(name_system, 'DbDumps'), name_file='PLS_BIN_CONF.dmp'):
        await print_log(f'Нет файла PLS_BIN_CONF.dmp в {name_system}\\DbDumps.\n'
                        f'Сбор описания сигналов BIN невозможен', color='red', level='ERROR')
        return dict_kks_bin_data

    with open(path.join(name_system, 'DbDumps', 'PLS_BIN_CONF.dmp'), 'r', encoding='windows-1251') as file:
        new_text = reader(file, delimiter='|')
        for i_line in new_text:
            try:
                full_kks = i_line[42]
                kks = full_kks.partition('_')[0]
                description = i_line[43]
                if kks in dict_kks_bin_data:
                    dict_kks_bin_data[kks][full_kks] = description
                else:
                    dict_kks_bin_data[kks] = {full_kks: description}
            except IndexError:
                pass
    await print_log(text='\tsuccessfully', color='green', a_new_line=False)
    return dict_kks_bin_data


async def loading_data_kks_nary(name_system: str, print_log) -> Set[str]:
    """
    Функция считывающая базу много битовых сигналов.
    :return: Множество много битовых сигналов
    """
    set_kks_nary_date: Set[str] = set()
    await print_log(text=f'Сбор сигналов NARY ({name_system})')
    if not check_file(path_directory=path.join(name_system, 'DbDumps'), name_file='PLS_BIN_CONF.dmp'):
        await print_log(f'Нет файла PLS_BIN_CONF.dmp в {name_system}\\DbDumps.\n'
                        f'Сбор сигналов NARY невозможен', color='red', level='ERROR')
        return set_kks_nary_date
    with open(path.join(name_system, 'DbDumps', 'PLS_BIN_CONF.dmp'), 'r', encoding='windows-1251') as file:
        new_text = reader(file, delimiter='|')
        for i_line in new_text:
            try:
                full_kks = i_line[42]
                if i_line[18] == '16':
                    set_kks_nary_date.add(full_kks)
                # else:
                #     set_kks_nary_date.add(full_kks)
            except IndexError:
                ...
    await print_log(text='\tsuccessfully', color='green', a_new_line=False)
    return set_kks_nary_date


async def sort_files_into_groups(number_bloc: str, group_svg: dict, progress: QProgressBar):
    """
    Функция распределения замечаний по видеокадрам по соответствующим группам.
    :param number_bloc: Номер блока (папка в которой будет работать программа).
    :param group_svg: Словарь групп распределения видеокадров.
    :param progress: Прогресс выполнения программы
    :return: None
    """
    list_svg_file = os.listdir(path.join(number_bloc, 'Замечания по видеокадрам'))
    number = 1
    numbers = len(list_svg_file)
    for i_kks in list_svg_file:
        progress.setValue(round(number / numbers * 100))
        if i_kks.endswith('.txt'):
            name_group = group_search_by_file_name(name_file=i_kks[:-4], dict_groups=group_svg)
            check_directory(path_directory=number_bloc,
                            name_directory='Замечания по видеокадрам')

            check_directory(path_directory=path.join(number_bloc, 'Замечания по видеокадрам'),
                            name_directory=name_group)

            file_copy(start_path=path.join(number_bloc, 'Замечания по видеокадрам'),
                      end_path=path.join(number_bloc, 'Замечания по видеокадрам', name_group),
                      name_file=i_kks)
        number += 1


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
    except PermissionError:
        pass


def del_file(path_file: str, name_file: str) -> None:
    """
    Проверяет наличие файла в заданной директории и при его наличии удаляет.
    :param path_file: Путь по которому проверяется файл.
    :param name_file: Имя проверяемого файла.
    :return: None
    """
    if path.isfile(path.join(path_file, name_file)):
        os.remove(path.join(path_file, name_file))


async def actualizations_vk(print_log, name_directory: str, progress: QProgressBar) -> None:
    """Функция обновления видеокадров в папке SVBU_(1/2)/NPP_models из папки SVBU_(1/2)/NPP_models_new"""
    set_vis: Set[str] = set(listdir(path.join(name_directory, 'NPP_models')))
    set_vis_new: Set[str] = set(listdir(path.join(name_directory, 'NPP_models_new')))
    numbers_vis = len(set_vis)
    number = 1
    for i_vis in sorted(set_vis):
        await print_log(text=f'[{number}/{numbers_vis}]   Обновление видеокадра {i_vis}')
        progress.setValue(round(number / numbers_vis * 100))
        if i_vis in set_vis_new:
            shutil.copy2(path.join(name_directory, 'NPP_models_new', i_vis),
                         path.join(name_directory, 'NPP_models', i_vis))
            await print_log(text='\t+++обновлен+++', a_new_line=False, color='green')
        else:
            await print_log(text=f'\t---Нет в {name_directory}/NPP_models_new---',
                            a_new_line=False, color='red')
        number += 1
