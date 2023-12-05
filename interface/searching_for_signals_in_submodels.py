from typing import List, Set, Dict
import re
from math import ceil
from config.general_functions import check_directory
from os import path
from config.point_description import AnchorPoint


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
                                             dict_kks_bin_data: Dict[str, Dict[str, str]]):
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
                                                           dict_kks_bin_data=dict_kks_bin_data)
    else:
        if f'{kks_signal}.svg' in set_svg or f'{kks_signal}.SVG' in set_svg:
            return
        kks_1 = f'{kks_signal}_F0'
        kks_2 = f'{kks_signal}_XQ01'
        if kks_1 in set_kks_nary_data or kks_2 in set_kks_ana_data:
            return
        text_search_similar_kks = await search_similar_kks(kks=kks_signal,
                                                           dict_kks_ana_data=dict_kks_ana_data,
                                                           dict_kks_bin_data=dict_kks_bin_data)
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


def record_comment(kks: str, svg_constructor: str, text_search_similar_kks: str, text: str = 'нет в базе\t') -> str:
    """Добавляет запись о нахождении отсутствующего KKS в базе."""
    number_tyb = '\t' * ceil((24 - len(kks)) / 4)
    return f'{kks}{number_tyb}{text}{svg_constructor}{text_search_similar_kks}'


async def search_similar_kks(kks: str,
                             dict_kks_ana_data: Dict[str, Dict[str, str]],
                             dict_kks_bin_data: Dict[str, Dict[str, str]]) -> str:
    """
    Функция находящая в базе данных сигналы схожие с найденным основанием.
    :param kks: KKS найденного сигнала, по которому ищутся похожие.
    :param dict_kks_ana_data: Словарь аналоговых сигналов с описанием поделенных по KKS
    :param dict_kks_bin_data: Словарь бинарных сигналов с описанием поделенных по KKS
    :return: Все найденные сигналы с описанием.
    """
    text = ''
    if kks in dict_kks_ana_data:
        for i_kks in dict_kks_ana_data[kks]:
            text = f'{text}\n\t\tANA: {i_kks} - {dict_kks_ana_data[kks][i_kks]}'
    if kks in dict_kks_bin_data:
        for i_kks in dict_kks_bin_data[kks]:
            text = f'{text}\n\t\tBIN: {i_kks} - {dict_kks_bin_data[kks][i_kks]}'
    return text
