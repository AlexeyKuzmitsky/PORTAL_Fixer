from csv import reader
from PyQt6.QtWidgets import QProgressBar
from config.general_functions import (check_directory, check_file, loading_data_kks_ana, loading_data_kks_bin,
                                      loading_data_kks_nary)
from os import path
from typing import Set, List
from config.conf import dict_level_signale, dict_suffix_level_signale

import re
import csv


async def parse_the_formula(text: str) -> List[str]:
    """Функция производящая поиск KKS сигналов в полученной строке и возвращает множество найденных сигналов"""
    list_kks = re.findall(r'"([^\\"]+_[^\\"]+)"', text)
    return list_kks

async def search_for_comments_in_a_ana_file_1(print_log, name_system: str, progress: QProgressBar) -> None:
    """
    Функция поиска в файле ana_file-1.txt несуществующих KKS
    :param print_log: функция вывода лога.
    :param name_system: Система в которой проверяется файл.
    :param progress: Прогресс выполнения программы
    :return: None
    """
    result = await checking_the_presence_all_ana_files(print_log=print_log, name_system=name_system)
    if not result:
        return

    set_ana_signal = await loading_data_kks_ana(directory=name_system)

    set_kks: Set[str] = set()
    num = 1
    with open(path.join(name_system, 'DbSrc', 'ana_file-1.txt'), 'r', encoding='windows-1251') as file:
        csv_iter = list(reader(file, delimiter='\t'))
        len_num = len(csv_iter)
        for i_line in csv_iter[1:]:

            result = await parse_the_formula(text=i_line[19])
            for i_kks in result:
                if ' ' in i_kks:
                    await print_log(text=f'У KKS {i_kks} есть лишние пробелы', color='yellow')
                    i_kks = i_kks.replace(' ', '')

                if not i_kks in set_ana_signal:
                    # text_line = "\t".join(i_line)
                    await print_log(text=f'Нет в базе KKS {i_kks}', color='red')
                    # await print_log(text=f'Нет в базе KKS {i_kks} в строке {text_line}\n', color='red')

            set_kks.add(i_line[1])
            progress.setValue(round(num / len_num * 100))
            num += 1


async def checking_the_presence_all_ana_files(print_log, name_system: str):
    """Функция проверяет наличие всех нужных файлов для работы программы"""
    check_directory(path_directory=name_system, name_directory='DbSrc')
    if not check_file(path_directory=path.join(name_system, 'DbSrc'), name_file='ana_file-1.txt'):
        await print_log(text=f'Нет файла {name_system}/DbSrc/ana_file-1.txt, выполнение поиска замечанйи невозможно',
                        color='red')
        return False

    check_directory(path_directory=name_system, name_directory='data')
    if not check_file(path_directory=path.join(name_system, 'data'), name_file='ANA_list_kks.txt'):
        await print_log(text=f'Нет файла {name_system}/data/ANA_list_kks.txt, выполнение поиска замечанйи невозможно!\n'
                             f'Для продолжения выполните "Обновление баз данных сигналов"',
                        color='red')
        return False
    return True


async def search_for_comments_in_a_bin_file_1(print_log, name_system: str, progress: QProgressBar) -> None:
    """
    Функция поиска в файле bin_file-1.txt несуществующих KKS
    :param print_log: функция вывода лога.
    :param name_system: Система в которой проверяется файл.
    :param progress: Прогресс выполнения программы
    :return: None
    """
    result = await checking_the_presence_all_bin_files(print_log=print_log, name_system=name_system)
    if not result:
        return

    set_ana_signal = await loading_data_kks_ana(directory=name_system)
    set_bin_signal = await loading_data_kks_bin(directory=name_system)
    set_nary_signal = await loading_data_kks_nary(directory=name_system)

    set_kks: Set[str] = set()
    num = 1
    with open(path.join(name_system, 'DbSrc', 'bin_file-1.txt'), 'r', encoding='windows-1251') as file:
        csv_iter = list(reader(file, delimiter='\t'))
        len_num = len(csv_iter)
        for i_line in csv_iter[1:]:

            result = await parse_the_formula(text=i_line[9])
            for i_kks in result:
                if ' ' in i_kks:
                    await print_log(text=f'У KKS {i_kks} есть лишние пробелы', color='yellow')
                    i_kks = i_kks.replace(' ', '')

                if i_kks in set_bin_signal or i_kks in set_nary_signal or i_kks in set_ana_signal:
                    continue
                else:
                    # text_line = "\t".join(i_line)
                    await print_log(text=f'Нет в базе KKS {i_kks}', color='red')
                    # await print_log(text=f'Нет в базе KKS {i_kks} в строке {text_line}\n', color='red')

            set_kks.add(i_line[1])
            progress.setValue(round(num / len_num * 100))
            num += 1


async def checking_the_presence_all_bin_files(print_log, name_system: str):
    """Функция проверяет наличие всех нужных файлов для работы программы"""
    check_directory(path_directory=name_system, name_directory='DbSrc')
    if not check_file(path_directory=path.join(name_system, 'DbSrc'), name_file='bin_file-1.txt'):
        await print_log(text=f'Нет файла {name_system}/DbSrc/bin_file-1.txt, выполнение поиска замечанйи невозможно',
                        color='red')
        return False

    check_directory(path_directory=name_system, name_directory='data')
    if not check_file(path_directory=path.join(name_system, 'data'), name_file='BIN_list_kks.txt'):
        await print_log(text=f'Нет файла {name_system}/data/BIN_list_kks.txt, выполнение поиска замечанйи невозможно!\n'
                             f'Для продолжения выполните "Обновление баз данных сигналов"',
                        color='red')
        return False
    return True


async def checking_the_presence_of_all_files(print_log, name_system: str) -> List[str]:
    """
    Функция составляющая список файлов, для которых можно произвести проверку.
    Args:
        print_log: функция вывода лога
        name_system: Система в которой проверяется файл
    Returns: Список найденных файлов bin_file в директории
    """
    full_list_bin_file = [
        'bin_file00.rep',
        'bin_file01.rep',
        'bin_file02.rep',
        'bin_file03.rep',
        'bin_file04.rep',
        'bin_file05.rep',
        'bin_file06.rep',
        'bin_file07.rep',
        'bin_file08.rep',
        'bin_file09.rep',
        'bin_file10.rep',
        'bin_file11.rep',
        'bin_file12.rep',
        'bin_file13.rep',
        'bin_file45.rep'
    ]
    list_file_bin = list()
    for i_name_file in full_list_bin_file:
        if path.isfile(path.join(name_system, 'DbSrc', i_name_file)):
            list_file_bin.append(i_name_file)
            await print_log(text=f'Файл {name_system}/DbSrc/{i_name_file}, добавлен в обработку', color='green')
        else:
            await print_log(text=f'Нет файла {name_system}/DbSrc/{i_name_file}, он исключен из обработки', color='red')
    return list_file_bin


async def searching_for_comments_in_files_bin(print_log, name_system: str, progress: QProgressBar) -> bool:
    """
    Функция ведет проверку файлов bin_file.rep на соответствие кода уставок присвоенному суффиксу
    Args:
        print_log: Функция вывода лога
        name_system: Система в которой проверяется файл
        progress: Прогресс выполнения программы
    Returns: bool (True - успешное выполнение, False - программа была прервана)
    """

    progress.setValue(1)
    list_file_bin = await checking_the_presence_of_all_files(print_log=print_log, name_system=name_system)
    if not list_file_bin:
        await print_log(text=f'В каталоге {name_system}/DbSrc/ нет файлов bin_file\n'
                             f'Выполнение поиска замечаний по уставкам невозможно.', color='red'),
        await print_log(text=f'Для устранения замечания возьмите последние исходники из каталога DbSrc\n'
                             f'и положите их в {name_system}/DbSrc')
        progress.setValue(100)
        return False

    progress.setValue(4)
    len_num = len(list_file_bin)
    num = 0
    await print_log(text=f'Проверяемый файл\tЗавершен\t\tКоличество ошибок шт.')
    for i_name_file in list_file_bin:
        await print_log(text=f'{i_name_file}')
        num += 1
        with open(path.join(name_system, 'DbSrc', i_name_file), 'r', encoding='ANSI') as file:
            data_file = list(csv.reader(file, delimiter='\t'))
        count_error: int = 0
        with open(path.join(name_system, 'Ошибки в уставках', f'fail_suffix_{i_name_file[:-4]}.txt'), 'w', encoding='UTF-8') as fail_file:
            fail_file.write(f'KKS_signal\tSuffix_signal\tCod_signal\n')
            for i_line in data_file[1:]:
                kks = i_line[1]
                suffix = i_line[1].split('_')[1]
                kod_use_signal = i_line[4]
                try:
                    if not dict_level_signale[kod_use_signal] == dict_suffix_level_signale[suffix]:
                        count_error += 1
                        fail_file.write(f'{kks}\t{suffix}-{dict_suffix_level_signale[suffix]}\t'
                                        f'{kod_use_signal}-{dict_level_signale[kod_use_signal]}\n')
                except KeyError:
                    pass
        await print_log(text='\tSuccessfully', color='green', a_new_line=False)
        await print_log(text=f'\t\t{count_error}', color='red', a_new_line=False)
        progress.setValue(round(num / len_num * 100))
