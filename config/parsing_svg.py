import json
from os import listdir, path, system
import shutil
import re
from typing import List, Set, Dict
from csv import reader
from math import ceil

from .video_frame_sorting import dict_loading, sort_files_into_groups
from .general_functions import check_directory
from .get_logger import log_info, log_info_print
from .timer import timer


set_kks_bin_date: Set[str] = set()  # список ккс сигналов BIN из базы
set_kks_ana_date: Set[str] = set()  # список ккс сигналов ANA из базы

dict_kks_bin_data: Dict = dict()  # список ккс сигналов с описанием BIN из базы
dict_kks_ana_data: Dict = dict()  # список ккс сигналов с описанием ANA из базы

kks_set: Set[str] = set()  # Все найденные KKS на видеокадре


def kks_in_date(kks: str) -> bool:
    """
    Функция выполняющая проверку наличия KKS в базе данных. При нахождении сигнала в базе возвращает True, иначе False.
    :param kks: KKS проверяемого сигнала.
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


@timer
def new_date(name_directory: str) -> None:
    """
    Функция обновления файлов со списком KKS сигналов. По завершению обновляются (создаются если не было) 2 файла:
    BIN_list_kks.txt со списком бинарных сигналов
    ANA_list_kks.txt со списков аналоговых сигналов
    :param name_directory: папка в которой будут обновления.
    :return: None
    """
    set_kks_bin_date.clear()
    set_kks_ana_date.clear()

    dict_kks_bin_data.clear()
    dict_kks_ana_data.clear()

    log_info_print.info('Сбор BIN сигналов')
    with open(path.join(name_directory, 'DbDumps', 'PLS_BIN_CONF.dmp'), 'r', encoding='windows-1251') as file:
        new_text = reader(file, delimiter='|')
        for i_line in new_text:
            try:
                full_kks = i_line[42]
                kks = full_kks.partition('_')[0]
                description = i_line[43]
                if kks in dict_kks_bin_data:
                    dict_kks_bin_data[kks][full_kks] = description
                else:
                    uno_dict_kks = {full_kks: description}
                    dict_kks_bin_data[kks] = uno_dict_kks

                set_kks_bin_date.add(i_line[42])
            except IndexError:
                ...

    with open(path.join(name_directory, 'data', 'BIN_json_kks.json'), 'w', encoding='UTF-8') as json_file:
        json.dump(dict_kks_bin_data, json_file, indent=4, ensure_ascii=False)

    with open(path.join(name_directory, 'data', 'BIN_list_kks.txt'), 'w', encoding='UTF-8') as file:
        for i_kks in set_kks_bin_date:
            file.write(f'{i_kks}\n')

    log_info_print.info('Accesses. Сигналы BIN собраны успешно')

    log_info_print.info('Сбор ANA сигналов')
    with open(path.join(name_directory, 'DbDumps', 'PLS_ANA_CONF.dmp'), 'r', encoding='windows-1251') as file:
        new_text = reader(file, delimiter='|', quotechar=' ')
        for i_line in new_text:
            try:
                full_kks = i_line[78]
                kks = full_kks.partition('_')[0]
                description = i_line[79]
                if kks in dict_kks_ana_data:
                    dict_kks_ana_data[kks][full_kks] = description
                else:
                    uno_dict_kks = {full_kks: description}
                    dict_kks_ana_data[kks] = uno_dict_kks

                set_kks_ana_date.add(i_line[78])
            except IndexError:
                pass

    with open(path.join(name_directory, 'data', 'ANA_json_kks.json'), 'w', encoding='UTF-8') as json_file:
        json.dump(dict_kks_ana_data, json_file, indent=4, ensure_ascii=False)

    with open(path.join(name_directory, 'data', 'ANA_list_kks.txt'), 'w', encoding='UTF-8') as file:
        for i_kks in set_kks_ana_date:
            file.write(f'{i_kks}\n')
    log_info_print.info('Accesses. Сигналы ANA собраны успешно')


def search_similar_kks(kks: str) -> str:
    """
    Функция находящая в базе данных сигналы схожие с найденным основанием.
    :param kks: KKS найденного сигнала, по которому ищутся похожие.
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


def add_date(directory: str = '') -> None:
    """
    Функция считывающая базу сигналов.
    :return: None
    """
    with open(path.join(directory, 'data', 'ANA_list_kks.txt')) as file:
        for i_line in file:
            set_kks_ana_date.add(i_line[:-1])

    with open(path.join(directory, 'data', 'ANA_json_kks.json'), 'r', encoding='UTF-8') as json_file:
        dict_ana_kks = json.load(json_file)
        dict_kks_ana_data.update(dict_ana_kks)

    with open(path.join(directory, 'data', 'BIN_list_kks.txt')) as file:
        for i_line in file:
            set_kks_bin_date.add(i_line[:-1])

    with open(path.join(directory, 'data', 'BIN_json_kks.json'), 'r', encoding='UTF-8') as json_file:
        dict_bin_kks = json.load(json_file)
        dict_kks_bin_data.update(dict_bin_kks)


def base_name_svg(svg: str) -> str:
    if svg.startswith('diag_'):
        return svg[5:12]
    else:
        return svg[0:7]


def parsing_svg(svg: str, directory: str) -> None:
    """
    Функция принимающая KKS видеокадра на котором построчно ведется поиск начала кода подмодели. При нахождении кода,
    записывает его построчно во множество set_constructor и запускает функцию add_kks с аргументом set_constructor.
    :param svg: Имя видеокадра формата svg.
    :param directory: Директория в которой хранится папка с видеокадрами.
    :return: None
    """
    with open(path.join(directory, 'NPP_models', f'{svg}'), encoding='windows-1251') as svg_file:
        set_constructor: Set[str] = set()
        flag_constructor = False
        for i_line in svg_file:
            if flag_constructor:
                if re.search(r'<image', i_line):
                    add_kks(set_line_text=set_constructor, svg=base_name_svg(svg=svg))
                    set_constructor.clear()
                    set_constructor.add(i_line)
                else:
                    set_constructor.add(i_line)
            else:
                if re.search(r'<image', i_line):
                    flag_constructor = True
                    set_constructor.add(i_line)
        else:
            add_kks(set_line_text=set_constructor, svg=base_name_svg(svg=svg))


def out_kks_suffix(set_line_text: Set,
                   id_kks: str,
                   id_suffix: str,
                   svg_constructor: str,
                   default_suffix: str = None) -> None:
    """
    Функция, производящая поиск KKS и при отсутствии суффикса ведет поиск суффикс, если его нет, добавляет
    стандартный суффикс.
    :param set_line_text: Список сток с данными подмоделями.
    :param id_kks: Имя параметра в котором ведется поиск KKS.
    :param id_suffix: Имя параметра в котором ведется поиск суффикса.
    :param svg_constructor: Имя подмодели.
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
            if not kks_in_date(i_kks):
                record_comment(kks=i_kks, svg_constructor=svg_constructor)
        elif len(i_kks):
            for i_line in set_line_text:
                if re.search(f'{id_suffix}', i_line):
                    try:
                        suffix = re.findall(r'value="&(quot|apos);(.*).*&(quot|apos);"', i_line)[0][1]
                        new_kks = f'{i_kks}_{suffix}'
                        if not kks_in_date(new_kks):
                            record_comment(kks=new_kks, svg_constructor=svg_constructor)
                    except IndexError:
                        new_kks = f'{i_kks}_{default_suffix}'
                        if not kks_in_date(new_kks):
                            record_comment(kks=new_kks, svg_constructor=svg_constructor)
                    break
            else:
                new_kks = f'{i_kks}_{default_suffix}'
                if not kks_in_date(new_kks):
                    record_comment(kks=new_kks, svg_constructor=svg_constructor)
        else:
            log_info.info(f'ERROR нет привязки на подмодели {svg_constructor}')


def record_comment(kks: str, svg_constructor: str, text: str = 'нет в базе\t') -> None:
    """Добавляет запись о нахождении отсутствующего KKS в базе."""
    number_tyb = '\t' * ceil((24 - len(kks)) / 4)
    text_search_similar_kks = search_similar_kks(kks=kks.partition('_')[0])
    kks_set.add(f'{kks}{number_tyb}{text}{svg_constructor}{text_search_similar_kks}')


def out_kks(set_line_text: Set, id_kks: str, svg_constructor: str) -> None:
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
            if not kks_in_date(i_kks):
                record_comment(kks=i_kks, svg_constructor=svg_constructor)
        elif len(i_kks):
            if i_kks == 'NULL':
                log_info.info(f'ERROR нет привязки на подмодели {svg_constructor}')
            else:
                i_kks = f'{i_kks}_F0'
                if not kks_in_date(i_kks):
                    record_comment(kks=i_kks, svg_constructor=svg_constructor)
        else:
            log_info.info(f'ERROR нет привязки на подмодели {svg_constructor}')


def out_kks_nary(set_line_text: Set,
                 id_kks: str,
                 svg_constructor: str,
                 end_kks: str = 'TE0',
                 flag_teo: bool = True) -> None:
    """
    Функция производящая поиск ккс в подмодели
    :param set_line_text: Список сток с данными подмоделями
    :param id_kks:  Имя параметра в котором ведется поиск KKS
    :param svg_constructor:  Имя подмодели
    :param end_kks:  Окончание сигнала добавляемое в случае его отсутствия
    :param flag_teo:  Флаг, указывающий на добавление в конце KKS окончание TE0
    :return: None
    """
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
        if not kks_in_date(i_kks):
            record_comment(kks=i_kks, svg_constructor=svg_constructor)

    elif i_kks == 'NULL' or i_kks == '':
        for i_line in set_line_text:
            if re.search(r'SIG_', i_line):
                try:
                    i_kks = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
                    if i_kks == 'NULL' or kks_in_date(i_kks):
                        continue
                    else:
                        record_comment(kks=i_kks, svg_constructor=svg_constructor)
                except IndexError:
                    pass

    elif i_kks != 'NULL':
        flag = False
        if kks_in_date(f'{i_kks}_Z0'):
            flag = True
        elif flag_teo:
            if kks_in_date(f'{i_kks}{end_kks}_Z0'):
                flag = True
            else:
                for i_line in set_line_text:
                    if re.search(r'SIG_', i_line):
                        try:
                            suffix = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
                            if kks_in_date(f'{i_kks}_{suffix}'):
                                flag = True
                        except IndexError:
                            pass
        if not flag:
            record_comment(kks=i_kks, svg_constructor=svg_constructor)

    else:
        log_info.info(f'ERROR нет привязки на подмодели {svg_constructor}')


def out_vis_kks_nary(set_line_text: Set, id_kks: str, svg_constructor: str, name_svg: str) -> None:
    """
    Функция производящая поиск ккс в подмодели с использованием части KKS видеокадра если нет полного KKS
    :param set_line_text: Список строк с данными подмоделями
    :param id_kks:  Имя параметра в котором ведется поиск KKS
    :param svg_constructor: Имя подмодели
    :param name_svg: Имя видеокадра
    :return: None
    """
    i_kks = ''
    for i_line in set_line_text:
        if re.search(f'{id_kks}', i_line):
            try:
                i_kks = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
                break
            except IndexError:
                i_kks = re.findall(r'value="PVId_base \+ &quot;([^, ]*).*&quot;"', i_line)[0]
                i_kks = f'{name_svg}{i_kks}'

    if not kks_in_date(f'{i_kks}_F0'):
        record_comment(kks=i_kks, svg_constructor=svg_constructor)
        log_info.info(f'ERROR KKS{i_kks} без привязки на подмодели {svg_constructor}')


def out_some_kks(set_line_text: Set, id_kks: str, svg_constructor: str) -> None:
    """
    Функция производящая поиск ккс в подмодели которая может содержать больше одного KKS.
    :param set_line_text: Список сток с данными подмоделями
    :param id_kks:  Имя параметра в котором ведется поиск KKS
    :param svg_constructor:  Имя подмодели
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
            if not kks_in_date(i_kks):
                record_comment(kks=i_kks, svg_constructor=svg_constructor)


def out_kks_with_te_vl(set_line_text: Set, id_kks: str, svg_constructor: str) -> None:
    """
    Функция производящая поиск ккс в подмодели с подстановкой окончания KKS TE и VL
    :param set_line_text: Список сток с данными подмоделями
    :param id_kks:  Имя параметра в котором ведется поиск KKS
    :param svg_constructor:  Имя подмодели
    :return: None
    """
    for i_line in set_line_text:
        if re.search(f'{id_kks}', i_line):
            try:
                kks = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
                if re.search(r'_', kks):
                    if kks_in_date(kks):
                        return
                    else:
                        record_comment(kks=kks, svg_constructor=svg_constructor)
                elif kks.endswith('TE0') or kks.endswith('VL0'):
                    if kks_in_date(f'{kks}_Z0'):
                        return
                    else:
                        record_comment(kks=kks, svg_constructor=svg_constructor)
                elif kks_in_date(f'{kks}TE0_Z0') or kks_in_date(f'{kks}VL0_Z0'):
                    return
                else:
                    record_comment(kks=kks, svg_constructor=svg_constructor)
            except IndexError:
                log_info.info('В нужной строке не найден KKS')


def add_kks(set_line_text: Set, svg: str) -> None:
    """
    Функция проверяет полученный код подмодели и найдя имя, запускает соответствующую функцию поиска KKS.
    :param set_line_text: Множество строк с кодом подмодели из svg файла.
    :param svg: KKS видеокадра.
    :return: None
    """
    svg_constructor = ''  # имя подмодели
    for i_line in set_line_text:
        if re.search(r'.instr.*', i_line) or \
                re.search(r'.*obj_Button', i_line) or \
                re.search(r'Arm_4', i_line) or \
                re.search(r'unico', i_line) or \
                re.search(r'obj_Station_stat', i_line) or \
                re.search(r'Print', i_line):
            return
        if re.search(r'xlink:href=".*\.svg"', i_line):
            svg_constructor = re.findall(r'xlink:href="(.*\.svg)"', i_line)[0]
            break

    if svg_constructor == '':
        return

    if svg_constructor in ('icon_Notebook.svg', 'icon_regulation.svg', 'icon_call_wf.svg',
                           'obj_address.svg', 'icon_DontTurn.svg', 'aux_ana_bar_h.svg',
                           'obj_EnterText.svg', 'spds_menu_hor_left.svg', 'obj_NodeWS.svg',
                           'bool_checkbox.svg', 'aux_Comm.svg', 'diag_Comm.svg',
                           'aux_RSD_UPPS.svg', 'diag_TimeServer.svg', 'aux_Client.svg',
                           'aux_UPS.svg', 'aux_MKB.svg', 'aux_TimeSync.svg', 'aux_Comm.svg',
                           'spec_I_M_VHR_ShSO.svg', 'ShTK_PL_VHR.svg', 'spec_I_M.svg',
                           'spds_menu_hor_right.svg', 'scroll_bar_v.svg', 'obj_NodeSRV.svg',
                           'spec_I_M.svg', 'spds_menu_hor_right.svg', 'bool_indicator_txt.svg',
                           'bool_indicator.svg', 'icon_OOS.svg', 'icon_DontTurnExt.svg',
                           'Time_of_Change.svg', 'icon_Main.svg', 'icon_Pause.svg',
                           'icon_Repair1.svg', 'icon_Ack.svg', 'icon_Reset.svg',
                           'icon_DontTurnExt.svg', 'icon_Aux_PVs.svg', 'icon_Sel.svg',
                           'bin_msg_txt.svg', 'aux_PRJSPEC_breaker_diag.svg', 'aux_ps_Bel_PRJSPEC_AH_mode_diag.svg',
                           'ps_Bel4_TZ_init.svg', 'ps_Bel4_SKUV_motor.svg', 'ps_Bel4_TPTS_BIN_breaker.svg',
                           'ps_Bel4_SKUEL_disconnector.svg', 'ps_Bel4_SKUEL_breaker.svg', 'icon_call_ws.svg',
                           'ps_Bel4_aux_AH_mode_diag.svg', 'aux_TPTS_EM_diag.svg', 'aux_TPTS_EML_diag.svg',
                           'scroll_list_15.svg', 'icon_overheating.svg', 'ps_Novo2_aux_ES_diag.svg',
                           'aux_TPTS_IBR_diag.svg', 'ps_LAES2_aux_LabRez.svg', 'ps_Bel4_aux_BAR_M_i.svg',
                           'ps_Bel4_aux_BAR0M_r.svg', 'aux_TPTS_IBR_diag.svg', 'ps_Bel4_aux_CoA_r.svg',
                           'ps_Bel4_aux_common_r.svg', 'ps_Bel4_aux_TZi_r.svg', 'ps_Bel4_TZ_req.svg',
                           'scroll_list_10.svg'):
        return

    if svg_constructor in ('ps_Len2_DS_ana.svg', 'DS_ana.svg', 'DS_ana_bar.svg',
                           'DS_ana_bar_h.svg', 'DS_ana_GetLocation.svg', 'ps_LAES2_ana_DoubleBound.svg',
                           'ana_bar_scale.svg'):
        out_kks_suffix(set_line_text=set_line_text,
                       id_kks='FKKS',
                       id_suffix='Suffix',
                       svg_constructor=svg_constructor,
                       default_suffix='XQ01')
        return

    elif svg_constructor == 'DS_TPTS_Reg_degree.svg':
        out_kks_suffix(set_line_text=set_line_text,
                       id_kks='KKS',
                       id_suffix='SIGNAL',
                       svg_constructor=svg_constructor,
                       default_suffix='XQ01')
        return

    elif svg_constructor == 'DS_Reg_degree.svg':
        out_kks_suffix(set_line_text=set_line_text,
                       id_kks='KKS',
                       id_suffix='SIGNAL',
                       svg_constructor=svg_constructor,
                       default_suffix='AA1')
        return

    elif svg_constructor == 'bin_indicator.svg':
        out_kks_suffix(set_line_text=set_line_text,
                       id_kks='PointID',
                       id_suffix='BinMask',
                       svg_constructor=svg_constructor)
        return
    elif svg_constructor == 'spds_csf_block.svg':
        out_kks_suffix(set_line_text=set_line_text,
                       id_kks='LB_Point',
                       id_suffix='Suffix',
                       svg_constructor=svg_constructor)
        return

    elif svg_constructor in ('DS_TNT_HEAD.svg', 'DS_switch.svg', 'DS_T_valve.svg'):
        out_kks(set_line_text=set_line_text,
                id_kks='KKS',
                svg_constructor=svg_constructor)
        return
    elif svg_constructor == 'spds_ana_to_time.svg':
        out_kks(set_line_text=set_line_text,
                id_kks='AnaTime',
                svg_constructor=svg_constructor)
        return

    elif svg_constructor in ('bin_tablo.svg', 'bitwise_tablo_4bits.svg', 'bin_indicator_txt.svg'):
        out_kks(set_line_text=set_line_text,
                id_kks='PointID',
                svg_constructor=svg_constructor)
        return

    elif svg_constructor in ('DS_CO_valve.svg', 'DS_motor.svg', 'DS_TPTS_TE_spec.svg', 'DS_pivot_valve.svg',
                             'DS_Reg_valve.svg', 'DS_CO_valve_rect.svg', 'DS_breaker.svg', 'DS_setter.svg',
                             'DS_TPTS_IBR_set.svg', 'DS_Reg_set.svg'):
        out_kks_nary(set_line_text=set_line_text,
                     id_kks='KKS',
                     svg_constructor=svg_constructor)
        return
    elif svg_constructor == 'DS_TPTS_KO.svg':
        out_kks_nary(set_line_text=set_line_text,
                     id_kks='KKS',
                     svg_constructor=svg_constructor,
                     flag_teo=False)
        return
    elif svg_constructor == 'DS_pulse_valve.svg':
        out_kks_nary(set_line_text=set_line_text,
                     id_kks='KKS',
                     svg_constructor=svg_constructor,
                     flag_teo=True)
        return
    elif svg_constructor in ('DS_TPTS_VL_num.svg', 'DS_TPTS_VL_spec.svg'):
        out_kks_nary(set_line_text=set_line_text,
                     id_kks='KKS',
                     svg_constructor=svg_constructor,
                     end_kks='VL0')
        return

    elif svg_constructor == 'DS_TNT_DM_EXT.svg':
        out_vis_kks_nary(set_line_text=set_line_text,
                         id_kks='KKS',
                         svg_constructor=svg_constructor,
                         name_svg=svg)
        return

    elif svg_constructor in ('bin_mode_1o6.svg', 'DS_TNT_MOD1.svg', 'bin_tablo_flogic.svg',
                             'DS_ana_ext_bounds.svg', 'bin_checkbox.svg', 'bin_tablo_OR3.svg',
                             'DS_TurbValve_control.svg', 'bin_tablo_flogic.svg', 'DS_ana_bar_AKNP.svg',
                             'DS_ana_bar_usr.svg', 'ps_ana_bar_piecewise_lin_log_1.svg', 'ps_NVO_StepNumber.svg',
                             'ps_Len2_ana_AKNP.svg'):
        out_some_kks(set_line_text=set_line_text,
                     id_kks='PointID',
                     svg_constructor=svg_constructor)
        return
    elif svg_constructor in ('spds_timernd.svg', 'spds_timer_csf.svg', 'spds_graph_p_t.svg',
                             'spds_graph_DTs_BLR12.svg', 'spds_menu_vert.svg', 'spds_fb_menu.svg',
                             'DS_pulse3_valve.svg', 'spds_menu_hor_BLR12.svg',
                             'spds_graph_ts1k_BLR12.svg'):
        out_some_kks(set_line_text=set_line_text,
                     id_kks='type=',
                     svg_constructor=svg_constructor)
        return
    elif svg_constructor in ('DS_TurbValve_cutout.svg', 'DS_TurbValve_cutout.svg', 'DS_reflux_valve.svg',
                             'DS_pulse3_valve.svg'):
        out_some_kks(set_line_text=set_line_text,
                     id_kks='SIG',
                     svg_constructor=svg_constructor)
        return
    elif svg_constructor == 'spds_arrow.svg':
        # Сигнал вбивается полностью (наверное). несколько сигналов:
        # arr_col - 1-й сигнал
        # arr_log - 2-й сигнал
        out_some_kks(set_line_text=set_line_text,
                     id_kks='arr',
                     svg_constructor=svg_constructor)
        return

    elif svg_constructor in ('diag_WS_3mon.svg', 'diag_WS_2mon.svg', 'diag_LSD.svg', 'diag_Server.svg',
                             'diag_DTU.svg', 'aux_Server.svg'):
        out_some_kks(set_line_text=set_line_text,
                     id_kks='_PID',
                     svg_constructor=svg_constructor)
        return

    elif svg_constructor == 'spds_tablo.svg':  # Сигнал вбивается полностью
        out_some_kks(set_line_text=set_line_text,
                     id_kks='tab_log',
                     svg_constructor=svg_constructor)
        return
    elif svg_constructor == 'ps_Len2_ANA_Scale.svg' or svg_constructor == 'ps_Kz_Trends.svg':
        out_some_kks(set_line_text=set_line_text,
                     id_kks='FKKS',
                     svg_constructor=svg_constructor)
        return

    elif svg_constructor in ('DS_TPTS_AVR_sel.svg', 'DS_TPTS_TZB_universal.svg', 'DS_TPTS_nakladka.svg'):
        out_kks_with_te_vl(set_line_text=set_line_text,
                           id_kks='KKS',
                           svg_constructor=svg_constructor)
        return

    elif svg_constructor in ('GW.svg', 'TNT_indic_tips.svg', 'obj_Button.svg', 'ps_Blr_MotorStatistics.svg'):
        return
    else:
        log_info.info(f'--------> Найдена необрабатываемая подмодель {svg_constructor}')
        return


@timer
def new_start_parsing_svg_files(svg: List, directory: str) -> None:
    set_kks_bin_date.clear()
    set_kks_ana_date.clear()
    dict_kks_bin_data.clear()
    dict_kks_ana_data.clear()

    add_date(directory=directory)

    numbers = len(svg)
    number = 1
    for i_svg in svg:
        text_log = f'[{number}/{numbers}]\t Проверка {i_svg}'
        if i_svg.endswith('.svg') or i_svg.endswith('.SVG'):
            parsing_svg(svg=i_svg, directory=directory)
            list_error_kks: Set = set()
            number_errors = 0
            for i_kks in kks_set:
                if re.search('_', i_kks):
                    kks = i_kks
                    if kks in set_kks_ana_date:
                        continue
                    elif kks in set_kks_bin_date:
                        continue
                    else:
                        list_error_kks.add(i_kks)
                else:
                    if f'{i_kks}.svg' in svg or f'{i_kks}.SVG' in svg:
                        continue
                    kks_1 = f'{i_kks}_F0'
                    kks_2 = f'{i_kks}_XQ01'
                    if kks_1 in set_kks_ana_date or kks_2 in set_kks_ana_date:
                        continue
                    elif kks_1 in set_kks_bin_date or kks_2 in set_kks_bin_date:
                        continue
                    else:
                        list_error_kks.add(i_kks)
            if len(list_error_kks):
                check_directory(path_directory=directory,
                                name_directory='Замечания по видеокадрам')
                with open(path.join(directory, 'Замечания по видеокадрам', f'{i_svg[:-4]}.txt'),
                          'w', encoding='utf-8') as file:
                    for i_kks in list_error_kks:
                        file.write(f'{i_kks}\n')
                        number_errors += 1
            kks_set.clear()
            text_log = f'{text_log:<55}Кривых KKS: {number_errors}'
        else:
            text_log = f'{text_log:<55}Файл {i_svg} не svg!'
        log_info_print.info(text_log)
        number += 1


def database_update(directory: str) -> None:
    """
    Функция обновления из исходных данных базы сигналов (ANA и BIN).
    :return: None
    """
    if directory != '0':
        log_info_print.info(f'Старт обновления базы дынных сигналов {directory}')
        new_date(name_directory=directory)
        log_info_print.info(f'База {directory} обновлена успешно')
        input('Enter для продолжения ')


def checking_svg_files(directory: str) -> None:
    """
    Функция запускающая поиск неверных привязок на видеокадрах соответствующей системы.
    :return: None
    """
    if directory != '0':
        list_svg = listdir(path.join(directory, 'NPP_models'))
        log_info_print.info(f'Старт проверки видеокадров {directory}')
        new_start_parsing_svg_files(svg=list_svg, directory=directory)
        input('Поиск завершен.. Для продолжения нажмите Enter\n')


def actualizations_vk(directory: str) -> None:
    """
    Функция проверяет в указанной директории папки NPP_models и NPP_models_new. Если в папке NPP_models_new есть
    видеокадры новее чем в папке NPP_models, копирует с заменой видеокадра из папки NPP_models_new в папку NPP_models.
    :param directory: Папка системы в которой ведется сравнение и замена файлов.
    :return: None
    """
    if directory != '0':
        set_npp_models = listdir(path.join(directory, 'NPP_models'))
        try:
            set_new_npp_models = listdir(path.join(directory, 'NPP_models_new'))
        except FileNotFoundError:
            log_info_print.info('Нет папки NPP_models_new с новыми видеокадрами')
            check_directory(path_directory=directory, name_directory='NPP_models_new')
            print('Папка NPP_models_new создана. Загрузите в нее актуальные видеокадры и попробуйте еще раз.')
            input('Enter для завершения')
            return

        log_info_print.info(f'Старт обновления видеокадров {directory}')
        number = 0
        len_number_svg = len(set_npp_models)
        for i_svg in set_npp_models:
            number += 1
            print(f'[{number}/{len_number_svg}]', end='\t')
            if i_svg in set_new_npp_models:
                shutil.copy2(path.join(directory, 'NPP_models_new', i_svg),
                             path.join(directory, 'NPP_models', i_svg))
                print(f'+++{i_svg} видеокадр обновлен+++')
                log_info.info(f'+++{i_svg} видеокадр обновлен+++')
            else:
                print(f'Видеокадра {i_svg} нет в папке NPP_models_new. Обновление невозможно.')
                log_info.info(f'Видеокадра {i_svg} нет в папке NPP_models_new. Обновление невозможно.')
        input('Enter для продолжения ')


def system_selection(text: str) -> str:
    """
    Функция выбора системы с которой работать.
    :return: None
    """
    while True:
        name_system = input(f'{text}\n'
                            f'1 - SVBU_1\n'
                            f'2 - SVBU_2\n'
                            f'3 - SKU_VP_1\n'
                            f'4 - SKU_VP_2\n'
                            f'5 - SVSU\n'
                            f'[0] - выйти\n'
                            f' -> ')
        if name_system == '1':
            return 'SVBU_1'
        elif name_system == '2':
            return 'SVBU_2'
        elif name_system == '3':
            return 'SKU_VP_1'
        elif name_system == '4':
            return 'SKU_VP_2'
        elif name_system == '5':
            return 'SVSU'
        elif name_system == '0' or name_system == '':
            return '0'
        else:
            print('Ошибка. Нет такого ответа.\n')


def sorting_notes_files(directory: str) -> None:
    """
    Функция запускающая распределение файлов с замечаниями согласно списку принадлежности к группе.
    :return: None
    """
    if directory != '0':
        log_info_print.info(f'Старт распределения файлов с замечаниями {directory} '
                            f'согласно списку принадлежности к группе')
        vis_groups = dict_loading(number_bloc=directory)
        if len(vis_groups):
            sort_files_into_groups(number_bloc=directory, group_svg=vis_groups)
            log_info_print.info('Распределено успешно')
        else:
            log_info_print.info('Распределение невозможно')
        input('Enter для продолжения ')


def start_program_parsing_svg() -> None:
    """
    Меню выбора действия.
    :return: None
    """
    system('cls')
    while True:
        user_response = input('Программа поиска замечаний на ВК\n'
                              '1. Обновить базу сигналов\n'
                              '2. Обновить видеокадры\n'
                              '3. Поиск отсутствующих привязок на видеокадрах\n'
                              '4. Распределить замечания видеокадров по группам\n'
                              '[0]. Выйти из программы\n'
                              ' -> ')
        if user_response == '1':
            system('cls')
            directory = system_selection(text='Где обновляем базу данных?')
            database_update(directory=directory)
            system('cls')
        elif user_response == '2':
            system('cls')
            directory = system_selection(text='Какие видеокадры требуется обновить?')
            actualizations_vk(directory=directory)
            system('cls')
        elif user_response == '3':
            system('cls')
            directory = system_selection(text='На каких видеокадрах ищем замечания?')
            checking_svg_files(directory=directory)
            system('cls')
        elif user_response == '4':
            system('cls')
            directory = system_selection(text='Какие замечания распределить по группам?')
            sorting_notes_files(directory=directory)
            system('cls')
        elif user_response == '0' or user_response == '':
            system('cls')
            return
        else:
            system('cls')
            print('Нет такого варианта')


if __name__ == '__main__':
    pass
