from config.point_description import AnchorPoint
from typing import List, Set
from os import path

import re


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


async def bloc_button(svg: str, set_kks_name_svg: Set[str]) -> None:
    """
    Функция проверяющая видеокадр и анализирует есть ли вызываемые видеокадры в папке NPP_models. Если вызываемого
    видеокадра нет, добавляет строку, которая делает неактивной кнопку вызова.
    :param svg: Название файла видеокадра.
    :param set_kks_name_svg: Список всех имеющихся видеокадров на которые может быть ссылка
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
