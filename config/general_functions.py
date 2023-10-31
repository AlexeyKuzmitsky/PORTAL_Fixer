import time
from os import path, mkdir
from typing import Set, Dict
from .timer import timer
from .get_logger import log_info_print
import json
from csv import reader


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
            print(f'Создана папка: {name_directory}')
            # log.info(f'Создана папка: {name_directory}')
            return True
    else:
        if not path.isdir(path.join(path_directory, name_directory)):
            print(f'Создана папка: {path.join(path_directory, name_directory)}')
            # log.info(f'Создана папка: {path.join(path_directory, name_directory)}')
            mkdir(path.join(path_directory, name_directory))
            return True
    return False


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
                            'Нет файла PLS_BIN_NARY_CONF.dmp в папке DbDumps')
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
