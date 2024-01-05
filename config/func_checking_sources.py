from csv import reader
from PyQt6.QtWidgets import QProgressBar
from config.general_functions import (check_directory, check_file, loading_data_kks_ana, loading_data_kks_bin,
                                      loading_data_kks_nary)
from os import path
from typing import Set, List

import re


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
                    text_line = "\t".join(i_line)
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
    Функция поиска в файле ana_file-1.txt несуществующих KKS
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
                    text_line = "\t".join(i_line)
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
