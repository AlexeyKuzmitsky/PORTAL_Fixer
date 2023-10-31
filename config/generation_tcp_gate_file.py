import json
from typing import List, Set, Dict
from .point_description import AnchorPoint
from os import path, system, listdir
from .get_logger import log_info_print
from .timer import timer
from .general_functions import database_loading_list_kks_ana_bin_nary, check_directory, new_data_ana_bin_nary, \
    add_data_file_bin_nary


def creating_list_of_submodel(svg_file, name_svg: str) -> List[AnchorPoint]:
    """
    Функция составляющая список подмоделей на видеокадре.
    :param svg_file: Файл svg проверяемого видеокадра.
    :param name_svg: Название svg файла.
    :return: Список найденных подмоделей.
    """
    list_submodel: List[AnchorPoint] = list()
    list_constructor: List[str] = list()
    flag_constructor = False

    for i_line in svg_file:
        if flag_constructor:
            if '</image>' in i_line:
                list_constructor.append(i_line)
                new_submodel(list_constructor=list_constructor,
                             list_submodel=list_submodel,
                             name_svg=name_svg)
                flag_constructor = False
                list_constructor.clear()
            else:
                list_constructor.append(i_line)
        else:
            if '<image' in i_line and '</image>' in i_line or '<image' in i_line and '/>' in i_line:
                list_constructor.append(i_line)
                new_submodel(list_constructor=list_constructor,
                             list_submodel=list_submodel,
                             name_svg=name_svg)
                list_constructor.clear()
            elif '<image' in i_line:
                flag_constructor = True
                list_constructor.clear()
                list_constructor.append(i_line)
    return list_submodel


def new_submodel(list_constructor, list_submodel, name_svg: str) -> None:
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
        submodel.search_kks_on_submodel()
        list_submodel.append(submodel)


def update_signal_database() -> None:
    """Выбор системы в которой будет обновление базы данных сигналов"""
    while True:
        number_procedure = input('Где обновить базы данных сигналов\n'
                                 '1. СВБУ_1\n'
                                 '2. СВБУ_2\n'
                                 '3. СВСУ\n'
                                 '[0].  Выход\n'
                                 '  -> ')
        if number_procedure == '1':
            system('cls')
            log_info_print.info(f'Обновление базы данных сигналов SVBU_1')
            add_data_file_bin_nary(name_system='SVBU_1')
            new_data_ana_bin_nary(name_system='SVBU_1')
            system('cls')
        elif number_procedure == '2':
            system('cls')
            log_info_print.info(f'Обновление базы данных сигналов SVBU_2')
            add_data_file_bin_nary(name_system='SVBU_2')
            new_data_ana_bin_nary(name_system='SVBU_2')
            system('cls')
        elif number_procedure == '3':
            system('cls')
            log_info_print.info(f'Обновление базы данных сигналов SVSU')
            add_data_file_bin_nary(name_system='SVSU')
            new_data_ana_bin_nary(name_system='SVSU')
            system('cls')
        elif number_procedure == '0' or number_procedure == '':
            log_info_print.info(f'Выход из программы создания файла ZPUPD.CFG')
            break


def start_program_generation_tcp_gate() -> None:
    """Запускает программу генерации файла TcpGateConf для ZPUPD"""
    while True:
        number_procedure = input('Программа создания файла ZPUPD.cfg для TcpGate\n'
                                 '1. Обновить базу данных сигналов\n'
                                 '2. Создание файла ZPUPD.cfg\n'
                                 '[0].  Выход\n'
                                 '  -> ')
        if number_procedure == '1':
            system('cls')
            log_info_print.info(f'Обновление базы данных сигналов')
            update_signal_database()
            system('cls')
        elif number_procedure == '2':
            system('cls')
            log_info_print.info(f'Старт программы создания файла ZPUPD.CFG')
            program_generation_tcp_gate()
            system('cls')
        elif number_procedure == '0' or number_procedure == '':
            log_info_print.info(f'Выход из программы создания файла ZPUPD.CFG')
            break


def program_generation_tcp_gate() -> None:
    """Выбор системы для которой будет создан файл ZPUPD.CFG"""
    # add_data_file_bin_nary(name_system='SVBU_1')
    while True:
        number_procedure = input('Программа создания файла ZPUPD.CFG для TcpGate\n'
                                 '1. СВБУ_1\n'
                                 '2. СВБУ_2\n'
                                 '3. СВСУ\n'
                                 '[0].  Выход\n'
                                 '  -> ')
        if number_procedure == '1':
            system('cls')
            log_info_print.info(f'Старт программы создания файла ZPUPD.CFG для 1-го блока.')
            generation_tcp_gate(name_system='SVBU_1')
            system('cls')
        elif number_procedure == '2':
            system('cls')
            log_info_print.info(f'Старт программы создания файла ZPUPD.CFG для 2-го блока.')
            generation_tcp_gate(name_system='SVBU_2')
            system('cls')
        elif number_procedure == '3':
            system('cls')
            log_info_print.info(f'Старт программы создания файла ZPUPD.CFG для СВСУ.')
            generation_tcp_gate(name_system='SVSU')
            system('cls')
        elif number_procedure == '0' or number_procedure == '':
            log_info_print.info(f'Выход из программы создания файла ZPUPD.CFG')
            break


def generation_tcp_gate(name_system):
    """Генерирует файл TcpGateConf для ZPUPD"""
    # создание базы сигналов соответствующей системы
    data_ana, data_bin, data_nary = database_loading_list_kks_ana_bin_nary(name_system=name_system)

    check_directory(path_directory=name_system, name_directory='TcpGate')
    check_directory(path_directory=path.join(name_system, 'data'), name_directory='TcpGate')
    if name_system == 'SVSU':
        removing_redundant_signals(data_ana=data_ana, data_bin=data_bin, data_nary=data_nary)
        list_name_svg_system = listdir(path.join(name_system, 'NPP_models'))
    else:
        list_name_svg_system = listdir(path.join(name_system, 'NPP_models')) + listdir(path.join('SVSU', 'NPP_models'))

    set_ana_signal: Set[str] = set()
    set_bin_signal: Set[str] = set()

    # создаем список проверяемых svg файлов
    list_name_svg: List[str] = preparing_list_of_video_frames(name_system=name_system)

    # добавляем список видеокадров от цеха связи если есть
    list_name_txt = listdir(path.join(name_system, 'data', 'TcpGate'))

    number_name_svg = len(list_name_svg) + len(list_name_txt)
    num = 0
    for name_svg in list_name_svg + list_name_txt:
        num += 1
        print(f'[{num}/{number_name_svg}] Проверка {name_svg}', end='\t')
        if name_svg in list_name_svg_system:
            list_submodel: List[AnchorPoint] = video_frame_parsing(svg=name_svg, name_system=name_system)
        elif name_svg.endswith('.txt'):
            list_submodel: List[AnchorPoint] = txt_file_parsing(name_txt_file=name_svg, name_system=name_system)
        else:
            if name_svg not in list_name_svg_system:
                print(f'Файла {name_svg} нет в {name_system}\\NPP_models и SVSU\\NPP_models')
            if not name_svg.endswith('.svg'):
                print(f'Найден файл {name_svg} не являющийся svg файлом')
            continue

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
    input('Программа выполнена успешно\n'
          'Enter...')


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


def removing_redundant_signals(data_ana: Set[str], data_bin: Set[str], data_nary: Set[str]):
    """Функция удаляет из списка СВСУ сигналов те, которые уже имеются в базе блоков"""
    ana_signal_svbu1, bin_signal_svbu1, nary_signal_svbu1 = database_loading_list_kks_ana_bin_nary(name_system='SVBU_1')
    ana_signal_svbu2, bin_signal_svbu2, nary_signal_svbu2 = database_loading_list_kks_ana_bin_nary(name_system='SVBU_2')

    data_ana.difference_update(ana_signal_svbu1)  # удаляем ANA сигналы СВБУ_1
    data_ana.difference_update(ana_signal_svbu2)  # удаляем ANA сигналы СВБУ_2

    data_bin.difference_update(bin_signal_svbu1)  # удаляем BIN сигналы СВБУ_1
    data_bin.difference_update(bin_signal_svbu2)  # удаляем BIN сигналы СВБУ_2

    data_nary.difference_update(nary_signal_svbu1)  # удаляем NARY сигналы СВБУ_1
    data_nary.difference_update(nary_signal_svbu2)  # удаляем NARY сигналы СВБУ_2


def preparing_list_of_video_frames(name_system: str) -> List[str]:
    """Подготовка списка видеокадров из файла list_kks_svg_TcpGate.txt"""
    list_name_svg: List[str] = list()
    with open(path.join(name_system, 'data', 'list_kks_svg_TcpGate.txt'), 'r', encoding='UTF') as file_list_name_svg:
        for i_line in file_list_name_svg:
            if i_line.endswith('\n'):

                list_name_svg.append(f'{i_line[:-1]}.svg')
            else:
                list_name_svg.append(f'{i_line}.svg')
    return list_name_svg


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


def creating_lists_of_found_signals_on_a_video_frame(list_submodel: List[AnchorPoint]):
    """Создает 2 множества сигналов найденных на видеокадре аналоговые сигналы и бинарные"""
    set_ana = set()
    set_bin = set()
    for i_submodel in list_submodel:
        set_kks_ana, set_kks_bin = i_submodel.get_kks_ana_bin()
        set_ana.update(set_kks_ana)
        set_bin.update(set_kks_bin)
    return set_ana, set_bin


def compiling_list_of_kks(list_submodel: List[AnchorPoint],
                          data_ana: Set[str], data_bin: Set[str], data_nary: Set[str]):
    """Проверяет существование найденных KKS в базе данных"""
    for i_submodel in list_submodel:
        i_submodel.check_existence_database(data_ana=data_ana, data_bin=data_bin, data_nary=data_nary)


@timer
def video_frame_parsing(svg: str, name_system: str) -> List[AnchorPoint]:
    """
    Функция принимающая KKS видеокадра на котором построчно ведется поиск начала кода подмодели. При нахождении кода,
    записывает его построчно в список list_constructor и запускает функцию add_kks с аргументом list_constructor.
    :param svg: Имя видеокадра формата svg.
    :param name_system: Имя папки системы для которой подготавливается паспорт.
    :return: Список найденных подмоделей.
    """
    try:
        with open(path.join(name_system, 'NPP_models', svg), 'r', encoding='windows-1251') as svg_file:
            list_submodel = creating_list_of_submodel(svg_file=svg_file, name_svg=svg)
    except FileNotFoundError:
        with open(path.join('SVSU', 'NPP_models', svg), 'r', encoding='windows-1251') as svg_file:
            list_submodel = creating_list_of_submodel(svg_file=svg_file, name_svg=svg)
    return list_submodel


@timer
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
