from csv import reader
from PyQt6.QtWidgets import QProgressBar
from config.general_functions import (check_directory, check_file, loading_data_kks_ana, loading_data_kks_bin,
                                      loading_data_kks_nary, creating_list_of_submodel,
                                      loading_data_dict_kks_bin_description)
from os import path, listdir
from typing import Set, List, Dict
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

    set_ana_signal = await loading_data_kks_ana(name_system=name_system, print_log=print_log)

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

                if i_kks not in set_ana_signal:
                    await print_log(text=f'Нет в базе KKS {i_kks}', color='red')

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

    set_ana_signal = await loading_data_kks_ana(name_system=name_system, print_log=print_log)
    set_bin_signal = await loading_data_kks_bin(name_system=name_system, print_log=print_log)
    set_nary_signal = await loading_data_kks_nary(name_system=name_system, print_log=print_log)

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
                    await print_log(text=f'Нет в базе KKS {i_kks}', color='red')

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
        with open(path.join(name_system, 'Ошибки в уставках', f'fail_suffix_{i_name_file[:-4]}.txt'),
                  'w', encoding='UTF-8') as fail_file:
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


async def new_start_parsing_svg_files(print_log, name_system: str, progress: QProgressBar) -> None:
    """
    Функция создает файл altstation.dip
    Args:
        print_log: Функция вывода лога
        name_system: Система в которой проверяется файл
        progress: Прогресс выполнения программы
    Returns: None
    """
    await print_log(text='Поиск подмоделей obj_Station_stat.svg на видеокадрах:')
    list_svg_obj_station_stat: List[str] = await list_files_with_submodel(print_log=print_log, name_system=name_system,
                                                                          progress=progress)

    await print_log(text='Поиск видеокадров на которые ссылаются подмодели obj_Station_stat.svg')
    set_svg_obj_station_stat: Set[str] = await list_of_name_links_svg(
        print_log=print_log, name_system=name_system,
        list_svg_obj_station_stat=list_svg_obj_station_stat,
        progress=progress)

    await print_log(text='Поиск сигналов на видеокадрах')
    dict_of_detected_signal_on_svg: Dict[str, Set[str]] = await search_for_signals_bin_nary_on_svg(
        print_log=print_log, name_system=name_system,
        set_svg_obj_station_stat=set_svg_obj_station_stat, progress=progress)

    await print_log(text='Поиск дубликатов привязок на видеокадров')
    dict_of_detected_signal_on_svg: Dict[str, Set[str]] = await removing_duplicates_by_priority(
        print_log=print_log, dict_signal_on_svg=dict_of_detected_signal_on_svg, name_system=name_system)

    await print_log(text='Запись файла altStation.dic')
    await recording_found_signals_to_a_file(name_system=name_system,
                                            dict_of_detected_signal_on_svg=dict_of_detected_signal_on_svg)
    await print_log(text=f'Всего записано сигналов: {await count_elements(my_dict=dict_of_detected_signal_on_svg)}')
    await print_log(text=f'для {len(dict_of_detected_signal_on_svg)} видеокадров')
    progress.setValue(100)


async def removing_duplicates_by_priority(print_log, dict_signal_on_svg: dict[str, Set[str]],
                                          name_system: str) -> Dict[str, Set[str]]:
    """
    Функция проверяет приоритеты сигналов для альтстанций, и удаляет дубликаты найденных одинаковых сигналов на разных
    видеокадрах
    Args:
        print_log: Функция вывода лога
        dict_signal_on_svg: Словарь имен видеокадров и найденных на них сигналов
        name_system: Имя системы (директории) в которой берется файл altStation_priority.txt
    Returns: Словарь имен видеокадров и найденных на них сигналов без дубликатов
    """
    dict_of_detected_signal_on_svg: Dict[str, Set[str]] = dict()
    all_signals: Set[str] = set()  # Все сигналы найденные на видеокадре
    dict_priority: Dict[str, str] = dict()  # словарь приоритетов распределения сигналов на видеокадрах
    try:
        with open(path.join(name_system, 'data', 'altStation_priority.txt'), 'r', encoding='UTF-8') as file:
            for i_line in file:
                signal, svg_file = i_line[: -1].split('\t')
                dict_priority[signal] = svg_file

        for signal, svg_file in dict_priority.items():
            if svg_file in dict_signal_on_svg:
                if signal in dict_signal_on_svg[svg_file]:
                    if svg_file in dict_of_detected_signal_on_svg:
                        dict_of_detected_signal_on_svg[svg_file].add(signal)
                    else:
                        dict_of_detected_signal_on_svg[svg_file] = {signal}
                    all_signals.add(signal)
    except FileNotFoundError:
        await print_log(text=f'Нет файла {name_system}/data/altStation_priority.txt. Приоритет не будет установлен',
                        color='red')
    for svg_file, signal in sorted(dict_signal_on_svg.items()):
        dict_signal_on_svg[svg_file] -= all_signals
        if svg_file in dict_of_detected_signal_on_svg:
            dict_of_detected_signal_on_svg[svg_file].update(dict_signal_on_svg[svg_file])
        else:
            dict_of_detected_signal_on_svg[svg_file] = dict_signal_on_svg[svg_file]
        all_signals.update(dict_of_detected_signal_on_svg[svg_file])

    return dict_of_detected_signal_on_svg


async def list_files_with_submodel(print_log, name_system: str, progress: QProgressBar) -> List[str]:
    """
    Функция ведет поиск на видеокадрах подмодель obj_Station_stat.svg, при нахождении записывает название видеокадра
    Args:
        print_log: Функция вывода лога
        name_system: Система в которой проверяется файл
        progress: Прогресс выполнения программы
    Returns: Список найденных svg файлов (видеокадров)
    """
    list_svg_obj_station_stat: List[str] = list()  # список видеокадров на которых есть подмодель obj_Station_stat.svg
    list_name_svg = listdir(path.join(name_system, 'NPP_models'))
    numbers = len(list_name_svg)
    number = 1
    for i_svg in list_name_svg:
        progress.setValue(round(50 * (number / numbers)))
        await print_log(text=f'[{number} из {numbers}] Проверка {i_svg}')
        if i_svg.endswith('.svg') or i_svg.endswith('.SVG'):
            if await search_obj_station_stat(name_system=name_system, name_svg=i_svg):
                list_svg_obj_station_stat.append(i_svg)
                await print_log(text='\t+Есть+', color='green', a_new_line=False)
            else:
                await print_log(text='\t-Нет-', a_new_line=False)
        number += 1
    await print_log(text=f'Поиск завершен. Найдено {len(list_svg_obj_station_stat)} видеокадров', color='green')
    progress.setValue(50)
    return list_svg_obj_station_stat


async def list_of_name_links_svg(print_log, name_system: str, list_svg_obj_station_stat: List[str],
                                 progress: QProgressBar) -> Set[str]:
    """
    Функция находящая подмодели obj_Station_stat.svg на видеокадре и записывающая привязки (ссылки на видеокадры)
    подмоделей
    Args:
        print_log: Функция вывода лога
        name_system: Система в которой проверяется файл
        list_svg_obj_station_stat: Список содержащий названия svg содержащих подмодель obj_Station_stat.svg
        progress: Прогресс выполнения программы
    Returns: Список привязок на видеокадры
    """
    number = 1
    numbers = len(list_svg_obj_station_stat)

    set_svg_obj_station_stat: Set[str] = set()  # список видеокадров на которые ссылаются подмодели obj_Station_stat.svg
    for i_svg in list_svg_obj_station_stat:
        await print_log(text=f'[{number} из {numbers}] Проверка {i_svg}')
        list_submodel = await creating_list_of_submodel(name_system=name_system,
                                                        name_svg=i_svg,
                                                        name_submodel='obj_Station_stat.svg')
        await print_log(text=f'\tНайдено ссылок: {len(list_submodel)}', a_new_line=False)
        number += 1
        progress.setValue(round((60 - 50) * (number / numbers)) + 50)
        set_svg_obj_station_stat.update({i_svg.signal_description[0]['text_kks'] for i_svg in list_submodel})
    return set_svg_obj_station_stat


async def search_for_signals_bin_nary_on_svg(print_log, name_system: str, set_svg_obj_station_stat: Set[str],
                                             progress: QProgressBar) -> Dict[str, Set[str]]:
    await print_log(text='Загрузка базы данных сигналов')
    set_ana_signal = await loading_data_kks_ana(name_system=name_system, print_log=print_log)
    progress.setValue(61)
    set_bin_signal = await loading_data_kks_bin(name_system=name_system, print_log=print_log)
    progress.setValue(62)
    set_nary_signal = await loading_data_kks_nary(name_system=name_system, print_log=print_log)
    progress.setValue(63)
    dict_bin_signals = await loading_data_dict_kks_bin_description(name_system=name_system, print_log=print_log)
    progress.setValue(64)
    await print_log(text='Сигналы загружены')
    numbers = len(set_svg_obj_station_stat)
    number = 1
    dict_of_detected_signal_on_svg: Dict[str, Set[str]] = dict()  # KKS найденные на каждом видеокадре
    for i_svg in set_svg_obj_station_stat:
        await print_log(text=f'[{number} из {numbers}] Проверка {i_svg}.svg')
        if not path.isfile(path.join(name_system, 'NPP_models', f'{i_svg}.svg')):
            await print_log(text=f'\tОшибка', color='red', a_new_line=False)
            await print_log(text=f'Видеокадра {name_system}/NPP_models/{i_svg}.svg нет. Поиск сигналов невозможен',
                            color='red')
            continue
        dict_of_detected_signal_on_svg[i_svg] = set()
        list_submodel = await creating_list_of_submodel(name_system=name_system, name_svg=f'{i_svg}.svg')
        for i_submodel in list_submodel:
            set_signal = i_submodel.check_signal_existence_database(data_ana=set_ana_signal,
                                                                    data_bin=set_bin_signal,
                                                                    data_nary=set_nary_signal,
                                                                    dict_bin=dict_bin_signals)

            dict_of_detected_signal_on_svg[i_svg].update(set_signal)

        await print_log(text=f'\tНайдено сигналов: {len(dict_of_detected_signal_on_svg[i_svg])}', a_new_line=False)
        number += 1
        progress.setValue(round((95 - 65) * (number / numbers)) + 65)
    return dict_of_detected_signal_on_svg


async def recording_found_signals_to_a_file(name_system: str,
                                            dict_of_detected_signal_on_svg: Dict[str, Set[str]]) -> None:
    """
    Функция записывает найденные сигналы в файл altStation.dic
    Args:
        name_system: Система в которой проверяется файл
        dict_of_detected_signal_on_svg: KKS найденные на каждом видеокадре
    Returns: None
    """
    with open(path.join(name_system, 'altStation.dic'), 'w', encoding='UTF-8') as file_alt_station:
        for name_svg, list_signal in sorted(dict_of_detected_signal_on_svg.items()):
            for i_signal in sorted(list_signal):
                file_alt_station.write(f'{i_signal}\t{name_svg}\n')


async def search_obj_station_stat(name_system: str, name_svg: str) -> bool:
    """
    Функция поиска использования видеокадром подмодели obj_Station_stat.svg.
    Args:
        name_system: Название системы в которой ведется проверка
        name_svg: Имя видеокадра.
    Returns:  True при наличии подмодели, False при отсутствии.
    """
    with open(path.join(name_system, 'NPP_models', name_svg), 'r', encoding='windows-1251') as file_svg:
        for i_line in file_svg:
            if 'obj_Station_stat.svg' in i_line:
                return True
    return False


async def count_elements(my_dict):
    number_elements = 0
    for list_number in my_dict.values():
        number_elements += len(list_number)
    return number_elements
