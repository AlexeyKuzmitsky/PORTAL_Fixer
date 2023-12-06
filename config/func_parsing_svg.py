from typing import Set, Dict
import re
from math import ceil
from config.general_functions import check_directory
from os import path


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
