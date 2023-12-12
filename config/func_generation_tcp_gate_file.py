from config.general_functions import (check_directory, loading_data_kks_ana, loading_data_kks_bin,
                                      loading_data_kks_nary, creating_list_of_submodel)
from os import path, listdir
from typing import Set, List, Dict
from config.point_description import AnchorPoint
from csv import reader
from PyQt6.QtWidgets import QProgressBar

import json


async def generation_tcp_gate(name_system, print_log):
    """Генерирует файл TcpGateConf для ZPUPD"""
    # создание базы сигналов соответствующей системы
    data_ana = await loading_data_kks_ana(directory=name_system)
    if not data_ana:
        await print_log(f'Нет файла ANA_list_kks.txt в {name_system}\\data.\n'
                        f'Создание файла ZPUPD невозможно. \n'
                        f'Для продолжения выполните пункт "обновления баз данных" для {name_system}\n', color='red')
        return False

    data_bin = await loading_data_kks_bin(directory=name_system)
    if not data_bin:
        await print_log(f'Нет файла BIN_list_kks.txt в {name_system}\\data.\n'
                        f'Создание файла ZPUPD невозможно. \n'
                        f'Для продолжения выполните пункт "обновления баз данных" для {name_system}\n', color='red')
        return False

    data_nary = await loading_data_kks_nary(directory=name_system)
    if not data_nary:
        await print_log(f'Нет файла NARY_list_kks.txt в {name_system}\\data.\n'
                        f'Создание файла ZPUPD невозможно. \n'
                        f'Для продолжения выполните пункт "обновления баз данных" для {name_system}\n', color='red')
        return False

    check_directory(path_directory=name_system, name_directory='TcpGate')
    check_directory(path_directory=path.join(name_system, 'data'), name_directory='TcpGate')
    if name_system == 'SVSU':
        await removing_redundant_signals(data_ana=data_ana, data_bin=data_bin, data_nary=data_nary)
        list_name_svg_system = listdir(path.join(name_system, 'NPP_models'))
    else:
        list_name_svg_system = listdir(path.join(name_system, 'NPP_models')) + listdir(path.join('SVSU', 'NPP_models'))

    set_ana_signal: Set[str] = set()
    set_bin_signal: Set[str] = set()

    # создаем список проверяемых svg файлов
    list_name_svg: List[str] = await preparing_list_of_video_frames(name_system=name_system)
    if not list_name_svg:
        await print_log(f'Нет файла list_kks_svg_TcpGate.txt в {name_system}\\data.\n'
                        f'Создание файла ZPUPD невозможно. \n'
                        f'Для продолжения поместите файл list_kks_svg_TcpGate.txt в {name_system}\\data\n', color='red')
        return False

    # добавляем список видеокадров от цеха связи если есть
    list_name_txt = listdir(path.join(name_system, 'data', 'TcpGate'))

    number_name_svg = len(list_name_svg) + len(list_name_txt)
    num = 0
    for name_svg in list_name_svg + list_name_txt:
        num += 1
        text_log = f'[{num}/{number_name_svg}] Проверка {name_svg}'

        if name_svg in list_name_svg_system:
            try:
                list_submodel: List[AnchorPoint] = await creating_list_of_submodel(name_system=name_system,
                                                                                   name_svg=name_svg)
            except FileNotFoundError:
                list_submodel: List[AnchorPoint] = await creating_list_of_submodel(name_system='SVSU',
                                                                                   name_svg=name_svg)
        elif name_svg.endswith('.txt'):
            list_submodel: List[AnchorPoint] = txt_file_parsing(name_txt_file=name_svg, name_system=name_system)
        else:
            if name_svg not in list_name_svg_system:
                await print_log(text=f'{text_log} Файла {name_svg} нет в {name_system}\\NPP_models и SVSU\\NPP_models',
                                color='red')
            if not name_svg.endswith('.svg'):
                await print_log(text=f'{text_log} Найден файл {name_svg} не являющийся svg файлом', color='red')
            continue
        await print_log(text=text_log)

        compiling_list_of_kks(list_submodel=list_submodel, data_ana=data_ana, data_bin=data_bin, data_nary=data_nary)
        set_ana, set_bin = creating_lists_of_found_signals_on_a_video_frame(list_submodel=list_submodel)

        if len(set_ana) or len(set_bin):
            recording_signals_to_a_video_frame_file(svg=name_svg, name_system=name_system,
                                                    set_ana=set_ana, set_bin=set_bin)
        set_ana_signal.update(set_ana)
        set_bin_signal.update(set_bin)

    if name_system == 'SVSU':
        file_creation(set_ana=set_ana_signal, set_bin=set_bin_signal, name_system=name_system, name_file='ZPUPDG.cfg')
        file_creation(set_ana=set_ana_signal, set_bin=set_bin_signal, name_system=name_system, name_file='ZPUPDAS.cfg')
    else:
        file_creation(set_ana=set_ana_signal, set_bin=set_bin_signal, name_system=name_system)
    if not file_description_nary_signal(set_bin=set_bin_signal, name_system=name_system):
        await print_log(f'Нет файла BIN_NARY_kks.json в {name_system}\\data.\n'
                        f'Создание файла description_nary_signal.json  с описанием многобитовых сигналов невозможно.\n'
                        f'Для создания данного файла, выполните пункт "обновления баз данных" для {name_system}\n',
                        color='red')
    return True


async def removing_redundant_signals(data_ana: Set[str], data_bin: Set[str], data_nary: Set[str]):
    """Функция удаляет из списка СВСУ сигналов те, которые уже имеются в базе блоков"""
    ana_signal_svbu1 = await loading_data_kks_ana(directory='SVBU_1')
    bin_signal_svbu1 = await loading_data_kks_bin(directory='SVBU_1')
    nary_signal_svbu1 = await loading_data_kks_nary(directory='SVBU_1')

    ana_signal_svbu2 = await loading_data_kks_ana(directory='SVBU_2')
    bin_signal_svbu2 = await loading_data_kks_bin(directory='SVBU_2')
    nary_signal_svbu2 = await loading_data_kks_nary(directory='SVBU_2')

    data_ana.difference_update(ana_signal_svbu1)  # удаляем ANA сигналы СВБУ_1
    data_ana.difference_update(ana_signal_svbu2)  # удаляем ANA сигналы СВБУ_2

    data_bin.difference_update(bin_signal_svbu1)  # удаляем BIN сигналы СВБУ_1
    data_bin.difference_update(bin_signal_svbu2)  # удаляем BIN сигналы СВБУ_2

    data_nary.difference_update(nary_signal_svbu1)  # удаляем NARY сигналы СВБУ_1
    data_nary.difference_update(nary_signal_svbu2)  # удаляем NARY сигналы СВБУ_2


async def preparing_list_of_video_frames(name_system: str) -> List[str]:
    """Подготовка списка видеокадров из файла list_kks_svg_TcpGate.txt"""
    list_name_svg: List[str] = list()
    try:
        with open(path.join(name_system, 'data', 'list_kks_svg_TcpGate.txt'), 'r',
                  encoding='UTF-8') as file_list_name_svg:
            for i_line in file_list_name_svg:
                if i_line.endswith('\n'):

                    list_name_svg.append(f'{i_line[:-1]}.svg')
                else:
                    list_name_svg.append(f'{i_line}.svg')
    except FileNotFoundError:
        pass
    return list_name_svg


def txt_file_parsing(name_txt_file: str, name_system: str) -> List[AnchorPoint]:
    """Создаем список точек из текстового файла со списком KKS"""
    list_submodel: List[AnchorPoint] = list()
    with open(path.join(name_system, 'data', 'TcpGate', name_txt_file), 'r', encoding='windows-1251') as txt_file:
        for i_line in txt_file:
            if i_line.endswith('\n'):
                kks = i_line[:-1]
            else:
                kks = i_line
            if kks:
                point = AnchorPoint(full_description_of_the_submodel=list())
                point.set_signal_description({'KKS': kks})
                list_submodel.append(point)
    return list_submodel


def compiling_list_of_kks(list_submodel: List[AnchorPoint],
                          data_ana: Set[str], data_bin: Set[str], data_nary: Set[str]):
    """Проверяет существование найденных KKS в базе данных"""
    for i_submodel in list_submodel:
        i_submodel.check_existence_database(data_ana=data_ana, data_bin=data_bin, data_nary=data_nary)


def creating_lists_of_found_signals_on_a_video_frame(list_submodel: List[AnchorPoint]):
    """Создает 2 множества сигналов найденных на видеокадре аналоговые сигналы и бинарные"""
    set_ana = set()
    set_bin = set()
    for i_submodel in list_submodel:
        set_kks_ana, set_kks_bin = i_submodel.get_kks_ana_bin()
        set_ana.update(set_kks_ana)
        set_bin.update(set_kks_bin)
    return set_ana, set_bin


def recording_signals_to_a_video_frame_file(svg: str, name_system: str, set_ana: Set[str], set_bin: Set[str]):
    """Запись аналоговых и бинарных сигналов в файл"""
    with open(path.join(name_system, 'TcpGate', f'{svg[:-4]}.txt'), 'w', encoding='UTF-8') as file:
        if len(set_ana):
            file.write('#IA1000\n')
            for i_kks in set_ana:
                file.write(f'{i_kks}\n')
            file.write('#\n')
        if len(set_bin):
            file.write('#ID1000\n')
            for i_kks in set_bin:
                file.write(f'{i_kks}\n')
            file.write('#\n')


def file_creation(set_ana, set_bin, name_system, name_file: str = 'ZPUPD.cfg'):
    """Запись всех найденных сигналов в файл"""
    with open(path.join(name_system, 'TcpGate', name_file), 'w', encoding='UTF') as file_zpupd:
        file_zpupd.write('#IA1000\n')
        for i_kks in sorted(set_ana):
            file_zpupd.write(f'{i_kks}\n')
        file_zpupd.write('#\n#ID1000\n')
        for i_kks in sorted(set_bin):
            file_zpupd.write(f'{i_kks}\n')
        file_zpupd.write('#\n')


def file_description_nary_signal(set_bin: Set[str], name_system: str,
                                 name_file: str = 'description_nary_signal.json') -> bool:
    """Запись описания сигналов NARY в JSON файл"""
    try:
        with open(path.join(name_system, 'data', 'BIN_NARY_kks.json'), 'r', encoding='UTF-8') as file_description:
            dict_nary_signal = json.load(file_description)
    except FileNotFoundError:
        return False
    dict_nary_signal_to_file: Dict[str, Dict[str, str]] = dict()
    for i_kks in set_bin:
        if i_kks in dict_nary_signal:
            if dict_nary_signal[i_kks]:
                dict_nary_signal_to_file[i_kks] = dict_nary_signal[i_kks]

    with open(path.join(name_system, 'TcpGate', name_file), 'w', encoding='UTF-8') as json_file:
        json.dump(dict_nary_signal_to_file, json_file, indent=2, ensure_ascii=False)
    return True


async def add_data_file_bin_nary(print_log, name_system: str,
                                 progress: QProgressBar, min_progress: int=50, max_progress: int=100):
    """Функция создает файл BIN_NARY_kks.json"""
    check_directory(path_directory=name_system, name_directory='DbDumps')
    check_directory(path_directory=name_system, name_directory='data')
    dict_kks_bin_data: Dict = dict()

    print_log('Сбор описания сигналов NARY')
    progress.setValue(round((max_progress - min_progress) * 15 / 100 + min_progress))
    try:
        dict_description: Dict[int, Dict[str, str]] = add_list_description(name_system=name_system)
    except FileNotFoundError:
        print_log('INFO Создание файла BIN_NARY_kks.json невозможно. '
                  f'Нет файла PLS_BIN_NARY_CONF.dmp в папке {name_system}\\DbDumps\n', color='red')
        return
    progress.setValue(round((max_progress - min_progress) * 45 / 100 + min_progress))
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
            except KeyError:
                ...
    progress.setValue(round((max_progress - min_progress) * 65 / 100 + min_progress))
    with open(path.join(name_system, 'data', 'BIN_NARY_kks.json'), 'w', encoding='UTF-8') as json_file:
        json.dump(dict_kks_bin_data, json_file, indent=2, ensure_ascii=False)
    print_log('Описания сигналов NARY собраны\n', color='green')
    progress.setValue(round((max_progress - min_progress) + min_progress))


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