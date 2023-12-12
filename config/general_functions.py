import time
import json
import shutil
import os

from os import path, mkdir
from typing import Set, Dict, List
from .timer import timer
from .get_logger import log_info_print, log_info
from config.point_description import AnchorPoint
from PyQt6.QtWidgets import QProgressBar

from csv import reader


async def creating_list_of_submodel(name_system: str, name_svg: str) -> List[AnchorPoint]:
    """
    Функция составляющая список подмоделей на видеокадре.
    :param name_system: Файл svg проверяемого видеокадра.
    :param name_svg: Название svg файла.
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
                                       name_svg=name_svg)
                    flag_constructor = False
                    list_constructor.clear()
                else:
                    list_constructor.append(i_line)
            else:
                if '<image' in i_line and '</image>' in i_line or '<image' in i_line and '/>' in i_line:
                    list_constructor.append(i_line)
                    await new_submodel(list_constructor=list_constructor,
                                       list_submodel=list_submodel,
                                       name_svg=name_svg)
                    list_constructor.clear()
                elif '<image' in i_line:
                    flag_constructor = True
                    list_constructor.clear()
                    list_constructor.append(i_line)
    return list_submodel


async def new_submodel(list_constructor, list_submodel, name_svg: str) -> None:
    """
    Функция создания новой точки на видеокадре.
    :param list_constructor: Характеристики подмодели.
    :param list_submodel: Список точек уже найденных на видеокадре.
    :param name_svg: Название svg файла на котором находится подмодель.
    :return: None
    """
    submodel = AnchorPoint(full_description_of_the_submodel=list_constructor, name_svg=name_svg)
    submodel.set_name_submodel()
    if submodel.name_submodel:
        try:
            submodel.search_kks_on_submodel()
        except IndexError as e:
            print(submodel.name_svg)
            print(submodel.full_description_of_the_submodel)
            print(e)
        list_submodel.append(submodel)


async def new_file_data_ana_bin_nary(print_log, name_system: str,
                                     progress: QProgressBar, min_progress: int=0, max_progress: int=100) -> None:
    """
    Функция обновления файлов со списком KKS сигналов. По завершению обновляются (создаются если не было) 3 файла:
    BIN_list_kks.txt со списком бинарных сигналов
    NARY_list_kks.txt со списком много битовых сигналов
    ANA_list_kks.txt со списков аналоговых сигналов
    :param print_log: функция вывода лога.
    :param name_system: Папка в которой будут обновления.
    :param progress: Прогресс выполнения программы
    :param min_progress: Минимальный процент прогресса
    :param max_progress: Максимальный процент прогресса
    :return: None
    """
    check_directory(path_directory=name_system, name_directory='DbDumps')
    check_directory(path_directory=name_system, name_directory='data')

    set_kks_bin_date = set()
    set_kks_nary_date = set()
    set_kks_ana_date = set()

    dict_kks_bin_data = dict()
    dict_kks_ana_data = dict()

    await print_log(text='Сбор BIN сигналов')
    progress.setValue(round((max_progress-min_progress) * 5 / 100 + min_progress))
    try:
        with open(path.join(name_system, 'DbDumps', 'PLS_BIN_CONF.dmp'), 'r', encoding='windows-1251') as file:
            new_text = reader(file, delimiter='|')
            for i_line in new_text:
                try:
                    full_kks = i_line[42]
                    kks = full_kks.partition('_')[0]
                    description = i_line[43]

                    if i_line[14] == '-1':
                        set_kks_bin_date.add(full_kks)
                    else:
                        set_kks_nary_date.add(full_kks)

                    if kks in dict_kks_bin_data:
                        dict_kks_bin_data[kks][full_kks] = description
                    else:
                        dict_kks_bin_data[kks] = {full_kks: description}

                except IndexError:
                    ...
        progress.setValue(round((max_progress - min_progress) * 35 / 100 + min_progress))
        with open(path.join(name_system, 'data', 'BIN_json_kks.json'), 'w', encoding='UTF-8') as json_file:
            json.dump(dict_kks_bin_data, json_file, indent=4, ensure_ascii=False)
        progress.setValue(round((max_progress - min_progress) * 40 / 100 + min_progress))
        with open(path.join(name_system, 'data', 'BIN_list_kks.txt'), 'w', encoding='UTF-8') as file:
            for i_kks in sorted(set_kks_bin_date):
                file.write(f'{i_kks}\n')
        progress.setValue(round((max_progress - min_progress) * 45 / 100 + min_progress))
        with open(path.join(name_system, 'data', 'NARY_list_kks.txt'), 'w', encoding='UTF-8') as file:
            for i_kks in sorted(set_kks_nary_date):
                file.write(f'{i_kks}\n')

        await print_log(text='Сигналы BIN собраны успешно', color='green')

        await print_log(text='Сбор ANA сигналов')
    except FileNotFoundError:
        await print_log(f'Нет файла PLS_BIN_CONF.dmp в {name_system}\\DbDumps.\n'
                        f'Сбор бинарных и много битовых сигналов невозможен',
                        color='red')
    progress.setValue(round((max_progress - min_progress) * 50 / 100 + min_progress))
    try:
        with open(path.join(name_system, 'DbDumps', 'PLS_ANA_CONF.dmp'), 'r', encoding='windows-1251') as file:
            new_text = reader(file, delimiter='|', quotechar=' ')
            for i_line in new_text:
                try:
                    full_kks = i_line[78]
                    kks = full_kks.partition('_')[0]
                    description = i_line[79]
                    set_kks_ana_date.add(full_kks)
                    if kks in dict_kks_ana_data:
                        dict_kks_ana_data[kks][full_kks] = description
                    else:
                        dict_kks_ana_data[kks] = {full_kks: description}
                except IndexError:
                    pass
        progress.setValue(round((max_progress - min_progress) * 65 / 100 + min_progress))
        with open(path.join(name_system, 'data', 'ANA_json_kks.json'), 'w', encoding='UTF-8') as json_file:
            json.dump(dict_kks_ana_data, json_file, indent=4, ensure_ascii=False)
        progress.setValue(round((max_progress - min_progress) * 80 / 100 + min_progress))
        with open(path.join(name_system, 'data', 'ANA_list_kks.txt'), 'w', encoding='UTF-8') as file:
            for i_kks in sorted(set_kks_ana_date):
                file.write(f'{i_kks}\n')
        await print_log(text='Сигналы ANA собраны успешно', color='green')
        progress.setValue(round((max_progress - min_progress) * 95 / 100 + min_progress))
    except FileNotFoundError:
        await print_log(f'Нет файла PLS_ANA_CONF.dmp в {name_system}\\DbDumps.\nСбор аналоговых сигналов невозможен',
                        color='red')
    progress.setValue(round((max_progress - min_progress) + min_progress))


def check_directory(path_directory: str, name_directory: str) -> bool:
    """
    Функция проверяет наличие директории по указанному адресу и при ее отсутствии создает ее.
    :param path_directory: Путь к директории.
    :param name_directory: Имя директории.
    :return: True - создана новая директория, False - новая директория не создавалась(уже существовала)
    """
    if path_directory == '':
        if not path.isdir(name_directory):
            mkdir(name_directory)
            log_info.info(f'Создана папка: {name_directory}')
            return True
    else:
        if not path.isdir(path.join(path_directory, name_directory)):
            log_info.info(f'Создана папка: {path.join(path_directory, name_directory)}')
            mkdir(path.join(path_directory, name_directory))
            return True
    return False


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


async def loading_data_kks_ana(directory: str = '') -> Set[str]:
    """
    Функция считывающая базу аналоговых сигналов.
    :return: Множество аналоговых сигналов
    """
    set_kks_ana_data: Set[str] = set()

    try:
        with open(path.join(directory, 'data', 'ANA_list_kks.txt')) as file:
            for i_line in file:
                set_kks_ana_data.add(i_line[:-1])
    except FileNotFoundError:
        pass
    return set_kks_ana_data


async def loading_data_kks_bin(directory: str = '') -> Set[str]:
    """
    Функция считывающая базу бинарных сигналов.
    :return: Множество бинарных сигналов
    """
    set_kks_bin_data: Set[str] = set()

    try:
        with open(path.join(directory, 'data', 'BIN_list_kks.txt')) as file:
            for i_line in file:
                set_kks_bin_data.add(i_line[:-1])
    except FileNotFoundError:
        pass
    return set_kks_bin_data


async def loading_data_dict_kks_ana(directory: str = '') -> Dict[str, Dict[str, str]]:
    """
    Функция считывающая базу аналоговых сигналов с описанием сигналов.
    :return: Словарь аналоговых сигналов с описанием
    """
    dict_kks_ana_data: Dict[str, Dict[str, str]] = dict()
    try:
        with open(path.join(directory, 'data', 'ANA_json_kks.json'), 'r', encoding='UTF-8') as json_file:
            dict_ana_kks = json.load(json_file)
            dict_kks_ana_data.update(dict_ana_kks)
    except FileNotFoundError:
        pass
    return dict_kks_ana_data


async def loading_data_dict_kks_bin(directory: str = '') -> Dict[str, Dict[str, str]]:
    """
    Функция считывающая базу бинарных сигналов с описанием сигналов.
    :return: Словарь бинарных сигналов с описанием
    """
    dict_kks_bin_data: Dict[str, Dict[str, str]] = dict()
    try:
        with open(path.join(directory, 'data', 'BIN_json_kks.json'), 'r', encoding='UTF-8') as json_file:
            dict_bin_kks = json.load(json_file)
            dict_kks_bin_data.update(dict_bin_kks)
    except FileNotFoundError:
        pass
    return dict_kks_bin_data


async def loading_data_kks_nary(directory: str = '') -> Set[str]:
    """
    Функция считывающая базу бинарных сигналов.
    :return: Множество бинарных сигналов
    """
    set_kks_nary_data: Set[str] = set()

    try:
        with open(path.join(directory, 'data', 'NARY_list_kks.txt')) as file:
            for i_line in file:
                set_kks_nary_data.add(i_line[:-1])
    except FileNotFoundError:
        pass
    return set_kks_nary_data


def program_execution_delay(pause_length_in_seconds: int):
    """Функция приостанавливает выполнение программы на n секунд"""
    for i in range(pause_length_in_seconds, 0, -1):
        print(f'\rПрограмма продолжится через {i} сек.', end='')
        time.sleep(1)
    print('\r                                                  ', end='')
    time.sleep(0.1)
    print()


def database_loading_list_kks(name_system: str):
    """Функция Загружает из подготовленных файлов базу данных сигналов и возвращает 2 списка с аналоговыми сигналами
    и бинарными"""
    set_ana_signal: Set[str] = set()
    try:
        with open(path.join(name_system, 'data', 'ANA_list_kks.txt'), 'r', encoding='UTF-8') as file_ana_signals:
            for i_line in file_ana_signals:
                set_ana_signal.add(i_line[:-1])
    except FileNotFoundError:
        log_info_print.info(f'\nERROR Не найден файл {name_system}/data/ANA_list_kks.txt.\n'
                            f'Программа продолжит выполнение без этих сигналов.'
                            f'\nДля создания файла ANA_list_kks.txt выберите пункт "Обновление базы данных"'
                            f' и систему {name_system}')
        program_execution_delay(pause_length_in_seconds=3)

    set_bin_signal: Set[str] = set()
    try:
        with open(path.join(name_system, 'data', 'BIN_list_kks.txt'), 'r', encoding='UTF-8') as file_bin_signals:
            for i_line in file_bin_signals:
                set_bin_signal.add(i_line[:-1])
    except FileNotFoundError:
        log_info_print.info(f'\nERROR Не найден файл {name_system}/data/BIN_list_kks.txt.\n'
                            f'Программа продолжит выполнение без этих сигналов.'
                            f'\nДля создания файла BIN_list_kks.txt выберите пункт "Обновление базы данных"'
                            f' и систему {name_system}')
        program_execution_delay(pause_length_in_seconds=3)

    return set_ana_signal, set_bin_signal


@timer
def new_date(name_system: str) -> None:
    """
    Функция обновления файлов со списком KKS сигналов. По завершению обновляются (создаются если не было) 2 файла:
    BIN_list_kks.txt со списком бинарных сигналов
    ANA_list_kks.txt со списков аналоговых сигналов
    :param name_system: папка в которой будут обновления.
    :return: None
    """
    check_directory(path_directory=name_system, name_directory='DbDumps')
    check_directory(path_directory=name_system, name_directory='data')
    set_kks_bin_date = set()
    set_kks_ana_date = set()

    dict_kks_bin_data = dict()
    dict_kks_ana_data = dict()

    log_info_print.info('Сбор BIN сигналов')

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
                    uno_dict_kks = {full_kks: description}
                    dict_kks_bin_data[kks] = uno_dict_kks

                set_kks_bin_date.add(i_line[42])
            except IndexError:
                ...

    with open(path.join(name_system, 'data', 'BIN_json_kks.json'), 'w', encoding='UTF-8') as json_file:
        json.dump(dict_kks_bin_data, json_file, indent=4, ensure_ascii=False)

    with open(path.join(name_system, 'data', 'BIN_list_kks.txt'), 'w', encoding='UTF-8') as file:
        for i_kks in set_kks_bin_date:
            file.write(f'{i_kks}\n')

    log_info_print.info('Accesses. Сигналы BIN собраны успешно')

    log_info_print.info('Сбор ANA сигналов')
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
                    uno_dict_kks = {full_kks: description}
                    dict_kks_ana_data[kks] = uno_dict_kks

                set_kks_ana_date.add(i_line[78])
            except IndexError:
                pass

    with open(path.join(name_system, 'data', 'ANA_json_kks.json'), 'w', encoding='UTF-8') as json_file:
        json.dump(dict_kks_ana_data, json_file, indent=4, ensure_ascii=False)

    with open(path.join(name_system, 'data', 'ANA_list_kks.txt'), 'w', encoding='UTF-8') as file:
        for i_kks in set_kks_ana_date:
            file.write(f'{i_kks}\n')
    log_info_print.info('Accesses. Сигналы ANA собраны успешно')
    input('Программа выполнена успешно\n'
          'Enter...')


def add_data_file_bin_nary(name_system: str):
    """Функция создает файл BIN_NARY_kks.json"""
    check_directory(path_directory=name_system, name_directory='DbDumps')
    check_directory(path_directory=name_system, name_directory='data')
    dict_kks_bin_data: Dict = dict()

    log_info_print.info('Сбор описания сигналов NARY')

    try:
        dict_description: Dict[int, Dict[str, str]] = add_list_description(name_system=name_system)
    except FileNotFoundError:
        log_info_print.info('INFO Создание файла BIN_NARY_kks.json невозможно. '
                            f'Нет файла PLS_BIN_NARY_CONF.dmp в папке {name_system}\\DbDumps')
        return
    with open(path.join(name_system, 'DbDumps', 'PLS_BIN_CONF.dmp'), 'r', encoding='windows-1251') as file:
        new_text = reader(file, delimiter='|')
        for i_line in new_text:
            try:
                full_kks = i_line[42]
                number_description = i_line[14]
                if number_description != '-1':
                    dict_kks_bin_data[full_kks] = dict_description[int(number_description)]
                else:
                    dict_kks_bin_data[full_kks] = dict()
            except IndexError:
                ...
            except ValueError:
                ...
                # print(i_line)
            except KeyError:
                print(i_line)

    with open(path.join(name_system, 'data', 'BIN_NARY_kks.json'), 'w', encoding='UTF-8') as json_file:
        json.dump(dict_kks_bin_data, json_file, indent=2, ensure_ascii=False)


def add_list_description(name_system: str) -> Dict[int, Dict[str, str]]:
    """Функция подготавливает словарь, в котором ключ это номер описания, значение - список описаний битов"""
    dict_description: Dict[int, Dict[str, str]] = dict()
    with open(path.join(name_system, 'DbDumps', 'PLS_BIN_NARY_CONF.dmp'), 'r', encoding='windows-1251') as file_nary:
        file_nary.readline()
        file_nary.readline()
        file_nary.readline()
        list_name_descriptions = file_nary.readline()[:-1].split('|')[-16:]
        new_text = reader(file_nary, delimiter='|')
        for i_line in new_text:
            try:
                number_description = int(i_line[0])
                dict_description[number_description] = dict()
                num = -16
                for i_name_description in list_name_descriptions:
                    text = i_line[num]
                    if text == '':
                        num += 1
                        continue
                    dict_description[number_description][i_name_description] = text
                    num += 1
            except (IndexError, ValueError):
                ...

    return dict_description


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


@timer
def new_data_ana_bin_nary(name_system: str) -> None:
    """
    Функция обновления файлов со списком KKS сигналов. По завершению обновляются (создаются если не было) 3 файла:
    BIN_list_kks.txt со списком бинарных сигналов
    NARY_list_kks.txt со списком много битовых сигналов
    ANA_list_kks.txt со списков аналоговых сигналов
    :param name_system: папка в которой будут обновления.
    :return: None
    """
    check_directory(path_directory=name_system, name_directory='DbDumps')
    check_directory(path_directory=name_system, name_directory='data')

    set_kks_bin_date = set()
    set_kks_nary_date = set()
    set_kks_ana_date = set()

    log_info_print.info('Сбор BIN сигналов')

    with open(path.join(name_system, 'DbDumps', 'PLS_BIN_CONF.dmp'), 'r', encoding='windows-1251') as file:
        new_text = reader(file, delimiter='|')
        for i_line in new_text:
            try:
                full_kks = i_line[42]
                if i_line[14] == '-1':

                    set_kks_bin_date.add(full_kks)
                else:
                    set_kks_nary_date.add(full_kks)
            except IndexError:
                ...

    with open(path.join(name_system, 'data', 'BIN_list_kks.txt'), 'w', encoding='UTF-8') as file:
        for i_kks in set_kks_bin_date:
            file.write(f'{i_kks}\n')

    with open(path.join(name_system, 'data', 'NARY_list_kks.txt'), 'w', encoding='UTF-8') as file:
        for i_kks in set_kks_nary_date:
            file.write(f'{i_kks}\n')

    log_info_print.info('Accesses. Сигналы BIN собраны успешно')

    log_info_print.info('Сбор ANA сигналов')
    with open(path.join(name_system, 'DbDumps', 'PLS_ANA_CONF.dmp'), 'r', encoding='windows-1251') as file:
        new_text = reader(file, delimiter='|', quotechar=' ')
        for i_line in new_text:
            try:
                set_kks_ana_date.add(i_line[78])
            except IndexError:
                pass

    with open(path.join(name_system, 'data', 'ANA_list_kks.txt'), 'w', encoding='UTF-8') as file:
        for i_kks in set_kks_ana_date:
            file.write(f'{i_kks}\n')
    log_info_print.info('Accesses. Сигналы ANA собраны успешно')


def database_loading_list_kks_ana_bin_nary(name_system: str):
    """Функция Загружает из подготовленных файлов базу данных сигналов и возвращает 3 списка(множества) с аналоговыми
    сигналами, бинарными и много битовыми сигналами"""
    set_ana_signal: Set[str] = set()
    try:
        with open(path.join(name_system, 'data', 'ANA_list_kks.txt'), 'r', encoding='UTF-8') as file_ana_signals:
            for i_line in file_ana_signals:
                set_ana_signal.add(i_line[:-1])
    except FileNotFoundError:
        log_info_print.info(f'\nERROR Не найден файл {name_system}/data/ANA_list_kks.txt.\n'
                            f'Программа продолжит выполнение без этих сигналов.'
                            f'\nДля создания файла ANA_list_kks.txt выберите пункт "Обновление базы данных"'
                            f' и систему {name_system}')
        program_execution_delay(pause_length_in_seconds=3)

    set_bin_signal: Set[str] = set()
    try:
        with open(path.join(name_system, 'data', 'BIN_list_kks.txt'), 'r', encoding='UTF-8') as file_bin_signals:
            for i_line in file_bin_signals:
                set_bin_signal.add(i_line[:-1])
    except FileNotFoundError:
        log_info_print.info(f'\nERROR Не найден файл {name_system}/data/BIN_list_kks.txt.\n'
                            f'Программа продолжит выполнение без этих сигналов.'
                            f'\nДля создания файла BIN_list_kks.txt выберите пункт "Обновление базы данных"'
                            f' и систему {name_system}')
        program_execution_delay(pause_length_in_seconds=3)

    set_nary_signal: Set[str] = set()
    try:
        with open(path.join(name_system, 'data', 'NARY_list_kks.txt'), 'r', encoding='UTF-8') as file_bin_signals:
            for i_line in file_bin_signals:
                set_nary_signal.add(i_line[:-1])
    except FileNotFoundError:
        log_info_print.info(f'\nERROR Не найден файл {name_system}/data/NARY_list_kks.txt.\n'
                            f'Программа продолжит выполнение без этих сигналов.'
                            f'\nДля создания файла NARY_list_kks.txt выберите пункт "Обновление базы данных"'
                            f' и систему {name_system}')
        program_execution_delay(pause_length_in_seconds=3)

    return set_ana_signal, set_bin_signal, set_nary_signal
