from config.point_description import AnchorPoint
from typing import List, Set, Dict
from os import path, listdir, remove, rename
from config.general_functions import (check_file, loading_data_kks_ana, loading_data_kks_bin, loading_data_kks_nary,
                                      creating_list_of_submodel, check_directory)
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QProgressBar

import re


async def actualizations_vk_svsu(print_log, name_directory: str, progress: QProgressBar) -> None:
    """Функция обновления видеокадров в папке SVSU/NPP_models из папки SVBU_(1/2)/NPP_models"""
    if name_directory == 'SVBU_1':
        number = '1'
    elif name_directory == 'SVBU_2':
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
    set_vis_bloc: Set[str] = set(listdir(path.join(name_directory, 'NPP_models')))
    num = 1
    numbers_vis = len(set_vis)

    for i_vis in sorted(set_vis):
        await print_log(text=f'[{num}/{numbers_vis}]\tобновление {i_vis}')
        progress.setValue(round(num / numbers_vis * 100))
        if i_vis in renaming_kks:
            await overwriting_a_file(number=number, name_svg=renaming_kks[i_vis], name_svg_new=i_vis,
                                     name_system=name_directory, kks_dict_new=kks_dict_new)
            await print_log(text='\t+++обновлен+++', color='green', a_new_line=False)
        elif i_vis in set_vis_bloc:
            await overwriting_a_file(number=number, name_svg=i_vis, name_svg_new=i_vis,
                                     name_system=name_directory, kks_dict_new=kks_dict_new)
            await print_log(text='\t+++обновлен+++', color='green', a_new_line=False)
        else:
            await print_log(text=f'\t---Видеокадра нет в папке {name_directory}\\NPP_models---',
                            color='red', a_new_line=False)
        num += 1


async def overwriting_a_file(number: str, name_svg: str, name_svg_new: str, name_system: str,
                             kks_dict_new: Dict[str, str]):
    """
    Функция переписывающая файл с заменой текста в ссылках на нужный блок
    :param number: Номер блока.
    :param name_svg: Имя начального видеокадра.
    :param name_svg_new: Новое имя видеокадра (обычно одно и тоже).
    :param name_system: Имя директории (SVBU_1 или SVBU_2).
    :param kks_dict_new: Словарь замен названий видеокадров.
    :return: None.
    """
    with open(path.join(name_system, 'NPP_models', name_svg), 'r', encoding='windows-1251') as file, \
            open(path.join('SVSU', 'NPP_models', name_svg_new), 'w', encoding='windows-1251') as new_file:
        for i_line in file:
            for vis in kks_dict_new:
                if f'{vis}' in i_line and not f'{number}0{vis}' in i_line:
                    result = re.split(fr'{vis}', i_line)
                    result = f'{result[0]}{kks_dict_new[vis]}{result[1]}'
                    new_file.write(result)
                    break
            else:
                new_file.write(i_line)


async def compiling_list_of_kks(list_submodel: List[AnchorPoint],
                                data_ana: Set[str], data_bin: Set[str], data_nary: Set[str]):
    """Проверяет существование найденных KKS в базе данных"""
    for i_submodel in list_submodel:
        i_submodel.check_existence_database(data_ana=data_ana,
                                            data_bin=data_bin,
                                            data_nary=data_nary,
                                            set_suffix={'XH01', 'XH41', 'XH52', 'XH92'})


async def list_of_signals_on_video_frame(list_submodel: List[AnchorPoint]):
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


async def enumeration_of_svg(print_log, progress: QProgressBar) -> None:
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
        await print_log(text=f'[{num}/{len_num}] Проверка файла {i_svg}')
        progress.setValue(round(num / len_num * 100))
        if i_svg.endswith('.svg'):
            await bloc_button(svg=i_svg, set_kks_name_svg=set_kks_vis_npp_models)
            await print_log(text='\t+++SUCCESSFULLY+++', color='green', a_new_line=False)
        else:
            await print_log(text=f'\tНе является svg', color='yellow', a_new_line=False)
        num += 1


async def bloc_button(svg: str, set_kks_name_svg: Set[str]) -> None:
    """
    Функция проверяющая видеокадр и анализирует есть ли вызываемые видеокадры в папке NPP_models. Если вызываемого
    видеокадра нет, добавляет строку, которая делает неактивной кнопку вызова.
    :param svg: Название файла видеокадра.
    :param set_kks_name_svg: Список всех имеющихся видеокадров на которые может быть ссылка
    :return: None
    """
    alt_station_line = ''
    with open(path.join('SVSU', 'NPP_models', svg), 'r', encoding='windows-1251') as file_svg, \
            open(path.join('SVSU', 'new_NPP_models_SVSU', svg), 'w', encoding='windows-1251') as new_file_svg:
        flag_button = False
        for i_line in file_svg:
            if '<rt:dyn type="Disable" mode="constant" value="true"/>' in i_line:
                continue
            if flag_button:
                if 'Station_Name' in i_line:
                    alt_station_line = i_line
                    continue
                if 'type="OnClick">' in i_line:
                    new_file_svg.write(i_line)
                    try:
                        result = re.findall(r'&quot;(.*)&quot;', i_line)[0]
                    except IndexError:
                        try:
                            result = re.findall(r'\("(\d0.*\d+)"\)</', i_line)[0]
                        except IndexError:
                            result = '0'
                    if result in set_kks_name_svg:
                        if alt_station_line:
                            new_file_svg.write(alt_station_line)
                    else:
                        new_file_svg.write(f'    <rt:dyn type="Disable" mode="constant" value="true"/>\n')
                    flag_button = False
                else:
                    new_file_svg.write(i_line)
            else:
                if re.search(r'obj_Button.svg', i_line) or re.search(r'obj_Station_stat.svg', i_line):
                    flag_button = True
                new_file_svg.write(i_line)


async def add_file_svsu_import(print_log, name_system: str, progress: QProgressBar) -> None:
    """Функция подготовки файла SVSU_IMPORT.txt"""
    check_directory(path_directory='SVSU', name_directory='NPP_models')
    await save_old_file(print_log=print_log, name_system=name_system)
    if not await check_all_files(print_log=print_log, name_system=name_system):
        return

    list_name_svg_svsu = listdir(path.join('SVSU', 'NPP_models'))

    data_ana = await loading_data_kks_ana(name_system=name_system, print_log=print_log)
    data_bin = await loading_data_kks_bin(name_system=name_system, print_log=print_log)
    data_nary = await loading_data_kks_nary(name_system=name_system, print_log=print_log)
    set_ana_signal: Set[str] = set()
    set_bin_signal: Set[str] = set()
    set_nary_signal: Set[str] = set()
    num = 1
    number_name_svg = len(list_name_svg_svsu)
    for name_svg in list_name_svg_svsu:
        await print_log(text=f'[{num: <4}/{number_name_svg: <4}] Проверка {name_svg: <25}\t')
        progress.setValue(round(num / number_name_svg * 100))
        if name_svg.endswith('.svg'):
            list_submodel: List[AnchorPoint] = await creating_list_of_submodel(name_system='SVSU',
                                                                               name_svg=name_svg)
            await compiling_list_of_kks(list_submodel=list_submodel,
                                        data_ana=data_ana, data_bin=data_bin, data_nary=data_nary)
            set_ana, set_bin, set_nary = await list_of_signals_on_video_frame(list_submodel=list_submodel)
            await print_log(text=f'Найдено KKS: ANA - {len(set_ana): <4}, BIN - {len(set_bin): <4}, '
                                 f'NARY - {len(set_nary): <4}', color='green', a_new_line=False)
            set_ana_signal.update(set_ana)
            set_bin_signal.update(set_bin)
            set_nary_signal.update(set_nary)
        else:
            await print_log(text=f'Не является svg', color='yellow', a_new_line=False)
        num += 1
    await writing_signals_to_a_file(print_log=print_log,
                                    name_system=name_system,
                                    set_ana_signal=set_ana_signal,
                                    set_bin_signal=set_bin_signal,
                                    set_nary_signal=set_nary_signal)

    await file_comparison(print_log=print_log, name_system=name_system)


async def save_old_file(print_log, name_system: str):
    """Спрашивает у пользователя нужно ил сохранить старый файл. Если пользователь дает положительный ответ,
    запускает функцию переименования файла SVSU_IMPORT.txt"""
    msg = QMessageBox.question(QMainWindow(), 'Сохранение старого файла SVSU_IMPORT?',
                               'Забэкапить старый файл SVSU_IMPORT?\n'
                               '(файл SVSU_IMPORT.txt будет переименован в SVSU_IMPORT_bck.txt)')
    if msg == QMessageBox.StandardButton.Yes:
        await renaming_old_file_svsu_import(print_log=print_log, name_system=name_system)


async def check_all_files(print_log, name_system: str):
    """Функция проверяет наличие всех файлов (ANA_list_kks.txt, BIN_list_kks.txt, NARY_list_kks.txt)
     для работы программы по созданию файла SVSU_IMPORT.txt"""
    if not check_file(path_directory=path.join(name_system, 'data'), name_file='ANA_list_kks.txt'):
        msg = QMessageBox.question(QMainWindow(), 'Нет файла ANA_list_kks.txt',
                                   f'Не найден файл {name_system}/data/ANA_list_kks.txt\n '
                                   f'Для создания файла ANA_list_kks.txt выберите пункт "Обновление базы данных"'
                                   f' и систему {name_system}.\n'
                                   f'Продолжить выполнение программы без файла ANA_list_kks.txt?')
        if msg == QMessageBox.StandardButton.No:
            await print_log(text=f'Программа создания файла SVSU_IMPORT.txt прервана пользователем\n',
                            color='red')
            return False

    if not check_file(path_directory=path.join(name_system, 'data'), name_file='BIN_list_kks.txt'):
        msg = QMessageBox.question(QMainWindow(), 'Нет файла BIN_list_kks.txt',
                                   f'Не найден файл {name_system}/data/BIN_list_kks.txt\n '
                                   f'Для создания файла BIN_list_kks.txt выберите пункт "Обновление базы данных"'
                                   f' и систему {name_system}.\n'
                                   f'Продолжить выполнение программы без файла BIN_list_kks.txt?')
        if msg == QMessageBox.StandardButton.No:
            await print_log(text=f'Программа создания файла SVSU_IMPORT.txt прервана пользователем\n',
                            color='red')
            return False

    if not check_file(path_directory=path.join(name_system, 'data'), name_file='NARY_list_kks.txt'):
        msg = QMessageBox.question(QMainWindow(), 'Нет файла NARY_list_kks.txt',
                                   f'Не найден файл {name_system}/data/NARY_list_kks.txt\n '
                                   f'Для создания файла NARY_list_kks.txt выберите пункт "Обновление базы данных"'
                                   f' и систему {name_system}.\n'
                                   f'Продолжить выполнение программы без файла NARY_list_kks.txt?')
        if msg == QMessageBox.StandardButton.No:
            await print_log(text=f'Программа создания файла SVSU_IMPORT.txt прервана пользователем\n',
                            color='red')
            return False
    return True


async def renaming_old_file_svsu_import(print_log, name_system: str):
    """Функция переименовывает файл SVSU_IMPORT.txt в SVSU_IMPORT_bck.txt"""
    if check_file(path_directory=path.join(name_system, 'Исходники'), name_file='SVSU_IMPORT.txt'):
        if check_file(path_directory=path.join(name_system, 'Исходники'), name_file='SVSU_IMPORT_bck.txt'):
            remove(path.join(name_system, 'Исходники', 'SVSU_IMPORT_bck.txt'))
        rename(path.join(name_system, 'Исходники', 'SVSU_IMPORT.txt'),
               path.join(name_system, 'Исходники', 'SVSU_IMPORT_bck.txt'))
        await print_log(text=f'Файл {name_system}/Исходники/SVSU_IMPORT.txt переименован в '
                             f'{name_system}/Исходники/SVSU_IMPORT_bck.txt', color='green')
    else:
        await print_log(text=f'Файл {name_system}/Исходники/SVSU_IMPORT.txt не найден', color='red')


async def writing_signals_to_a_file(print_log, name_system: str,
                                    set_ana_signal: Set[str],
                                    set_bin_signal: Set[str],
                                    set_nary_signal: Set[str]):
    """Функция записывающая в файл SVSU_import.txt найденные сигналы"""
    with open(path.join(name_system, 'Исходники', 'SVSU_IMPORT.txt'), 'w', encoding='utf-8') as file_import:
        file_import.write('signum\ttype\tfunction\tcycle\n')
        await print_log(text=f'KKS записано в файл SVSU_IMPORT.txt:')
        for i_kks in sorted(set_ana_signal):
            file_import.write(f'\tA\t{i_kks}\t\n')
        await print_log(text=f'ANA - {len(set_ana_signal)}')
        for i_kks in sorted(set_bin_signal):
            file_import.write(f'\tB\t{i_kks}\t\n')
        await print_log(text=f'BIN - {len(set_bin_signal)}')
        for i_kks in sorted(set_nary_signal):
            file_import.write(f'\tN\t{i_kks}\t\n')
        await print_log(text=f'NARY - {len(set_nary_signal)}')


async def file_comparison(print_log, name_system: str) -> None:
    """Функция спрашивает у пользователя сравнивать ли старый файл SVSU_IMPORT с новым. Если получает положительный
    ответ, запускает функцию сравнения и вывода всех отличий пользователю"""
    if check_file(path_directory=path.join(name_system, 'Исходники'), name_file='SVSU_IMPORT_bck.txt'):
        msg = QMessageBox.question(QMainWindow(), 'Вывод внесенных изменений',
                                   'Произвести сравнение старого файла SVSU_IMPORT с новым?')
        if msg == QMessageBox.StandardButton.Yes:
            await file_svsu_import_comparison(print_log=print_log, name_system=name_system)


async def file_svsu_import_comparison(print_log, name_system: str):
    """Функция сравнения двух файлов SVSU_IMPORT.txt и SVSU_IMPORT_bck.txt и вывода отчета"""
    list_kks_svsu_import: Set[str] = set()
    list_kks_svsu_import_bck: Set[str] = set()
    with open(path.join(name_system, 'Исходники', 'SVSU_IMPORT.txt'), encoding='UTF-8') as file_svsu:
        for i_line in file_svsu:
            list_kks_svsu_import.add(i_line[:-1])

    with open(path.join(name_system, 'Исходники', 'SVSU_IMPORT_bck.txt'), encoding='UTF-8') as file_svsu_bck:
        for i_line in file_svsu_bck:
            list_kks_svsu_import_bck.add(i_line[:-1])

    del_kks = list_kks_svsu_import_bck.difference(list_kks_svsu_import)
    add_kks = list_kks_svsu_import.difference(list_kks_svsu_import_bck)

    await print_log(text=f'Удалены KKS в новом ({len(del_kks)} шт.):', color='red')
    num = 1
    for i_kks in sorted(del_kks):
        await print_log(text=f'{num}. {i_kks}', color='red')
        num += 1
    await print_log(text='')

    await print_log(text=f'Добавлены KKS в новом ({len(add_kks)} шт.):', color='green')
    num = 1
    for i_kks in sorted(add_kks):
        await print_log(text=f'{num}. {i_kks}', color='green')
        num += 1
    await print_log(text='')
