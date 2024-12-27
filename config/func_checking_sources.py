from csv import reader

import pandas
from PyQt6.QtWidgets import QProgressBar
from config.general_functions import (check_directory, check_file, loading_data_kks_ana, loading_data_kks_bin,
                                      loading_data_kks_nary, creating_list_of_submodel,
                                      loading_data_dict_kks_bin_description)
from os import path, listdir
from typing import Set, List, Dict
from config.conf import dict_level_signale, dict_suffix_level_signale

import re
import csv
import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor


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
            number += 1
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
    with open(path.join(name_system, 'Исходники', 'altStation.dic'), 'w', encoding='UTF-8') as file_alt_station:
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


async def creating_new_file_skuvp_bin(print_log, name_system: str, source_system: str, name_file: str,
                                      progress: QProgressBar, start: int = 0, end: int = 100) -> None:
    """
    Функция создает файл с описанием бинарных и многобитовых сигналов ..._BIN.txt на основе исходных данных
    Args:
        print_log: Функция вывода лога
        name_system: Имя системы куда создается файл
        source_system: Система из которой берутся файлы описания сигналов
        name_file: Имя создаваемого файла
        progress: Прогресс выполнения программы
        start: Начальные проценты выполнения программы
        end: Конечные проценты выполнения программы
    Returns: None
    """
    progress.setValue(percentage_calculation(start=start, end=end, count=1))
    if name_system == 'SVSU':
        name_file_import = 'SVSU_IMPORT.txt'
    else:
        name_file_import = 'SVBU_IMPORT.txt'
    if await check_file_for_bin(print_log=print_log, name_system=source_system, name_file_import=name_file_import):
        progress.setValue(percentage_calculation(start=start, end=end, count=5))
        df_bin = await preparing_data_for_the_file_bin(print_log=print_log,
                                                       source_system=source_system,
                                                       name_file_import=name_file_import,
                                                       progress=progress,
                                                       start=percentage_calculation(start=start, end=end, count=5),
                                                       end=percentage_calculation(start=start, end=end, count=90))

        await print_log(text=f'Запись полученных данных в файл {name_system}/Исходники/{name_file}')
        df_bin.to_csv(path.join(name_system, 'Исходники', name_file), sep='\t', index=False)
        await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    else:
        await print_log(text='Выполнение задачи невозможно!', color='red')
    progress.setValue(percentage_calculation(start=start, end=end, count=100))


async def preparing_data_for_the_file_bin(print_log, source_system: str, name_file_import: str,
                                          progress: QProgressBar, start: int = 0, end: int = 100):
    """
    Функция подготавливает данные для файла с описанием бинарных и многобитовых сигналов ..._BIN.txt
    Args:
        print_log: Функция вывода лога
        source_system: Система из которой берутся исходники
        name_file_import: Имя файла списка импорта сигналов
        progress: Прогресс выполнения программы
        start: Начальные проценты выполнения программы
        end: Конечные проценты выполнения программы
    Returns: None
    """
    df_bin = pd.DataFrame(columns=['RTM', 'function', 'NAME_RUS', 'NAME_RUS_FULL', 'z_verw', 'alarm', 'hist',
                                   'signum', 'ITEMID_EXT', 'CategoryNR', 'Type'])
    df_bin.set_index('function', drop=False, inplace=True)

    await print_log(text=f'Загрузка {name_file_import}')
    df_svbu_import = pd.read_csv(path.join(source_system, 'DbSrc', name_file_import), sep='\t')
    df_svbu_import.set_index('function', drop=False, inplace=True)
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    progress.setValue(percentage_calculation(start=start, end=end, count=6))

    await print_log(text='Загрузка PLS_PROC_CATEGORIES.dmp')
    df_pls_proc_categories = await async_load_data(path.join(source_system, 'DbDumps', 'PLS_PROC_CATEGORIES.dmp'))
    df_pls_proc_categories.set_index('*#CATEGORYNR', drop=False, inplace=True)
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    progress.setValue(percentage_calculation(start=start, end=end, count=7))

    await print_log(text='Загрузка PLS_BIN_CONF.dmp')
    df_plc_bin_conf = await async_load_data(file_path=path.join(source_system, 'DbDumps', 'PLS_BIN_CONF.dmp'))
    df_plc_bin_conf.set_index('PVID', drop=False, inplace=True)
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    progress.setValue(percentage_calculation(start=start, end=end, count=15))

    list_kks_nary = df_svbu_import.loc[df_svbu_import['type'] == 'N', 'function'].tolist()

    await print_log(text='Сбор данных')
    number_kks = len(list_kks_nary)
    count = 0
    for i_kks in list_kks_nary:
        try:
            await filling_data_on_signal_bin(kks=i_kks,
                                             df_bin=df_bin,
                                             df_plc_bin_conf=df_plc_bin_conf,
                                             df_svbu_import=df_svbu_import,
                                             df_pls_proc_categories=df_pls_proc_categories,
                                             type_signal=3)
        except KeyError:
            df_bin.drop(axis=0, index=i_kks, inplace=True)
            await print_log(text=f'В базе данных {source_system} нет многобитового сигнала {i_kks}. '
                                 f'Он не будет добавлен',
                            color='red')
        count += 1
        progress.setValue(percentage_calculation(start=percentage_calculation(start=start, end=end, count=15),
                                                 end=percentage_calculation(start=start, end=end, count=75),
                                                 count=count,
                                                 number=number_kks))

    list_kks_bin = df_svbu_import.loc[df_svbu_import['type'] == 'B', 'function'].tolist()
    for i_kks in list_kks_bin:
        try:
            await filling_data_on_signal_bin(kks=i_kks,
                                             df_bin=df_bin,
                                             df_plc_bin_conf=df_plc_bin_conf,
                                             df_svbu_import=df_svbu_import,
                                             df_pls_proc_categories=df_pls_proc_categories,
                                             type_signal=2)
        except KeyError:
            df_bin.drop(axis=0, index=i_kks, inplace=True)
            await print_log(text=f'В базе данных {source_system} нет бинарного сигнала {i_kks}. Он не будет добавлен',
                            color='red')
        except ValueError:
            df_bin.drop(axis=0, index=i_kks, inplace=True)
            await print_log(text=f'В файле импорта найден дубликат сигнала {i_kks}. Он не будет добавлен',
                            color='red')
        count += 1
        progress.setValue(percentage_calculation(start=percentage_calculation(start=start, end=end, count=75),
                                                 end=percentage_calculation(start=start, end=end, count=95),
                                                 count=count,
                                                 number=number_kks))
    return df_bin


async def filling_data_on_signal_bin(kks: str, df_bin, df_plc_bin_conf, df_svbu_import, df_pls_proc_categories,
                                     type_signal: int) -> None:
    """
    Функция заполняет данные по сигналу
        Args:
        kks: KKS сигнала
        df_bin: База данных в которую будут ложиться данные сигнала
        df_plc_bin_conf: База данных файла PLS_BIN_CONF
        df_svbu_import: База данных файла SVBU_IMPORT
        df_pls_proc_categories: База данных файла PLS_PROC_CATEGORIES
        type_signal: тип сигнала (1 - аналоговый, 2 - бинарный, 3 - многобитовый)
    Returns: None
    """
    df_bin.loc[kks, 'RTM'] = kks
    df_bin.loc[kks, 'function'] = kks
    df_bin.loc[kks, 'NAME_RUS'] = df_plc_bin_conf.loc[kks, 'PVTEXT']
    df_bin.loc[kks, 'NAME_RUS_FULL'] = df_plc_bin_conf.loc[kks, 'PVDESCRIPTION']
    df_bin.loc[kks, 'CategoryNR'] = df_plc_bin_conf.loc[kks, 'CATEGORYNR']
    try:
        df_bin.loc[kks, 'signum'] = df_svbu_import.loc[kks, 'signum']
    except ValueError:
        print(kks)
    df_bin.loc[kks, 'Type'] = type_signal

    id_proc_categories = df_plc_bin_conf.loc[kks, 'PROCCATNR']
    if str(id_proc_categories) != 'nan':
        description = df_pls_proc_categories.loc[id_proc_categories, 'DESCRIPTION']
        df_bin.loc[kks, 'z_verw'] = description.split('PriorityLevel=')[1][0]

        alarm_value_mask = df_pls_proc_categories.loc[id_proc_categories, 'ALARMVALUEMASK']
        result = ''

        if type_signal == 3:
            for i in range(15, -1, -1):
                if alarm_value_mask & 2 ** i:
                    result += 'X'
                else:
                    result += '-'
        elif type_signal == 2:
            if alarm_value_mask == 0:
                result = '--'
            elif alarm_value_mask == 1:
                result = 'X-'
            elif alarm_value_mask == 2:
                result = '-X'
            elif alarm_value_mask == 3:
                result = 'XX'
        df_bin.loc[kks, 'alarm'] = result

        if df_pls_proc_categories.loc[id_proc_categories, 'HISTORIANSUPPORTED']:
            df_bin.loc[kks, 'hist'] = 1
        else:
            df_bin.loc[kks, 'hist'] = 0
    else:
        df_bin.loc[kks, 'hist'] = 1

    text_plc_itemid = df_plc_bin_conf.loc[kks, 'PLC_ITEMID'].split(':')[-2]
    if '=' not in text_plc_itemid:
        df_bin.loc[kks, 'ITEMID_EXT'] = text_plc_itemid


def percentage_calculation(start: int, end: int, count: int, number: int = 100) -> int:
    """
    Функция высчитывает настоящий процент выполнения программы по значениям
    Args:
        start: Начальный процент
        end: Конечный процент
        count: Счетчик, место на котором сейчас или проценты
        number: Общее число
    Returns: int
    """
    try:
        difference = end - start
        result = round(count / number * difference + start)
        return result
    except ZeroDivisionError:
        print(start, end, count, number)
        return 0


async def check_file_existence(print_log, file_path: str, name_file: str) -> bool:
    """
    Функция проверяет наличие файлов PLS_BIN_CONF.dmp и SVBU_IMPORT.txt
    Args:
        print_log: Функция вывода лога
        file_path: Путь к файлу
        name_file: Имя проверяемого файла
    Returns: bool
    """
    await print_log(text=f'Проверка наличия файла {file_path} {name_file}')
    if path.isfile(path.join(file_path, name_file)):
        await print_log(text=f'\tTrue', color='green', a_new_line=False)
        return True
    else:
        await print_log(text=f'\tFalse', color='red', a_new_line=False)
        return False


async def check_file_for_bin(print_log, name_system: str, name_file_import: str) -> bool:
    """
    Функция проверяет наличие файлов PLS_BIN_CONF.dmp и SVBU_IMPORT.txt
    Args:
        print_log: Функция вывода лога
        name_system: Система у которой проверяется наличие файла
        name_file_import: Имя файла импорта
    Returns: bool
    """
    file_check_flag = True

    await print_log(text=f'Проверка наличия файла PLS_BIN_CONF.dmp в {name_system}/DbDumps')
    if path.isfile(path.join(name_system, 'DbDumps', 'PLS_BIN_CONF.dmp')):
        await print_log(text=f'\tTrue', color='green', a_new_line=False)
    else:
        await print_log(text=f'\tFalse', color='red', a_new_line=False)
        file_check_flag = False

    await print_log(text=f'Проверка наличия файла PLS_PROC_CATEGORIES.dmp в {name_system}/DbDumps')
    if path.isfile(path.join(name_system, 'DbDumps', 'PLS_PROC_CATEGORIES.dmp')):
        await print_log(text=f'\tTrue', color='green', a_new_line=False)
    else:
        await print_log(text=f'\tFalse', color='red', a_new_line=False)
        file_check_flag = False

    await print_log(text=f'Проверка наличия файла {name_file_import} в {name_system}/DbSrc')
    if path.isfile(path.join(name_system, 'DbSrc', name_file_import)):
        await print_log(text=f'\tTrue', color='green', a_new_line=False)
    else:
        await print_log(text=f'\tFalse', color='red', a_new_line=False)
        file_check_flag = False
    return file_check_flag


async def creating_new_file_ana(print_log, name_system: str, source_system: str, name_file: str,
                                progress: QProgressBar, start: int = 0, end: int = 100) -> None:
    """
    Функция создает файл _ANA.txt на основе исходных данных (файл SVBU_IMPORT.txt из DbSrc SKU_VP
    и PLS_ANA_CONF.dmp из DbDumps SKU_VP
    Args:
        print_log: Функция вывода лога
        name_system: Система для которой создается файл
        source_system:  Система из которой берутся исходники
        name_file: Имя создаваемого файла
        progress: Прогресс выполнения программы
        start: Начальные проценты выполнения программы
        end: Конечные проценты выполнения программы
    Returns: None
    """
    progress.setValue(percentage_calculation(start=start, end=end, count=1))
    if name_system == 'SVSU':
        name_file_import = 'SVSU_IMPORT.txt'
    else:
        name_file_import = 'SVBU_IMPORT.txt'

    if await check_file_for_ana(print_log=print_log, name_system=source_system, name_file_import=name_file_import):
        progress.setValue(percentage_calculation(start=start, end=end, count=5))
        df_ana = await preparing_data_for_the_file_ana(print_log=print_log,
                                                       name_system=source_system,
                                                       name_file_import=name_file_import,
                                                       progress=progress,
                                                       start=percentage_calculation(start=start, end=end, count=5),
                                                       end=percentage_calculation(start=start, end=end, count=95))

        await print_log(text=f'Запись полученных данных в файл {name_system}/Исходники/{name_file}')
        df_ana.to_csv(path.join(name_system, 'Исходники', name_file), sep='\t', index=False)
        await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    else:
        await print_log(text='Выполнение задачи невозможно!', color='red')
    progress.setValue(percentage_calculation(start=start, end=end, count=100))


async def preparing_data_for_the_file_ana(print_log, name_system: str, name_file_import: str,
                                          progress: QProgressBar, start: int = 0, end: int = 100):
    """
    Функция подготавливает данные для файла SKUVP_ANA.txt
    Args:
        print_log: Функция вывода лога
        name_system: Система из которой берутся исходники
        name_file_import: Имя файла со списком импорта сигналов
        progress: Прогресс выполнения программы
        start: Начальные проценты выполнения программы
        end: Конечные проценты выполнения программы
    Returns: None
    """
    df_ana = pd.DataFrame(columns=['RTM', 'function', 'NAME_RUS', 'NAME_RUS_FULL',
                                   'MAX', 'MIN', 'HA', 'HW', 'HT', 'LT', 'LW', 'LA',
                                   'UNITSRUS', 'display', 'deadband',
                                   'z_verw', 'hist', 'histdeadband',
                                   'signum', 'ITEMID_EXT', 'CategoryNR', 'Type',
                                   'Department', 'Channel', 'alarmSite'
                                   ])
    df_ana.set_index('function', drop=False, inplace=True)

    await print_log(text=f'Загрузка {name_file_import}')
    df_svbu_import = pd.read_csv(path.join(name_system, 'DbSrc', name_file_import), sep='\t')
    df_svbu_import.set_index('function', drop=False, inplace=True)
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    progress.setValue(percentage_calculation(start=start, end=end, count=6))

    await print_log(text='Загрузка PLS_PROC_CATEGORIES.dmp')
    df_pls_proc_categories = await async_load_data(path.join(name_system, 'DbDumps', 'PLS_PROC_CATEGORIES.dmp'))
    df_pls_proc_categories.set_index('*#CATEGORYNR', drop=False, inplace=True)
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    progress.setValue(percentage_calculation(start=start, end=end, count=7))

    await print_log(text='Загрузка PLS_ANA_CONF.dmp')
    df_plc_ana_conf = await async_load_data(file_path=path.join(name_system, 'DbDumps', 'PLS_ANA_CONF.dmp'))
    df_plc_ana_conf.set_index('PVID', drop=False, inplace=True)
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    progress.setValue(percentage_calculation(start=start, end=end, count=15))

    await print_log(text='Загрузка PLS_DIMENSION_CONF.dmp')
    df_pls_dimension_conf = await async_load_data(file_path=path.join(name_system, 'DbDumps', 'PLS_DIMENSION_CONF.dmp'))
    df_pls_dimension_conf.set_index('*#DIMNR', drop=False, inplace=True)
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    progress.setValue(percentage_calculation(start=start, end=end, count=16))

    list_kks_ana = df_svbu_import.loc[df_svbu_import['type'] == 'A', 'function'].tolist()

    number_kks = len(list_kks_ana)
    count = 0
    for i_kks in list_kks_ana:
        try:
            filling_data_on_signal_ana(kks=i_kks,
                                       df_ana=df_ana,
                                       df_plc_ana_conf=df_plc_ana_conf,
                                       df_svbu_import=df_svbu_import,
                                       df_pls_proc_categories=df_pls_proc_categories,
                                       df_pls_dimension_conf=df_pls_dimension_conf)
        except KeyError:
            df_ana.drop(axis=0, index=i_kks, inplace=True)
            await print_log(text=f'В базе данных {name_system} нет аналогово сигнала {i_kks}. Он не будет добавлен',
                            color='red')
        except ValueError:
            df_ana.drop(axis=0, index=i_kks, inplace=True)
            await print_log(text=f'В файле импорта найден дубликат сигнала {i_kks}. Он не будет добавлен',
                            color='red')
        count += 1
        progress.setValue(percentage_calculation(start=percentage_calculation(start=start, end=end, count=16),
                                                 end=percentage_calculation(start=start, end=end, count=95),
                                                 count=count,
                                                 number=number_kks))
    return df_ana


def filling_data_on_signal_ana(kks: str, df_ana, df_plc_ana_conf, df_svbu_import, df_pls_proc_categories,
                               df_pls_dimension_conf) -> None:
    """
    Функция заполняет данные по сигналу
        Args:
        kks: KKS сигнала
        df_ana: База данных в которую будут ложиться данные сигнала
        df_plc_ana_conf: База данных файла PLS_ANA_CONF
        df_svbu_import: База данных сингалов импорта
        df_pls_proc_categories: База данных файла PLS_PROC_CATEGORIES
        df_pls_dimension_conf: База данных единиц измерения из файла PLS_DIMENSION_CONF
    Returns: None
    """
    df_ana.loc[kks, 'RTM'] = kks
    df_ana.loc[kks, 'function'] = kks
    df_ana.loc[kks, 'Type'] = 1
    df_ana.loc[kks, 'NAME_RUS'] = df_plc_ana_conf.loc[kks, 'PVTEXT']
    df_ana.loc[kks, 'NAME_RUS_FULL'] = df_plc_ana_conf.loc[kks, 'PVDESCRIPTION']
    df_ana.loc[kks, 'MAX'] = df_plc_ana_conf.loc[kks, 'RANGEHIGH']
    df_ana.loc[kks, 'MIN'] = df_plc_ana_conf.loc[kks, 'RANGELOW']

    df_ana.loc[kks, 'LA'] = df_plc_ana_conf.loc[kks, 'BOUND_LOW3']
    df_ana.loc[kks, 'LW'] = df_plc_ana_conf.loc[kks, 'BOUND_LOW2']
    df_ana.loc[kks, 'LT'] = df_plc_ana_conf.loc[kks, 'BOUND_LOW1']
    df_ana.loc[kks, 'HT'] = df_plc_ana_conf.loc[kks, 'BOUND_HIGH1']
    df_ana.loc[kks, 'HW'] = df_plc_ana_conf.loc[kks, 'BOUND_HIGH2']
    df_ana.loc[kks, 'HA'] = df_plc_ana_conf.loc[kks, 'BOUND_HIGH3']

    number_pls_dimension_conf = df_plc_ana_conf.loc[kks, 'DIMNR']
    if number_pls_dimension_conf != -1:
        df_ana.loc[kks, 'UNITSRUS'] = df_pls_dimension_conf.loc[number_pls_dimension_conf, 'DIMSTRING']
    df_ana.loc[kks, 'display'] = df_plc_ana_conf.loc[kks, 'ROUNDDIGITS']
    df_ana.loc[kks, 'deadband'] = df_plc_ana_conf.loc[kks, 'DEADBAND']
    df_ana.loc[kks, 'histdeadband'] = df_plc_ana_conf.loc[kks, 'HIST_DEADBAND']
    df_ana.loc[kks, 'CategoryNR'] = df_plc_ana_conf.loc[kks, 'CATEGORYNR']
    df_ana.loc[kks, 'alarmSite'] = df_plc_ana_conf.loc[kks, 'CATEGORYMAP3']

    id_proc_categories = df_plc_ana_conf.loc[kks, 'PROCCATNR']
    if str(id_proc_categories) != 'nan':
        description = df_pls_proc_categories.loc[id_proc_categories, 'DESCRIPTION']
        df_ana.loc[kks, 'z_verw'] = description.split('PriorityLevel=')[1][0]

        if df_pls_proc_categories.loc[id_proc_categories, 'HISTORIANSUPPORTED']:
            df_ana.loc[kks, 'hist'] = 1
        else:
            df_ana.loc[kks, 'hist'] = 0

    df_ana.loc[kks, 'signum'] = df_svbu_import.loc[kks, 'signum']

    text_plc_itemid = df_plc_ana_conf.loc[kks, 'PLC_ITEMID'].split(':')[-2]
    if '=' not in text_plc_itemid:
        df_ana.loc[kks, 'ITEMID_EXT'] = text_plc_itemid
    # (Department, Channel) оставляем пустыми


async def check_file_for_ana(print_log, name_system: str, name_file_import: str) -> bool:
    """
    Функция проверяет наличие файлов PLS_ANA_CONF.dmp и SVBU_IMPORT.txt|SVSU_IMPORT.txt
    Args:
        print_log: Функция вывода лога
        name_system: Система у которой проверяется наличие файла
        name_file_import: Имя файла импорта
    Returns: bool
    """
    file_check_flag = True

    await print_log(text=f'Проверка наличия файла PLS_ANA_CONF.dmp в {name_system}/DbDumps')
    if path.isfile(path.join(name_system, 'DbDumps', 'PLS_ANA_CONF.dmp')):
        await print_log(text=f'\tTrue', color='green', a_new_line=False)
    else:
        await print_log(text=f'\tFalse', color='red', a_new_line=False)
        file_check_flag = False

    await print_log(text=f'Проверка наличия файла PLS_PROC_CATEGORIES.dmp в {name_system}/DbDumps')
    if path.isfile(path.join(name_system, 'DbDumps', 'PLS_PROC_CATEGORIES.dmp')):
        await print_log(text=f'\tTrue', color='green', a_new_line=False)
    else:
        await print_log(text=f'\tFalse', color='red', a_new_line=False)
        file_check_flag = False

    await print_log(text=f'Проверка наличия файла {name_file_import} в {name_system}/DbSrc')
    if path.isfile(path.join(name_system, 'DbSrc', name_file_import)):
        await print_log(text=f'\tTrue', color='green', a_new_line=False)
    else:
        await print_log(text=f'\tFalse', color='red', a_new_line=False)
        file_check_flag = False
    return file_check_flag


def load_data(file_path):
    df = pd.read_csv(file_path, sep='|', encoding='windows-1251', header=3, skipfooter=1, engine='python')
    return df


async def async_load_data(file_path) -> pd.DataFrame:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        df = await loop.run_in_executor(executor, load_data, file_path)
    return df


async def creating_new_file_nary_conf(print_log, name_system: str, source_system: str, name_file: str,
                                      progress: QProgressBar, start: int = 0, end: int = 100) -> None:
    """
    Функция создает файл с описанием многобитовых сигналов PLS_BIN_NARY_CONF0(1/2).txt на основе исходных данных
    Args:
        print_log: Функция вывода лога
        name_system: Имя системы куда создается файл
        source_system: Система из которой берутся файлы описания сигналов
        name_file: Имя создаваемого файла
        progress: Прогресс выполнения программы
        start: Начальные проценты выполнения программы
        end: Конечные проценты выполнения программы
    Returns: None
    """

    await print_log(text=f'Загрузка SVSU_IMPORT.txt')
    df_svbu_import = pd.read_csv(path.join(source_system, 'DbSrc', 'SVSU_IMPORT.txt'), sep='\t')
    df_svbu_import.set_index('function', drop=False, inplace=True)
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    progress.setValue(percentage_calculation(start=start, end=end, count=6))

    await print_log(text='Загрузка PLS_BIN_CONF.dmp')
    df_plc_bin_conf = await async_load_data(file_path=path.join(source_system, 'DbDumps', 'PLS_BIN_CONF.dmp'))
    df_plc_bin_conf.set_index('PVID', drop=False, inplace=True)
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    progress.setValue(percentage_calculation(start=start, end=end, count=15))

    set_category_nr = set()

    await print_log(text='Составление списка CATEGORYNR (описания многобитовых сигналов передаваемых на SVSU) ')
    list_kks_nary = df_svbu_import.loc[df_svbu_import['type'] == 'N', 'function'].tolist()
    progress.setValue(percentage_calculation(start=start, end=end, count=20))

    number_kks = len(list_kks_nary)
    count = 0
    for i_kks in list_kks_nary:
        set_category_nr.add(int(df_plc_bin_conf.loc[i_kks, 'NARYCATNR']))
        progress.setValue(percentage_calculation(start=percentage_calculation(start=start, end=end, count=20),
                                                 end=percentage_calculation(start=start, end=end, count=75),
                                                 count=count,
                                                 number=number_kks))

    await print_log(text=f'\tSuccessfully.\t Будет добавлено {len(set_category_nr)} описаний',
                    color='green', a_new_line=False)

    await print_log(text='Загрузка PLS_BIN_NARY_CONF.dmp')
    df_pls_bin_nary_conf = await async_load_data(path.join(source_system, 'DbDumps', 'PLS_BIN_NARY_CONF.dmp'))
    df_pls_bin_nary_conf.rename(columns={'*#CATEGORYNR': 'CATEGORYNR'}, inplace=True)
    df_pls_bin_nary_conf.set_index('CATEGORYNR', drop=False, inplace=True)
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    progress.setValue(percentage_calculation(start=start, end=end, count=85))

    await print_log(text=f'Запись файла {name_file}')
    await writing_data_nary_conf_to_a_file(path_file=path.join(name_system, 'Исходники', name_file),
                                           set_category_nr=set_category_nr,
                                           df_pls_bin_nary_conf=df_pls_bin_nary_conf)
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)


async def writing_data_nary_conf_to_a_file(path_file, set_category_nr, df_pls_bin_nary_conf):
    """
    Переписывание нужных строчек из файла PLS_BIN_NARY_CONF для обновления базы SVSU
    """
    list_columns = df_pls_bin_nary_conf.columns.tolist()
    df_data_file = pd.DataFrame(columns=list_columns)
    df_data_file.set_index('CATEGORYNR', drop=False, inplace=True)

    for i in sorted(set_category_nr):
        if i == -1:
            continue
        df_data_file.loc[i] = df_pls_bin_nary_conf.loc[i]

    df_data_file.to_csv(path_file, sep='\t', index=False)


async def creating_new_file_portal_kks(print_log, name_system: str, source_system: str, name_file: str,
                                       progress: QProgressBar, start: int = 0, end: int = 100) -> None:
    """
    Функция создает файл PORTAL_KKS0(1/2).dmp на основе исходных данных для обновления РБД СВСУ
    Args:
        print_log: Функция вывода лога
        name_system: Имя системы куда создается файл
        source_system: Система из которой берутся файлы описания сигналов
        name_file: Имя создаваемого файла
        progress: Прогресс выполнения программы
        start: Начальные проценты выполнения программы
        end: Конечные проценты выполнения программы
    Returns: None
    """
    await print_log(text=f'Загрузка SVSU_IMPORT.txt')
    df_svsu_import = pd.read_csv(path.join(source_system, 'DbSrc', 'SVSU_IMPORT.txt'), sep='\t')
    # df_svsu_import.set_index('function', drop=False, inplace=True)
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    progress.setValue(percentage_calculation(start=start, end=end, count=6))

    await print_log(text=f'Составляется список передаваемых многобитовых сигналов')
    list_kks_nary = df_svsu_import.loc[df_svsu_import['type'] == 'N', 'function'].tolist()
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    progress.setValue(percentage_calculation(start=start, end=end, count=10))

    await print_log(text='Загрузка PORTAL_KKS.dmp')
    df_portal_kks = await async_load_data(file_path=path.join(source_system, 'DbDumps', 'PORTAL_KKS.dmp'))
    df_portal_kks.set_index('*#KKS', drop=False, inplace=True)
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    progress.setValue(percentage_calculation(start=start, end=end, count=10))

    await print_log(text=f'Создание новых данных для файла {name_file}')
    new_df_portal_kks = pd.DataFrame(columns=df_portal_kks.columns.tolist())
    list_index = df_portal_kks.index.tolist()
    path_file = path.join(name_system, 'Исходники', name_file)
    progress.setValue(percentage_calculation(start=start, end=end, count=20))
    for i_kks in list_kks_nary:
        kks = i_kks.split('_')[0]
        if kks in list_index:
            new_df_portal_kks.loc[kks] = df_portal_kks.loc[kks]
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)
    progress.setValue(percentage_calculation(start=start, end=end, count=70))

    await print_log(text=f'Сохранение данных в файл {name_file}')
    with open(path_file, 'w') as new_file_portal_kks:
        new_file_portal_kks.write('*************************************************************************\n'
                                  '* RtDb ASCII PERSISTENCE file of table: PORTAL_KKS\n'
                                  '*************************************************************************\n')
    new_df_portal_kks.to_csv(path_file, mode='a', sep='|', index=False)
    with open(path_file, 'a') as new_file_portal_kks:
        new_file_portal_kks.write('* end of file\n')
    await print_log(text='\tSuccessfully', color='green', a_new_line=False)

    progress.setValue(percentage_calculation(start=start, end=end, count=100))
