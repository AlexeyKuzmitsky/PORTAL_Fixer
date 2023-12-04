from typing import List, Set, Dict
import re
from math import ceil
from config.get_logger import log_info
from config.general_functions import check_directory
from os import path
from config.point_description import AnchorPoint
import json


# set_kks_bin_date: Set[str] = set()  # список ккс сигналов BIN из базы
# set_kks_ana_date: Set[str] = set()  # список ккс сигналов ANA из базы
#
# dict_kks_bin_data: Dict = dict()  # список ккс сигналов с описанием BIN из базы
# dict_kks_ana_data: Dict = dict()  # список ккс сигналов с описанием ANA из базы


# async def loading_data(self, directory: str = '') -> \
#         (Set[str], Set[str], Dict[str, Dict[str, str]], Dict[str, Dict[str, str]]):
#     """
#     Функция считывающая базу сигналов.
#     :return: 1-множество аналоговых сигналов, 2-множество бинарных сигналов,
#     3-словарь аналоговых сигналов с описанием, 4-словарь бинарных сигналов с описанием
#     """
#     set_kks_bin_data: Set[str] = set()
#     set_kks_ana_data: Set[str] = set()
#     dict_kks_bin_data: Dict[str, Dict[str, str]] = dict()
#     dict_kks_ana_data: Dict[str, Dict[str, str]] = dict()
#
#     await self.print_log(text=f'Загрузка БД {directory}')
#     with open(path.join(directory, 'data', 'ANA_list_kks.txt')) as file:
#         for i_line in file:
#             set_kks_ana_data.add(i_line[:-1])
#
#     with open(path.join(directory, 'data', 'ANA_json_kks.json'), 'r', encoding='UTF-8') as json_file:
#         dict_ana_kks = json.load(json_file)
#         dict_kks_ana_data.update(dict_ana_kks)
#
#     with open(path.join(directory, 'data', 'BIN_list_kks.txt')) as file:
#         for i_line in file:
#             set_kks_bin_data.add(i_line[:-1])
#
#     with open(path.join(directory, 'data', 'BIN_json_kks.json'), 'r', encoding='UTF-8') as json_file:
#         dict_bin_kks = json.load(json_file)
#         dict_kks_bin_data.update(dict_bin_kks)
#     return set_kks_bin_data, set_kks_ana_data, dict_kks_bin_data, dict_kks_ana_data


async def creating_list_of_submodel(svg_file, name_svg: str) -> List[AnchorPoint]:
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
                await new_submodel(list_constructor=list_constructor,
                                   list_submodel=list_submodel,
                                   name_svg=name_svg)
                flag_constructor = False
                list_constructor.clear()
            else:
                list_constructor.append(i_line)
        else:
            if '<image' in i_line and '</image>' in i_line or '<image' in i_line and '/>' in i_line:
                list_constructor.append(i_line)
                await new_submodel(list_constructor=list_constructor,
                                   list_submodel=list_submodel,
                                   name_svg=name_svg)
                list_constructor.clear()
            elif '<image' in i_line:
                flag_constructor = True
                list_constructor.clear()
                list_constructor.append(i_line)
    return list_submodel


async def new_submodel(list_constructor, list_submodel, name_svg: str) -> None:
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
        # submodel.set_width_and_height()
        # submodel.set_x_and_y()
        # submodel.set_transform()
        try:
            submodel.search_kks_on_submodel()
        except IndexError as e:
            print(submodel.name_svg)
            print(submodel.full_description_of_the_submodel)
            print(e)
        list_submodel.append(submodel)


async def checking_kks_and_preparing_comment(kks_signal: str,
                                             list_error_kks: Set[str],
                                             name_submodel: str,
                                             set_svg: Set[str],
                                             set_kks_ana_data: Set[str],
                                             set_kks_bin_data: Set[str],
                                             set_kks_nary_data: Set[str],
                                             dict_kks_ana_data: Dict[str, Dict[str, str]],
                                             dict_kks_bin_data: Dict[str, Dict[str, str]],
                                             dict_kks_nary_data: Dict[str, Dict[str, str]]):
    """Функция проверки наличия в базе KKS и подготовки сообщения с замечанием в случае отсутствия сигнала в базе"""
    if re.search('_', kks_signal):
        if kks_signal in set_kks_ana_data:
            return
        elif kks_signal in set_kks_bin_data:
            return
        elif kks_signal in set_kks_nary_data:
            return
        text_search_similar_kks = await search_similar_kks(kks=kks_signal.split('_')[0],
                                                           dict_kks_ana_data=dict_kks_ana_data,
                                                           dict_kks_bin_data=dict_kks_bin_data,
                                                           dict_kks_nary_data=dict_kks_nary_data)
    else:
        if f'{kks_signal}.svg' in set_svg or f'{kks_signal}.SVG' in set_svg:
            return
        kks_1 = f'{kks_signal}_F0'
        kks_2 = f'{kks_signal}_XQ01'
        if kks_1 in set_kks_nary_data or kks_2 in set_kks_ana_data:
            return
        text_search_similar_kks = await search_similar_kks(kks=kks_signal,
                                                           dict_kks_ana_data=dict_kks_ana_data,
                                                           dict_kks_bin_data=dict_kks_bin_data,
                                                           dict_kks_nary_data=dict_kks_nary_data)
    list_error_kks.add(record_comment(kks=kks_signal,
                                      svg_constructor=name_submodel,
                                      text_search_similar_kks=text_search_similar_kks))


def recording_comments_to_a_file(directory: str, list_error_kks: Set[str], name_file: str):
    """Функция запись замечаний найденных на видеокадре в файл"""
    check_directory(path_directory=directory,
                    name_directory='Замечания по видеокадрам')
    with open(path.join(directory, 'Замечания по видеокадрам', f'{name_file}.txt'),
              'w', encoding='utf-8') as file:
        for i_kks in list_error_kks:
            file.write(f'{i_kks}\n')


def kks_in_date(kks: str, set_kks_ana_date: Set[str], set_kks_bin_date: Set[str]) -> bool:
    """
    Функция выполняющая проверку наличия KKS в базе данных. При нахождении сигнала в базе возвращает True, иначе False.
    :param kks: KKS проверяемого сигнала.
    :param set_kks_ana_date: Список всех аналоговых сигналов в базе
    :param set_kks_bin_date: Список всех бинарных сигналов в базе
    :return: bool (True, False)
    """
    if kks in set_kks_ana_date:
        # log.info(f'Найден ккс {kks}. Есть в базе ANA')
        return True
    elif kks in set_kks_bin_date:
        # log.info(f'Найден ккс {kks}. Есть в базе BIN')
        return True
    else:
        # log.info(f'Найден ккс {kks}. !!!!!!!!!!!!НЕТ В БАЗЕ!!!!!!!!!!!!')
        return False


def record_comment(kks: str, svg_constructor: str, text_search_similar_kks: str, text: str = 'нет в базе\t') -> str:
    """Добавляет запись о нахождении отсутствующего KKS в базе."""
    number_tyb = '\t' * ceil((24 - len(kks)) / 4)
    return f'{kks}{number_tyb}{text}{svg_constructor}{text_search_similar_kks}'


async def search_similar_kks(kks: str,
                             dict_kks_ana_data: Dict[str, Dict[str, str]],
                             dict_kks_bin_data: Dict[str, Dict[str, str]],
                             dict_kks_nary_data: Dict[str, Dict[str, str]]) -> str:
    """
    Функция находящая в базе данных сигналы схожие с найденным основанием.
    :param kks: KKS найденного сигнала, по которому ищутся похожие.
    :param dict_kks_ana_data: Словарь аналоговых сигналов с описанием поделенных по KKS
    :param dict_kks_bin_data: Словарь бинарных сигналов с описанием поделенных по KKS
    :param dict_kks_nary_data: Словарь много битовых сигналов с описанием поделенных по KKS
    :return: Все найденные сигналы с описанием.
    """
    text = ''
    if kks in dict_kks_ana_data:
        for i_kks in dict_kks_ana_data[kks]:
            text = f'{text}\n\t\tANA: {i_kks} - {dict_kks_ana_data[kks][i_kks]}'
    if kks in dict_kks_bin_data:
        for i_kks in dict_kks_bin_data[kks]:
            text = f'{text}\n\t\tBIN: {i_kks} - {dict_kks_bin_data[kks][i_kks]}'
    if kks in dict_kks_nary_data:
        text = f'{text}\n\t\tNARY: {kks}'
        for number_bit, description in dict_kks_nary_data[kks].items():
            text = f'{text}\n\t\t\t {number_bit} - {description}'
    return text


def out_kks_suffix(set_line_text: Set,
                   id_kks: str,
                   id_suffix: str,
                   svg_constructor: str,
                   dict_kks_svg: Dict[str, str],
                   default_suffix: str = None) -> None:
    """
    Функция, производящая поиск KKS и при отсутствии суффикса ведет поиск суффикс, если его нет, добавляет
    стандартный суффикс.
    :param set_line_text: Список сток с данными подмоделями.
    :param id_kks: Имя параметра в котором ведется поиск KKS.
    :param id_suffix: Имя параметра в котором ведется поиск суффикса.
    :param svg_constructor: Имя подмодели.
    :param dict_kks_svg: Список сигналов найденных на видеокадре с названием подмодели
    :param default_suffix: Суффикс, который добавляется если ничего другого не нашлось.
    :return: None
    """
    kks: List[str] = list()
    for i_line in set_line_text:
        if re.search(f'{id_kks}', i_line):
            kks = re.findall(r'value="&quot;([^& ]*).*&quot;"', i_line)
            break
    for i_kks in kks:
        if re.search(r'_', i_kks):
            dict_kks_svg[i_kks] = svg_constructor
        elif len(i_kks):
            for i_line in set_line_text:
                if re.search(f'{id_suffix}', i_line):
                    try:
                        suffix = re.findall(r'value="&(quot|apos);(.*).*&(quot|apos);"', i_line)[0][1]
                        new_kks = f'{i_kks}_{suffix}'
                        dict_kks_svg[new_kks] = svg_constructor
                    except IndexError:
                        new_kks = f'{i_kks}_{default_suffix}'
                        dict_kks_svg[new_kks] = svg_constructor
                    break
            else:
                new_kks = f'{i_kks}_{default_suffix}'
                dict_kks_svg[new_kks] = svg_constructor
        else:
            log_info.info(f'ERROR нет привязки на подмодели {svg_constructor}')


def out_kks(set_line_text: Set, id_kks: str, svg_constructor: str, dict_kks_svg: Dict[str, str]) -> None:
    """
    Функция, производящая поиск KKS и при отсутствии суффикса ведет поиск суффикс, если его нет, добавляет
    стандартный суффикс.
    :param set_line_text: Список сток с данными подмоделями.
    :param id_kks: Имя параметра в котором ведется поиск KKS.
    :param svg_constructor: Имя подмодели.
    :param dict_kks_svg: Список сигналов найденных на видеокадре с названием подмодели
    :return: None
    """
    kks = ''
    for i_line in set_line_text:
        if re.search(f'{id_kks}', i_line):
            try:
                kks = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)
                break
            except IndexError:
                log_info.info('На подмодели нет привязки')
                return
    for i_kks in kks:
        if re.search(r'_', i_kks):
            dict_kks_svg[i_kks] = svg_constructor
        elif len(i_kks):
            if i_kks == 'NULL':
                log_info.info(f'ERROR нет привязки на подмодели {svg_constructor}')
            else:
                i_kks = f'{i_kks}_F0'
                dict_kks_svg[i_kks] = svg_constructor
        else:
            log_info.info(f'ERROR нет привязки на подмодели {svg_constructor}')


def out_kks_nary(set_line_text: Set,
                 id_kks: str,
                 svg_constructor: str,
                 dict_kks_svg: Dict[str, str],
                 end_kks: str = 'TE0',
                 flag_teo: bool = True) -> None:
    """
    Функция производящая поиск ккс в подмодели
    :param set_line_text: Список сток с данными подмоделями
    :param id_kks:  Имя параметра в котором ведется поиск KKS
    :param svg_constructor: Имя подмодели
    :param dict_kks_svg: Список сигналов найденных на видеокадре с названием подмодели
    :param end_kks:  Окончание сигнала добавляемое в случае его отсутствия
    :param flag_teo:  Флаг, указывающий на добавление в конце KKS окончание TE0
    :return: None
    """
    переделать
    i_kks = ''
    for i_line in set_line_text:
        if re.search(f'{id_kks}', i_line):
            try:
                i_kks = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
                break
            except IndexError:
                log_info.info('На подмодели нет привязки')
                return

    if re.search(r'_', i_kks):
        dict_kks_svg[i_kks] = svg_constructor

    list_sig: Set[str] = set()
    for i_line in set_line_text:
        if re.search(r'SIG_', i_line):
            try:
                list_sig.add(re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0])
            except IndexError:
                pass

    for i_sig in list_sig:
        if '_' not in i_sig:
            if i_sig != 'NULL':
                dict_kks_svg[f'{i_kks}_{i_sig}'] = svg_constructor
            break
        else:
            dict_kks_svg[i_sig] = svg_constructor

    if i_kks != 'NULL' or i_kks != '':
        if flag_teo:
            if i_kks.endswith(end_kks):
                dict_kks_svg[f'{i_kks}_Z0'] = svg_constructor
            else:
                dict_kks_svg[f'{i_kks}{end_kks}_Z0'] = svg_constructor
        else:
            dict_kks_svg[f'{i_kks}_Z0'] = svg_constructor
    else:
        log_info.info(f'ERROR нет привязки на подмодели {svg_constructor}')
###############
    # elif i_kks != 'NULL':
    #     flag = False
    #     if kks_in_date(f'{i_kks}_Z0'):
    #         flag = True
    #     elif flag_teo:
    #         if kks_in_date(f'{i_kks}{end_kks}_Z0'):
    #             flag = True
    #         else:
    #             for i_line in set_line_text:
    #                 if re.search(r'SIG_', i_line):
    #                     try:
    #                         suffix = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
    #                         if kks_in_date(f'{i_kks}_{suffix}'):
    #                             flag = True
    #                     except IndexError:
    #                         pass
    #     if not flag:
    #         dict_kks_svg[i_kks] = svg_constructor
    # else:
    #     log_info.info(f'ERROR нет привязки на подмодели {svg_constructor}')
####################


def out_vis_kks_nary(set_line_text: Set,
                     id_kks: str,
                     svg_constructor: str,
                     name_svg: str,
                     dict_kks_svg: Dict[str, str]) -> None:
    """
    Функция производящая поиск ккс в подмодели с использованием части KKS видеокадра если нет полного KKS
    :param set_line_text: Список строк с данными подмоделями
    :param id_kks:  Имя параметра в котором ведется поиск KKS
    :param svg_constructor: Имя подмодели
    :param name_svg: Имя видеокадра
    :param dict_kks_svg: Список сигналов найденных на видеокадре с названием подмодели
    :return: None
    """
    i_kks = ''
    for i_line in set_line_text:
        if re.search(f'{id_kks}', i_line):
            try:
                i_kks = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
                dict_kks_svg[i_kks] = svg_constructor
                break
            except IndexError:
                i_kks = re.findall(r'value="PVId_base \+ &quot;([^, ]*).*&quot;"', i_line)[0]
                i_kks = f'{name_svg}{i_kks}'
                dict_kks_svg[i_kks] = svg_constructor
    else:
        log_info.info(f'ERROR KKS{i_kks} без привязки на подмодели {svg_constructor}')


def out_some_kks(set_line_text: Set, id_kks: str, svg_constructor: str, dict_kks_svg: Dict[str, str]) -> None:
    """
    Функция производящая поиск ккс в подмодели которая может содержать больше одного KKS.
    :param set_line_text: Список сток с данными подмоделями
    :param id_kks:  Имя параметра в котором ведется поиск KKS
    :param svg_constructor:  Имя подмодели
    :param dict_kks_svg: Список сигналов найденных на видеокадре с названием подмодели
    :return: None
    """
    kks_list: List[str] = list()
    for i_line in set_line_text:
        if re.search(f'{id_kks}', i_line):
            try:
                for i_kks in re.findall(r'&quot;([^, &]*).*&quot;', i_line):
                    kks_list.append(i_kks)
            except IndexError:
                log_info.info('В нужной строке не найден KKS')
    if not len(kks_list):
        log_info.info(f'На подмодели {svg_constructor} нет привязки')

    for i_kks in kks_list:
        if re.search(r'_', i_kks):
            dict_kks_svg[i_kks] = svg_constructor


def out_kks_with_te_vl(set_line_text: Set, id_kks: str, svg_constructor: str, dict_kks_svg: Dict[str, str]) -> None:
    """
    Функция производящая поиск ккс в подмодели с подстановкой окончания KKS TE и VL
    :param set_line_text: Список сток с данными подмоделями
    :param id_kks:  Имя параметра в котором ведется поиск KKS
    :param svg_constructor:  Имя подмодели
    :param dict_kks_svg: Список сигналов найденных на видеокадре с названием подмодели
    :return: None
    """
    for i_line in set_line_text:
        if re.search(f'{id_kks}', i_line):
            try:
                kks = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
                if re.search(r'_', kks):
                    dict_kks_svg[kks] = svg_constructor
                elif kks.endswith('TE0') or kks.endswith('VL0'):
                    dict_kks_svg[f'{kks}_Z0'] = svg_constructor
                else:
                    dict_kks_svg[f'{kks}TE0_Z0'] = svg_constructor
            except IndexError:
                log_info.info('В нужной строке не найден KKS')

#########################################
# def out_kks_suffix(set_line_text: Set,
#                    id_kks: str,
#                    id_suffix: str,
#                    svg_constructor: str,
#                    dict_kks_svg: Dict[str, str],
#                    default_suffix: str = None) -> None:
#     """
#     Функция, производящая поиск KKS и при отсутствии суффикса ведет поиск суффикс, если его нет, добавляет
#     стандартный суффикс.
#     :param set_line_text: Список сток с данными подмоделями.
#     :param id_kks: Имя параметра в котором ведется поиск KKS.
#     :param id_suffix: Имя параметра в котором ведется поиск суффикса.
#     :param svg_constructor: Имя подмодели.
#     :param dict_kks_svg: Список сигналов найденных на видеокадре с названием подмодели
#     :param default_suffix: Суффикс, который добавляется если ничего другого не нашлось.
#     :return: None
#     """
#     kks: List[str] = list()
#     for i_line in set_line_text:
#         if re.search(f'{id_kks}', i_line):
#             kks = re.findall(r'value="&quot;([^& ]*).*&quot;"', i_line)
#             break
#     for i_kks in kks:
#         if re.search(r'_', i_kks):
#             if not kks_in_date(i_kks):
#                 dict_kks_svg[i_kks] = svg_constructor
#         elif len(i_kks):
#             for i_line in set_line_text:
#                 if re.search(f'{id_suffix}', i_line):
#                     try:
#                         suffix = re.findall(r'value="&(quot|apos);(.*).*&(quot|apos);"', i_line)[0][1]
#                         new_kks = f'{i_kks}_{suffix}'
#                         if not kks_in_date(new_kks):
#                             dict_kks_svg[new_kks] = svg_constructor
#                     except IndexError:
#                         new_kks = f'{i_kks}_{default_suffix}'
#                         if not kks_in_date(new_kks):
#                             dict_kks_svg[new_kks] = svg_constructor
#                     break
#             else:
#                 new_kks = f'{i_kks}_{default_suffix}'
#                 if not kks_in_date(new_kks):
#                     dict_kks_svg[new_kks] = svg_constructor
#         else:
#             log_info.info(f'ERROR нет привязки на подмодели {svg_constructor}')
#
#
#
#
#
# def out_kks(set_line_text: Set, id_kks: str, svg_constructor: str, dict_kks_svg: Dict[str, str]) -> None:
#     """
#     Функция, производящая поиск KKS и при отсутствии суффикса ведет поиск суффикс, если его нет, добавляет
#     стандартный суффикс.
#     :param set_line_text: Список сток с данными подмоделями.
#     :param id_kks: Имя параметра в котором ведется поиск KKS.
#     :param svg_constructor: Имя подмодели.
#     :param dict_kks_svg: Список сигналов найденных на видеокадре с названием подмодели
#     :return: None
#     """
#     kks = ''
#     for i_line in set_line_text:
#         if re.search(f'{id_kks}', i_line):
#             try:
#                 kks = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)
#                 break
#             except IndexError:
#                 log_info.info('На подмодели нет привязки')
#                 return
#     for i_kks in kks:
#         if re.search(r'_', i_kks):
#             if not kks_in_date(i_kks):
#                 dict_kks_svg[i_kks] = svg_constructor
#         elif len(i_kks):
#             if i_kks == 'NULL':
#                 log_info.info(f'ERROR нет привязки на подмодели {svg_constructor}')
#             else:
#                 i_kks = f'{i_kks}_F0'
#                 if not kks_in_date(i_kks):
#                     dict_kks_svg[i_kks] = svg_constructor
#         else:
#             log_info.info(f'ERROR нет привязки на подмодели {svg_constructor}')
#
#
# def out_kks_nary(set_line_text: Set,
#                  id_kks: str,
#                  svg_constructor: str,
#                  dict_kks_svg: Dict[str, str],
#                  end_kks: str = 'TE0',
#                  flag_teo: bool = True) -> None:
#     """
#     Функция производящая поиск ккс в подмодели
#     :param set_line_text: Список сток с данными подмоделями
#     :param id_kks:  Имя параметра в котором ведется поиск KKS
#     :param svg_constructor: Имя подмодели
#     :param dict_kks_svg: Список сигналов найденных на видеокадре с названием подмодели
#     :param end_kks:  Окончание сигнала добавляемое в случае его отсутствия
#     :param flag_teo:  Флаг, указывающий на добавление в конце KKS окончание TE0
#     :return: None
#     """
#     i_kks = ''
#     for i_line in set_line_text:
#         if re.search(f'{id_kks}', i_line):
#             try:
#                 i_kks = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
#                 break
#             except IndexError:
#                 log_info.info('На подмодели нет привязки')
#                 return
#
#     if re.search(r'_', i_kks):
#         if not kks_in_date(i_kks):
#             dict_kks_svg[i_kks] = svg_constructor
#
#     elif i_kks == 'NULL' or i_kks == '':
#         for i_line in set_line_text:
#             if re.search(r'SIG_', i_line):
#                 try:
#                     i_kks = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
#                     if i_kks == 'NULL' or kks_in_date(i_kks):
#                         continue
#                     else:
#                         dict_kks_svg[i_kks] = svg_constructor
#
#                 except IndexError:
#                     pass
#
#     elif i_kks != 'NULL':
#         flag = False
#         if kks_in_date(f'{i_kks}_Z0'):
#             flag = True
#         elif flag_teo:
#             if kks_in_date(f'{i_kks}{end_kks}_Z0'):
#                 flag = True
#             else:
#                 for i_line in set_line_text:
#                     if re.search(r'SIG_', i_line):
#                         try:
#                             suffix = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
#                             if kks_in_date(f'{i_kks}_{suffix}'):
#                                 flag = True
#                         except IndexError:
#                             pass
#         if not flag:
#             dict_kks_svg[i_kks] = svg_constructor
#     else:
#         log_info.info(f'ERROR нет привязки на подмодели {svg_constructor}')
#
#
# def out_vis_kks_nary(set_line_text: Set,
#                      id_kks: str,
#                      svg_constructor: str,
#                      name_svg: str,
#                      dict_kks_svg: Dict[str, str]) -> None:
#     """
#     Функция производящая поиск ккс в подмодели с использованием части KKS видеокадра если нет полного KKS
#     :param set_line_text: Список строк с данными подмоделями
#     :param id_kks:  Имя параметра в котором ведется поиск KKS
#     :param svg_constructor: Имя подмодели
#     :param name_svg: Имя видеокадра
#     :param dict_kks_svg: Список сигналов найденных на видеокадре с названием подмодели
#     :return: None
#     """
#     i_kks = ''
#     for i_line in set_line_text:
#         if re.search(f'{id_kks}', i_line):
#             try:
#                 i_kks = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
#                 break
#             except IndexError:
#                 i_kks = re.findall(r'value="PVId_base \+ &quot;([^, ]*).*&quot;"', i_line)[0]
#                 i_kks = f'{name_svg}{i_kks}'
#
#     if not kks_in_date(f'{i_kks}_F0'):
#         dict_kks_svg[i_kks] = svg_constructor
#         log_info.info(f'ERROR KKS{i_kks} без привязки на подмодели {svg_constructor}')
#
#
# def out_some_kks(set_line_text: Set, id_kks: str, svg_constructor: str, dict_kks_svg: Dict[str, str]) -> None:
#     """
#     Функция производящая поиск ккс в подмодели которая может содержать больше одного KKS.
#     :param set_line_text: Список сток с данными подмоделями
#     :param id_kks:  Имя параметра в котором ведется поиск KKS
#     :param svg_constructor:  Имя подмодели
#     :param dict_kks_svg: Список сигналов найденных на видеокадре с названием подмодели
#     :return: None
#     """
#     kks_list: List[str] = list()
#     for i_line in set_line_text:
#         if re.search(f'{id_kks}', i_line):
#             try:
#                 for i_kks in re.findall(r'&quot;([^, &]*).*&quot;', i_line):
#                     kks_list.append(i_kks)
#             except IndexError:
#                 log_info.info('В нужной строке не найден KKS')
#     if not len(kks_list):
#         log_info.info(f'На подмодели {svg_constructor} нет привязки')
#
#     for i_kks in kks_list:
#         if re.search(r'_', i_kks):
#             if not kks_in_date(i_kks):
#                 dict_kks_svg[i_kks] = svg_constructor
#
#
# def out_kks_with_te_vl(set_line_text: Set, id_kks: str, svg_constructor: str, dict_kks_svg: Dict[str, str]) -> None:
#     """
#     Функция производящая поиск ккс в подмодели с подстановкой окончания KKS TE и VL
#     :param set_line_text: Список сток с данными подмоделями
#     :param id_kks:  Имя параметра в котором ведется поиск KKS
#     :param svg_constructor:  Имя подмодели
#     :param dict_kks_svg: Список сигналов найденных на видеокадре с названием подмодели
#     :return: None
#     """
#     for i_line in set_line_text:
#         if re.search(f'{id_kks}', i_line):
#             try:
#                 kks = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
#                 if re.search(r'_', kks):
#                     if kks_in_date(kks):
#                         return
#                     else:
#                         dict_kks_svg[kks] = svg_constructor
#                 elif kks.endswith('TE0') or kks.endswith('VL0'):
#                     if kks_in_date(f'{kks}_Z0'):
#                         return
#                     else:
#                         dict_kks_svg[kks] = svg_constructor
#                 elif kks_in_date(f'{kks}TE0_Z0') or kks_in_date(f'{kks}VL0_Z0'):
#                     return
#                 else:
#                     dict_kks_svg[kks] = svg_constructor
#             except IndexError:
#                 log_info.info('В нужной строке не найден KKS')

########################################
async def base_name_svg(svg: str) -> str:
    if svg.startswith('diag_'):
        return svg[5:12]
    else:
        return svg[0:7]
