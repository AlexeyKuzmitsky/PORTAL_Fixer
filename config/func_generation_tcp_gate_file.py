from config.general_functions import (check_directory, loading_data_kks_ana, loading_data_kks_bin,
                                      loading_data_kks_nary, creating_list_of_submodel)
from os import path, listdir
from typing import Set, List, Dict
from config.point_description import AnchorPoint

import json


async def generation_tcp_gate(name_system, print_log):
    """Генерирует файл TcpGateConf для ZPUPD"""
    # создание базы сигналов соответствующей системы
    data_ana = await loading_data_kks_ana(directory=name_system)
    data_bin = await loading_data_kks_bin(directory=name_system)
    data_nary = await loading_data_kks_nary(directory=name_system)

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

    # добавляем список видеокадров от цеха связи если есть
    list_name_txt = listdir(path.join(name_system, 'data', 'TcpGate'))

    number_name_svg = len(list_name_svg) + len(list_name_txt)
    num = 0
    for name_svg in list_name_svg + list_name_txt:
        num += 1
        text_log = f'[{num}/{number_name_svg}] Проверка {name_svg}'

        if name_svg in list_name_svg_system:
            list_submodel: List[AnchorPoint] = await creating_list_of_submodel(name_system=name_system,
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
    file_description_nary_signal(set_bin=set_bin_signal, name_system=name_system)


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
    with open(path.join(name_system, 'data', 'list_kks_svg_TcpGate.txt'), 'r', encoding='UTF') as file_list_name_svg:
        for i_line in file_list_name_svg:
            if i_line.endswith('\n'):

                list_name_svg.append(f'{i_line[:-1]}.svg')
            else:
                list_name_svg.append(f'{i_line}.svg')
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


def file_description_nary_signal(set_bin: Set[str], name_system: str, name_file: str = 'description_nary_signal.json'):
    """Запись описания сигналов NARY в JSON файл"""
    with open(path.join(name_system, 'data', 'BIN_NARY_kks.json'), 'r', encoding='UTF-8') as file_description:
        dict_nary_signal = json.load(file_description)
    dict_nary_signal_to_file: Dict[str, Dict[str, str]] = dict()
    for i_kks in set_bin:
        if i_kks in dict_nary_signal:
            if dict_nary_signal[i_kks]:
                dict_nary_signal_to_file[i_kks] = dict_nary_signal[i_kks]

    with open(path.join(name_system, 'TcpGate', name_file), 'w', encoding='UTF-8') as json_file:
        json.dump(dict_nary_signal_to_file, json_file, indent=2, ensure_ascii=False)
