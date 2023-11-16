import re
import shutil
from typing import Dict, List, Set
from os import listdir, path, system, rename
from .point_description import AnchorPoint
from .general_functions import (check_directory, database_loading_list_kks_ana_bin_nary, new_data_ana_bin_nary,
                                check_file)

from .timer import timer
from .get_logger import log_info_print


def numbers_bloc() -> str:
    """
    Функция смены работы папки в зависимости от выбранного блока (1 или 2)
    :return: None
    """
    while True:
        number_bloc = input('\nКакой блок(1, 2)([0] - отмена): \n'
                            '  -> ')
        if number_bloc == '1':
            return 'SVBU_1'
        elif number_bloc == '2':
            return 'SVBU_2'
        elif number_bloc == '0' or number_bloc == '':
            return '0'
        else:
            print('Ошибка. Нет такого блока.\n')


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
            new_data_ana_bin_nary(name_system='SVBU_1')
            system('cls')
        elif number_procedure == '2':
            system('cls')
            log_info_print.info(f'Обновление базы данных сигналов SVBU_2')
            new_data_ana_bin_nary(name_system='SVBU_2')
            system('cls')
        elif number_procedure == '3':
            system('cls')
            log_info_print.info(f'Обновление базы данных сигналов SVSU')
            new_data_ana_bin_nary(name_system='SVSU')
            system('cls')
        elif number_procedure == '0' or number_procedure == '':
            break


def start_svsu_import() -> None:
    """Функция подготовки файла SVSU_IMPORT.txt"""
    check_directory(path_directory='SVSU', name_directory='NPP_models')
    list_name_svg_svsu = listdir(path.join('SVSU', 'NPP_models'))

    name_system = numbers_bloc()
    if name_system == '0':
        return

    entered_text = input('Забэкапить старый файл SVSU_IMPORT? (1 - да, 0 - нет)\n [0]-> ')
    if entered_text == '1':
        renaming_old_file_svsu_import(name_system=name_system)

    data_ana, data_bin, data_nary = database_loading_list_kks_ana_bin_nary(name_system=name_system)
    print(f'ANA - {len(data_ana)}')
    print(f'BIN - {len(data_bin)}')
    print(f'NARY - {len(data_nary)}')
    set_ana_signal: Set[str] = set()
    set_bin_signal: Set[str] = set()
    set_nary_signal: Set[str] = set()

    num = 1
    number_name_svg = len(list_name_svg_svsu)
    for name_svg in list_name_svg_svsu:
        print(f'[{num}/{number_name_svg}] Проверка {name_svg}', end='\t')
        num += 1
        if name_svg.endswith('.svg'):
            list_submodel: List[AnchorPoint] = video_frame_parsing(svg=name_svg)
            compiling_list_of_kks(list_submodel=list_submodel,
                                  data_ana=data_ana, data_bin=data_bin, data_nary=data_nary)

            set_ana, set_bin, set_nary = creating_lists_of_found_signals_on_a_video_frame(list_submodel=list_submodel)
            set_ana_signal.update(set_ana)
            set_bin_signal.update(set_bin)
            set_nary_signal.update(set_nary)
    print(f'ANA - {len(set_ana_signal)}')
    print(f'BIN - {len(set_bin_signal)}')
    print(f'NARY - {len(set_nary_signal)}')

    writing_signals_to_a_file(name_system=name_system,
                              set_ana_signal=set_ana_signal,
                              set_bin_signal=set_bin_signal,
                              set_nary_signal=set_nary_signal)
    if check_file(path_directory=name_system, name_file='SVSU_IMPORT_bck.txt'):
        entered_text = input('Завершено успешно.\nEnter для выхода\n 1-Вывести изменения\n 0-Нет \n [0]-> ')
    else:
        input('Завершено успешно.\nEnter для выхода')
        return
    if entered_text == '1':
        file_svsu_import_comparison(name_system=name_system)


def file_svsu_import_comparison(name_system: str):
    """Функция сравнения двух файлов SVSU_IMPORT.txt и SVSU_IMPORT_bck.txt и вывода отчета"""
    list_kks_svsu_import: Set[str] = set()
    list_kks_svsu_import_bck: Set[str] = set()
    with open(path.join(name_system, 'SVSU_IMPORT.txt'), encoding='UTF-8') as file_svsu:
        for i_line in file_svsu:
            list_kks_svsu_import.add(i_line[:-1])
    with open(path.join(name_system, 'SVSU_IMPORT_bck.txt'), encoding='UTF-8') as file_svsu_bck:
        for i_line in file_svsu_bck:
            list_kks_svsu_import_bck.add(i_line[:-1])

    del_kks = list_kks_svsu_import_bck.difference(list_kks_svsu_import)
    add_kks = list_kks_svsu_import.difference(list_kks_svsu_import_bck)

    print(f'Удалены KKS в новом ({len(del_kks)} шт.):')
    num = 1
    for i_kks in sorted(del_kks):
        print(f'{num}. {i_kks}')
        num += 1
    print()

    print(f'Добавлены KKS в новом ({len(add_kks)} шт.):')
    num = 1
    for i_kks in sorted(add_kks):
        print(f'{num}. {i_kks}')
        num += 1
    print()


def renaming_old_file_svsu_import(name_system: str):
    """Функция переименовывает файл SVSU_IMPORT.txt в SVSU_IMPORT_bck.txt"""
    if check_file(path_directory=name_system, name_file='SVSU_IMPORT.txt'):
        rename(path.join(name_system, 'SVSU_IMPORT.txt'), path.join(name_system, 'SVSU_IMPORT_bck.txt'))
        log_info_print.info('Старый файл SVSU_IMPORT.txt переименован в SVSU_IMPORT_bck.txt')
    return


def writing_signals_to_a_file(name_system: str,
                              set_ana_signal: Set[str], set_bin_signal: Set[str], set_nary_signal: Set[str]):
    """Функция записывающая в файл SVSU_import.txt найденные сигналы"""
    with open(path.join(name_system, 'SVSU_IMPORT.txt'), 'w', encoding='utf-8') as file_import:
        file_import.write('signum\ttype\tfunction\tcycle\n')
        for i_kks in sorted(set_ana_signal):
            file_import.write(f'\tA\t{i_kks}\t\n')
        for i_kks in sorted(set_bin_signal):
            file_import.write(f'\tB\t{i_kks}\t\n')
        for i_kks in sorted(set_nary_signal):
            file_import.write(f'\tN\t{i_kks}\t\n')


def creating_lists_of_found_signals_on_a_video_frame(list_submodel: List[AnchorPoint]):
    """Создает 3 множества сигналов найденных на видеокадре аналоговые сигналы, бинарные и много битовые"""
    set_ana = set()
    set_bin = set()
    set_nary = set()
    for i_submodel in list_submodel:
        set_kks_ana, set_kks_bin, set_kks_nary = i_submodel.get_kks_ana_bin_nary()
        set_ana.update(set_kks_ana)
        set_bin.update(set_kks_bin)
        set_nary.update(set_kks_nary)
    return set_ana, set_bin, set_nary


def compiling_list_of_kks(list_submodel: List[AnchorPoint],
                          data_ana: Set[str], data_bin: Set[str], data_nary: Set[str]):
    """Проверяет существование найденных KKS в базе данных"""
    for i_submodel in list_submodel:
        i_submodel.check_existence_database(data_ana=data_ana,
                                            data_bin=data_bin,
                                            data_nary=data_nary,
                                            set_suffix={'XH01', 'XH41', 'XH52', 'XH92'})


@timer
def video_frame_parsing(svg: str) -> List[AnchorPoint]:
    """
    Функция принимающая KKS видеокадра на котором построчно ведется поиск начала кода подмодели. При нахождении кода,
    записывает его построчно в список list_constructor и запускает функцию add_kks с аргументом list_constructor.
    :param svg: Имя видеокадра формата svg.
    :return: Список найденных подмоделей.
    """
    with open(path.join('SVSU', 'NPP_models', svg), 'r', encoding='windows-1251') as svg_file:
        list_submodel = creating_list_of_submodel(svg_file=svg_file, name_svg=svg)
    return list_submodel


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


@timer
def start_bloc_button() -> None:
    """
    Функция берущая из папки NPP_models видеокадры и запускает функцию bloc_button в которую передает по
    оному видеокадру.
    :return: None
    """
    set_vis = set(listdir(path.join('SVSU', 'NPP_models')))
    set_kks_vis_npp_models = set()
    for i_vis in set_vis:
        if i_vis.endswith('.svg'):
            set_kks_vis_npp_models.add(i_vis[:-4])

    num = 1
    len_num = len(set_vis)
    for i_svg in sorted(set_vis):
        if i_svg.endswith('.svg'):

            print(f'[{num}/{len_num}] Проверка {i_svg}', end='\t')
            bloc_button(svg=i_svg, set_kks_name_svg=set_kks_vis_npp_models)
            num += 1
        else:
            print(f'[{num}/{len_num}] Файл {i_svg} не является svg')
            num += 1
    log_info_print.info(f'Кнопки успешно заблокированы')
    input('Enter для продолжения')


def bloc_button(svg: str, set_kks_name_svg: Set[str]) -> None:
    """
    Функция проверяющая видеокадр и анализирует есть ли вызываемые видеокадры в папке bloc_button. Если вызываемого
    видеокадра нет, добавляет строку, которая делает неактивной кнопку вызова.
    :param svg: Название файла видеокадра.
    :param set_kks_name_svg: Список все имеющихся видеокадров на которые может быть ссылка
    :return: None
    """
    with open(path.join('SVSU', 'NPP_models', svg), 'r', encoding='windows-1251') as file_svg, \
         open(path.join('SVSU', 'new_NPP_models_SVSU', svg), 'w', encoding='windows-1251') as new_file_svg:

        flag_button = False

        for i_line in file_svg:
            if '<rt:dyn type="Disable" mode="constant" value="true"/>' in i_line:
                continue
            if flag_button:
                if 'type="OnClick">LoadNew' in i_line:
                    new_file_svg.write(i_line)

                    try:
                        result = re.findall(r'&quot;(.*)&quot;', i_line)[0]
                    except IndexError:
                        try:
                            result = re.findall(r'\("(\d0.*\d+)"\)</', i_line)[0]
                        except IndexError:
                            result = '0'

                    if result not in set_kks_name_svg or result != '0':
                        new_file_svg.write(f'    <rt:dyn type="Disable" mode="constant" value="true"/>\n')
                    flag_button = False
                else:
                    new_file_svg.write(i_line)
            else:
                if re.search(r'obj_Button.svg', i_line) or re.search(r'obj_Station_stat.svg', i_line):
                    flag_button = True
                new_file_svg.write(i_line)
    print('завершено')


def actualizations_vk_svbu() -> None:
    """Функция обновления видеокадров в папке SVBU_(1/2)/NPP_models из папки SVBU_(1/2)/NPP_models_new"""
    bloc = numbers_bloc()
    if bloc == '0':
        return
    set_vis: Set[str] = set(listdir(path.join(bloc, 'NPP_models')))
    set_vis_new: Set[str] = set(listdir(path.join(bloc, 'NPP_models_new')))
    numbers_vis = len(set_vis)
    number = 1
    for i_vis in set_vis:
        if i_vis in set_vis_new:
            shutil.copy2(path.join(bloc, 'NPP_models_new', i_vis), path.join(bloc, 'NPP_models', i_vis))
            print(f'[{number}/{numbers_vis}]   +++{i_vis} видеокадр обновлен+++')
        else:
            print(f'[{number}/{numbers_vis}]   ---Видеокадра {i_vis} нет в {bloc}/NPP_models_new ---')
        number += 1

    log_info_print.info(f'Видеокадры обновлены успешно')
    input('Enter для продолжения')


@timer
def actualizations_vk() -> None:
    bloc = numbers_bloc()
    if bloc == 'SVBU_1':
        number = '1'
    elif bloc == 'SVBU_2':
        number = '2'
    else:
        return
    kks_dict_new: Dict[str, str] = {'MKA01': f'{number}0MKA01',
                                    'MKA02': f'{number}0MKA02',
                                    'MKA03': f'{number}0MKA03',
                                    'mkc': f'{number}0mkc',
                                    'ALL_STKTG': f'{number}0ALL_STKTG',
                                    'AKNP_RD2': f'{number}0AKNP_RD2'}

    renaming_kks: Dict[str, str] = {f'{number}0ALL_STKTG.svg': 'ALL_STKTG.svg',
                                    f'{number}0MKA01.svg': 'MKA01.svg',
                                    f'{number}0MKA02.svg': 'MKA02.svg',
                                    f'{number}0MKA03.svg': 'MKA03.svg',
                                    f'{number}0mkc.svg': 'mkc.svg',
                                    f'{number}0AKNP_RD2.svg': 'AKNP_RD2.svg'}

    set_vis: Set[str] = set(listdir(path.join('SVSU', 'NPP_models')))
    set_vis.discard('diag_PPD.svg')

    set_vis_bloc: Set[str] = set(listdir(path.join(bloc, 'NPP_models')))
    print()

    num = 1
    for i_vis in sorted(set_vis):
        if i_vis == '10MKA03.svg':
            pass
        print(num, end='. ')
        num += 1
        if i_vis in renaming_kks:
            # тут пойдет замена файла
            with open(path.join(bloc, 'NPP_models', renaming_kks[i_vis]), 'r', encoding='windows-1251') as file, \
                    open(path.join('SVSU', 'NPP_models', i_vis), 'w', encoding='windows-1251') as new_file:
                for i_line in file:
                    for vis in kks_dict_new:
                        if f'&quot;{vis}' in i_line:
                            result = re.split(fr'{vis}', i_line)
                            result = f'{result[0]}{kks_dict_new[vis]}{result[1]}'
                            new_file.write(result)
                            break
                    else:
                        new_file.write(i_line)
            print(f'+++{i_vis} видеокадр обновлен+++')

        elif i_vis in set_vis_bloc:
            # тут пойдет замена файла
            with open(path.join(bloc, 'NPP_models', i_vis), 'r', encoding='windows-1251') as file, \
                    open(path.join('SVSU', 'NPP_models', i_vis), 'w', encoding='windows-1251') as new_file:
                for i_line in file:
                    for vis in kks_dict_new:
                        if f'&quot;{vis}' in i_line:
                            result = re.split(fr'{vis}', i_line)
                            result = f'{result[0]}{kks_dict_new[vis]}{result[1]}'
                            new_file.write(result)
                            break
                    else:
                        new_file.write(i_line)
            print(f'+++{i_vis} видеокадр обновлен+++')
        else:
            print(f'Видеокадра {i_vis} нет в папке {bloc}\\NPP_models')
    log_info_print.info(f'Видеокадры обновлены успешно')
    input('Enter для продолжения')


def start_program_svsu_import() -> None:
    while True:
        number_procedure = input('Программа создания файла SVSU_import и обновления ВК SVSU\n'
                                 '1.  Обновить видеокадры SVBU\n'
                                 '2.  Обновить видеокадры SVSU из самых актуальных видеокадров SVBU\n'
                                 '3.  Сделать неактивными кнопки на кадрах с несуществующими ссылками\n'
                                 '4.  Обновление баз данных сигналов\n'
                                 '5.  Создать файл SVSU_IMPORT.txt\n'
                                 '[0].  Выход\n'
                                 '  -> ')
        if number_procedure == '1':
            system('cls')
            log_info_print.info(f'Старт программы обновления видеокадров SVBU')
            actualizations_vk_svbu()
            system('cls')
        if number_procedure == '2':
            system('cls')
            log_info_print.info(f'Старт программы обновления видеокадров SVSU из самых актуальных видеокадров SVBU')
            actualizations_vk()
            system('cls')
        elif number_procedure == '3':
            system('cls')
            log_info_print.info(f'Старт программы блокировки неактивных кнопок вызова')
            start_bloc_button()
            system('cls')
        elif number_procedure == '4':
            system('cls')
            log_info_print.info(f'Обновление базы данных сигналов')
            update_signal_database()
            system('cls')
        elif number_procedure == '5':
            system('cls')
            start_svsu_import()
            system('cls')
        elif number_procedure == '0' or number_procedure == '':
            log_info_print.info(f'Выход из программы создания файла SVSU_import и обновления ВК SVSU')
            return


if __name__ == '__main__':
    pass
