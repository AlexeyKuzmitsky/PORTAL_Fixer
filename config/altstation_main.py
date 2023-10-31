from os import chdir, listdir, path, system
import re
from typing import List, Set
from csv import reader
from .get_logger import log_info_print, log_info
from .timer import timer


set_kks_bin_date: Set[str] = set()  # список ккс сигналов BIN из базы
set_kks_ana_date: Set[str] = set()  # список ккс сигналов ANA из базы


def kks_in_date(kks: str, name_svg: str = '') -> bool:
    """
    Функция выполняющая проверку наличия KKS в базе данных. При нахождении сигнала в базе возвращает True, иначе False
    :param kks: KKS проверяемого сигнала
    :param name_svg: Имя видеокадра
    :return: bool (True, False)
    """
    if kks in set_kks_ana_date:
        analog_signal_setpoint_search(kks=kks[:-5], name_svg=name_svg)
        # log_info_print.info(f'Найден ккс {kks}. Есть в базе ANA')
        return True
    elif kks in set_kks_bin_date:
        # log_info_print.info(f'Найден ккс {kks}. Есть в базе BIN')
        return True
    else:
        # log_info_print.info(f'Найден ккс {kks}. !!!!!!!!!!!!НЕТ В БАЗЕ!!!!!!!!!!!!')
        return False


def analog_signal_setpoint_search(kks: str, name_svg: str) -> None:
    """
    Функция поиска в базе дынных бинарных уставок с конкретными суффиксами.
    :param kks: KKS к которому будут подставляться суффиксы.
    :param name_svg: Имя видеокадра.
    :return: None
    """
    list_suffix = ['XH01', 'XH03', 'XH05', 'XH52', 'XH54', 'XH56',
                   'XH41', 'XH43', 'XH45', 'XH92', 'XH94', 'XH96', 'XH98']

    for i_suffix in list_suffix:
        if kks_in_date(f'{kks}_{i_suffix}'):
            with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                file_alt_station.write(f'{kks}_{i_suffix}\t{name_svg}\n')


@timer
def new_date(number_block: str) -> None:
    """
    Функция обновления файлов со списком KKS сигналов. По завершению обновляются (создаются если не было) 2 файла:
    BIN_list_kks.txt со списком бинарных сигналов
    ANA_list_kks.txt со списков аналоговых сигналов
    :param number_block: папка в которой будут обновления
    :return: None
    """
    set_kks_bin_date.clear()
    set_kks_ana_date.clear()

    log_info_print.info('Сбор BIN сигналов')
    with open(path.join(number_block, 'DbDumps', 'PLS_BIN_CONF.dmp'), 'r', encoding='windows-1251') as file:
        new_text = reader(file, delimiter='|', quotechar=' ')
        for i_line in new_text:
            try:
                set_kks_bin_date.add(i_line[42])
            except IndexError:
                pass

    with open(path.join(number_block, 'data', 'BIN_list_kks.txt'), 'w', encoding='UTF-8') as file:
        for i_kks in set_kks_bin_date:
            file.write(f'{i_kks}\n')
    log_info_print.info('Accesses. Сигналы BIN собраны успешно')

    log_info_print.info('Сбор ANA сигналов')
    with open(path.join(number_block, 'DbDumps', 'PLS_ANA_CONF.dmp'), 'r', encoding='windows-1251') as file:
        new_text = reader(file, delimiter='|', quotechar=' ')
        for i_line in new_text:
            try:
                set_kks_ana_date.add(i_line[78])
            except IndexError:
                pass

    with open(path.join(number_block, 'data', 'ANA_list_kks.txt'), 'w', encoding='UTF-8') as file:
        for i_kks in set_kks_ana_date:
            file.write(f'{i_kks}\n')
    log_info_print.info('Accesses. Сигналы ANA собраны успешно')


def add_date() -> None:
    """
    Функция считывающая базу сигналов
    :return: None
    """
    with open(path.join('data', 'ANA_list_kks.txt')) as file:
        for i_line in file:
            set_kks_ana_date.add(i_line[:-1])

    with open(path.join('data', 'BIN_list_kks.txt')) as file:
        for i_line in file:
            set_kks_bin_date.add(i_line[:-1])


def base_name_svg(svg: str) -> str:
    if svg.startswith('diag_'):
        return svg[5:12]
    else:
        return svg[0:7]


def parsing_svg(svg: str, flag: bool = False, list_kks: Set = None) -> None:
    """
    Функция принимающая KKS видеокадра на котором построчно ведется поиск начала кода подмодели. При нахождении кода,
    записывает его построчно во множество set_constructor и запускает функцию add_kks с аргументом set_constructor.
    :param svg: Имя видеокадра.
    :param flag: Флаг отвечающий за режим работы функции.
    Если True - ведется поиск KKS видеокадров,
    если False - ведется поиск KKS сигналов.
    :param list_kks: Объект используемый для записи найденных KKS видеокадров.
    :return: None
    """
    log_info_print.info('Проверка {:<40}'.format(svg))
    with open(path.join('NPP_models', f'{svg}'), encoding='windows-1251') as svg_file:
        set_constructor: Set[str] = set()
        flag_constructor = False
        for i_line in svg_file:
            if flag_constructor:
                if re.search(r'<image', i_line):
                    if flag:
                        name_svg = add_video_frames(set_line_text=set_constructor)
                        if name_svg != '':
                            list_kks.add(name_svg)
                    else:
                        add_kks(set_line_text=set_constructor, name_svg=svg[:-4])
                    set_constructor.clear()
                    set_constructor.add(i_line)
                else:
                    set_constructor.add(i_line)
            else:
                if re.search(r'<image', i_line):
                    flag_constructor = True
                    set_constructor.add(i_line)


def out_kks_suffix(set_line_text: Set,
                   id_kks: str,
                   id_suffix: str,
                   name_svg: str,
                   default_suffix: str = None) -> None:
    """
    Функция, производящая поиск KKS и при отсутствии суффикса ведет поиск суффикс, если его нет, добавляет
    стандартный суффикс.
    :param set_line_text: Список сток с данными подмоделями.
    :param id_kks: Имя параметра в котором ведется поиск KKS.
    :param id_suffix: Имя параметра в котором ведется поиск суффикса.
    :param name_svg: Имя видеокадра.
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
            if kks_in_date(kks=i_kks, name_svg=name_svg):
                with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                    file_alt_station.write(f'{i_kks}\t{name_svg}\n')
        elif len(i_kks):

            for i_line in set_line_text:
                if re.search(f'{id_suffix}', i_line):
                    try:
                        suffix = re.findall(r'value="&(quot|apos);(.*).*&(quot|apos);"', i_line)[0][1]
                        new_kks = f'{i_kks}_{suffix}'
                        if kks_in_date(kks=i_kks, name_svg=name_svg):
                            with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                                file_alt_station.write(f'{new_kks}\t{name_svg}\n')
                            return
                    except IndexError:
                        break
            new_kks = f'{i_kks}_{default_suffix}'
            log_info.info(f'Суффикса нет, добавлен {default_suffix}: {new_kks}')
            if kks_in_date(kks=new_kks, name_svg=name_svg):
                with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                    file_alt_station.write(f'{new_kks}\t{name_svg}\n')


def out_kks(set_line_text: Set, id_kks: str, name_svg: str) -> None:
    """
    Функция производящая поиск ккс в подмодели.
    :param set_line_text: Список сток с данными подмоделями.
    :param id_kks:  Имя параметра в котором ведется поиск KKS.
    :param name_svg: Имя видеокадра.
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
            if kks_in_date(kks=i_kks, name_svg=name_svg):
                with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                    file_alt_station.write(f'{i_kks}\t{name_svg}\n')
        elif len(i_kks):
            if i_kks == 'NULL':
                pass
            else:
                i_kks = f'{i_kks}_F0'
                if kks_in_date(kks=i_kks, name_svg=name_svg):
                    with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                        file_alt_station.write(f'{i_kks}\t{name_svg}\n')


def out_kks_nary(set_line_text: Set,
                 id_kks: str,
                 name_svg: str,
                 end_kks: str = 'TE0',
                 flag_teo: bool = True,) -> None:
    """
    Функция производящая поиск ккс в подмодели.
    :param set_line_text: Список сток с данными подмоделями.
    :param id_kks:  Имя параметра в котором ведется поиск KKS.
    :param name_svg: Имя видеокадра.
    :param end_kks:  Окончание сигнала добавляемое в случае его отсутствия.
    :param flag_teo:  Флаг, указывающий на добавление в конце KKS окончание TE0.
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
        if kks_in_date(kks=i_kks, name_svg=name_svg):
            with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                file_alt_station.write(f'{i_kks}\t{name_svg}\n')

    elif i_kks == 'NULL' or i_kks == '':
        for i_line in set_line_text:
            if re.search(r'SIG_', i_line):
                try:
                    i_kks = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
                    if i_kks == 'NULL':
                        continue
                    elif kks_in_date(kks=i_kks, name_svg=name_svg):
                        with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                            file_alt_station.write(f'{i_kks}\t{name_svg}\n')
                except IndexError:
                    pass

    elif i_kks != 'NULL':
        if kks_in_date(kks=f'{i_kks}_Z0', name_svg=name_svg):
            with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                file_alt_station.write(f'{i_kks}_Z0\t{name_svg}\n')
        elif flag_teo:
            if kks_in_date(kks=f'{i_kks}{end_kks}_Z0', name_svg=name_svg):
                with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                    file_alt_station.write(f'{i_kks}{end_kks}_Z0\t{name_svg}\n')
            else:
                for i_line in set_line_text:
                    if re.search(r'SIG_', i_line):
                        suffix = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
                        if kks_in_date(kks=f'{i_kks}_{suffix}', name_svg=name_svg):
                            with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                                file_alt_station.write(f'{i_kks}_{suffix}\t{name_svg}\n')


def out_vis_kks_nary(set_line_text: Set, id_kks: str, name_svg: str) -> None:
    """
    Функция производящая поиск ккс в подмодели с использованием части KKS видеокадра если нет полного KKS.
    :param set_line_text: Список строк с данными подмоделями.
    :param id_kks:  Имя параметра в котором ведется поиск KKS.
    :param name_svg: Имя видеокадра.
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
                i_kks = f'{base_name_svg(name_svg)}{i_kks}'

    if kks_in_date(kks=f'{i_kks}_F0', name_svg=name_svg):
        with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
            file_alt_station.write(f'{i_kks}_F0\t{name_svg}\n')


def out_some_kks(set_line_text: Set, id_kks: str, name_svg: str) -> None:
    """
    Функция производящая поиск ккс в подмодели которая может содержать больше одного KKS.
    :param set_line_text: Список строк с данными подмоделями.
    :param id_kks:  Имя параметра в котором ведется поиск KKS.
    :param name_svg: Имя видеокадра.
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

    for i_kks in kks_list:
        if re.search(r'_', i_kks):
            if kks_in_date(kks=i_kks, name_svg=name_svg):
                with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                    file_alt_station.write(f'{i_kks}\t{name_svg}\n')


def out_kks_with_te_vl(set_line_text: Set, id_kks: str, name_svg: str) -> None:
    """
    Функция производящая поиск ккс в подмодели с подстановкой окончания KKS TE и VL.
    :param set_line_text: Список строк с данными подмоделями.
    :param id_kks:  Имя параметра в котором ведется поиск KKS.
    :param name_svg: Имя видеокадра.
    :return: None
    """
    for i_line in set_line_text:
        if re.search(f'{id_kks}', i_line):
            try:
                kks = re.findall(r'value="&quot;([^, ]*).*&quot;"', i_line)[0]
                if re.search(r'_', kks):
                    if kks_in_date(kks):
                        with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                            file_alt_station.write(f'{kks}\t{name_svg}\n')
                elif kks.endswith('TE0') or kks.endswith('VL0'):
                    if kks_in_date(f'{kks}_Z0'):
                        with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                            file_alt_station.write(f'{kks}_Z0\t{name_svg}\n')
                elif kks_in_date(f'{kks}TE0_Z0') or kks_in_date(f'{kks}VL0_Z0'):
                    with open('altStation.dic', 'a', encoding='windows-1251') as file_alt_station:
                        file_alt_station.write(f'{kks}TE0_Z0\t{name_svg}\n')
            except IndexError:
                log_info.info('В нужной строке не найден KKS')


def add_kks(set_line_text: Set, name_svg: str) -> None:
    """
    Функция проверяет полученный код подмодели и найдя имя, запускает соответствующую функцию поиска KKS.
    :param set_line_text: Множество строк с кодом подмодели из svg файла.
    :param name_svg: Имя видеокадра.
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
                           'spec_I_M_VHR_ShSO.svg', 'ShTK_PL_VHR.svg'):
        return

    if svg_constructor in ('ps_Len2_DS_ana.svg', 'DS_ana.svg', 'DS_ana_bar.svg',
                           'DS_ana_bar_h.svg', 'DS_ana_GetLocation.svg', 'ps_LAES2_ana_DoubleBound.svg',
                           'ana_bar_scale.svg'):
        out_kks_suffix(set_line_text=set_line_text,
                       id_kks='FKKS',
                       id_suffix='Suffix',
                       name_svg=name_svg,
                       default_suffix='XQ01')
        return

    elif svg_constructor in ('DS_Reg_degree.svg', 'DS_TPTS_Reg_degree.svg'):
        out_kks_suffix(set_line_text=set_line_text,
                       id_kks='KKS',
                       id_suffix='SIGNAL',
                       name_svg=name_svg,
                       default_suffix='XQ01')
        return

    elif svg_constructor == 'bin_indicator.svg':
        out_kks_suffix(set_line_text=set_line_text,
                       id_kks='PointID',
                       id_suffix='BinMask',
                       name_svg=name_svg)
        return
    elif svg_constructor == 'spds_csf_block.svg':
        out_kks_suffix(set_line_text=set_line_text,
                       id_kks='LB_Point',
                       id_suffix='Suffix',
                       name_svg=name_svg)
        return

    elif svg_constructor in ('DS_TNT_HEAD.svg', 'DS_switch.svg', 'DS_T_valve.svg'):
        out_kks(set_line_text=set_line_text,
                id_kks='KKS',
                name_svg=name_svg)
        return
    elif svg_constructor == 'spds_ana_to_time.svg':
        out_kks(set_line_text=set_line_text,
                id_kks='AnaTime',
                name_svg=name_svg)
        return

    elif svg_constructor in ('bin_tablo.svg', 'bitwise_tablo_4bits.svg', 'bin_indicator_txt.svg'):
        out_kks(set_line_text=set_line_text,
                id_kks='PointID',
                name_svg=name_svg)
        return

    elif svg_constructor in ('DS_CO_valve.svg', 'DS_motor.svg', 'DS_TPTS_TE_spec.svg', 'DS_pivot_valve.svg',
                             'DS_Reg_valve.svg', 'DS_CO_valve_rect.svg', 'DS_breaker.svg', 'DS_setter.svg',
                             'DS_TPTS_IBR_set.svg', 'DS_Reg_set.svg'):
        out_kks_nary(set_line_text=set_line_text,
                     id_kks='KKS',
                     name_svg=name_svg)
        return
    elif svg_constructor == 'DS_TPTS_KO.svg':
        out_kks_nary(set_line_text=set_line_text,
                     id_kks='KKS',
                     flag_teo=False,
                     name_svg=name_svg)
        return
    elif svg_constructor == 'DS_pulse_valve.svg':
        out_kks_nary(set_line_text=set_line_text,
                     id_kks='KKS',
                     flag_teo=True,
                     name_svg=name_svg)
        return
    elif svg_constructor in ('DS_TPTS_VL_num.svg', 'DS_TPTS_VL_spec.svg'):
        out_kks_nary(set_line_text=set_line_text,
                     id_kks='KKS',
                     end_kks='VL0',
                     name_svg=name_svg)
        return

    elif svg_constructor == 'DS_TNT_DM_EXT.svg':
        out_vis_kks_nary(set_line_text=set_line_text,
                         id_kks='KKS',
                         name_svg=name_svg)
        return

    elif svg_constructor in ('bin_mode_1o6.svg', 'DS_TNT_MOD1.svg', 'bin_tablo_flogic.svg',
                             'DS_ana_ext_bounds.svg', 'bin_checkbox.svg', 'bin_tablo_OR3.svg',
                             'DS_TurbValve_control.svg', 'bin_tablo_flogic.svg', 'DS_ana_bar_AKNP.svg',
                             'DS_ana_bar_usr.svg', 'ps_ana_bar_piecewise_lin_log_1.svg', 'ps_NVO_StepNumber.svg',
                             'ps_Len2_ana_AKNP.svg'):
        out_some_kks(set_line_text=set_line_text,
                     id_kks='PointID',
                     name_svg=name_svg)
        return
    elif svg_constructor in ('spds_timernd.svg', 'spds_timer_csf.svg', 'spds_graph_p_t.svg',
                             'spds_graph_DTs_BLR12.svg', 'spds_menu_vert.svg', 'spds_fb_menu.svg',
                             'DS_pulse3_valve.svg', 'spds_menu_hor_BLR12.svg',
                             'spds_graph_ts1k_BLR12.svg'):  # 'DS_reflux_valve.svg',
        out_some_kks(set_line_text=set_line_text,
                     id_kks='type=',
                     name_svg=name_svg)
        return
    elif svg_constructor in ('DS_TurbValve_cutout.svg', 'DS_TurbValve_cutout.svg', 'DS_reflux_valve.svg'
                             'DS_pulse3_valve.svg'):
        out_some_kks(set_line_text=set_line_text,
                     id_kks='SIG',
                     name_svg=name_svg)
        return
    elif svg_constructor == 'spds_arrow.svg':
        # Сигнал вбивается полностью (наверное). Несколько сигналов:
        # arr_col - 1-й сигнал
        # arr_log - 2-й сигнал
        out_some_kks(set_line_text=set_line_text,
                     id_kks='arr',
                     name_svg=name_svg)
        return

    elif svg_constructor in ('diag_WS_3mon.svg', 'diag_WS_2mon.svg', 'diag_LSD.svg', 'diag_Server.svg',
                             'diag_DTU.svg', 'aux_Server.svg'):
        out_some_kks(set_line_text=set_line_text,
                     id_kks='_PID',
                     name_svg=name_svg)
        return

    elif svg_constructor == 'spds_tablo.svg':  # Сигнал вбивается полностью
        out_some_kks(set_line_text=set_line_text,
                     id_kks='tab_log',
                     name_svg=name_svg)
        return
    elif svg_constructor == 'ps_Len2_ANA_Scale.svg' or svg_constructor == 'ps_Kz_Trends.svg':
        out_some_kks(set_line_text=set_line_text,
                     id_kks='FKKS',
                     name_svg=name_svg)
        return

    elif svg_constructor in ('DS_TPTS_AVR_sel.svg', 'DS_TPTS_TZB_universal.svg', 'DS_TPTS_nakladka.svg'):
        out_kks_with_te_vl(set_line_text=set_line_text,
                           id_kks='KKS',
                           name_svg=name_svg)
        return

    elif svg_constructor in ('GW.svg', 'TNT_indic_tips.svg', 'obj_Button.svg', 'ps_Blr_MotorStatistics.svg'):
        return
    else:
        log_info.info(f'--------> Найдена необрабатываемая подмодель {svg_constructor}')
        return


@timer
def new_start_parsing_svg_files(svg: List, flag: bool) -> None:
    set_kks_bin_date.clear()
    set_kks_ana_date.clear()

    add_date()
    list_svg_obj_station_stat = list()  # список видеокадров на которых есть подмодель obj_Station_stat.svg
    set_svg_obj_station_stat = set()  # список видеокадров на которые ссылаются все подмодели obj_Station_stat.svg
    numbers = len(svg)

    if flag:
        number = 1
        print('Поиск видеокадров на которых содержится подмодель obj_Station_stat.svg')
        for i_svg in svg:
            text_log = '{:11}'.format(f'\r[{number} из {numbers}]')
            print(text_log, end='')
            if i_svg.endswith('.svg') or i_svg.endswith('.SVG'):
                if search_obj_station_stat(name_svg=i_svg):
                    list_svg_obj_station_stat.append(i_svg)
            number += 1
        print('\r')
        print(f'\nПоиск завершен. Найдено {len(list_svg_obj_station_stat)} видеокадров\n')

        number = 1
        numbers = len(list_svg_obj_station_stat)
        print('Поиск видеокадров на которые ссылаются подмодели obj_Station_stat.svg')
        for i_svg in list_svg_obj_station_stat:
            text_log = '{:11}'.format(f'\r[{number} из {numbers}]')
            print(text_log, end='')
            parsing_svg(svg=i_svg, flag=True, list_kks=set_svg_obj_station_stat)
            number += 1
        numbers = len(set_svg_obj_station_stat)
        print(f'\nПоиск завершен. Найдено {numbers} видеокадров')
    else:
        set_svg_obj_station_stat = svg

    number = 1
    for i_svg in sorted(set_svg_obj_station_stat):
        text_log = '{:11}'.format(f'\r[{number} из {numbers}]')
        print(text_log, end='')
        try:
            parsing_svg(svg=f'{i_svg}.svg')
        except FileNotFoundError:
            try:
                parsing_svg(svg=f'{i_svg}')
            except FileNotFoundError:
                log_info_print.info(f'Ссылка на несуществующий видеокадр({i_svg}).')
        number += 1
    print()


def search_obj_station_stat(name_svg: str) -> bool:
    """
    Функция поиска использования видеокадром подмодели obj_Station_stat.svg.
    :param name_svg: Имя видеокадра.
    :return: True при наличии подмодели, False при отсутствии.
    """
    with open(path.join('NPP_models', name_svg), 'r', encoding='windows-1251') as file_svg:
        for i_line in file_svg:
            if 'obj_Station_stat.svg' in i_line:
                return True
    return False


def database_update() -> None:
    """
    Функция обновления из исходных данных базы сигналов (ANA и BIN).
    :return: None
    """
    dict_directory = {'1': 'SVBU_1',
                      '2': 'SVBU_2',
                      '3': 'SKU_VP_1',
                      '4': 'SKU_VP_2'}
    while True:
        user_response = input('Обновить базу сигналов?\n'
                              '1 - обновить 1-й блок\n'
                              '2 - обновить 2-й блок\n'
                              '[0] - выйти\n'
                              ' -> ')
        if user_response in ('1', '2'):
            log_info_print.info(f'Старт обновления базы дынных сигналов {dict_directory[user_response]} блока')
            new_date(number_block=dict_directory[user_response])
            log_info_print.info(f'База {dict_directory[user_response]} блока обновлена успешно')
        elif user_response == '0' or user_response == '':
            return
        else:
            print('Нет такого ответа.')


def add_video_frames(set_line_text) -> str:
    svg_constructor = ''
    for i_line in set_line_text:
        if re.search(r'xlink:href=".*\.svg"', i_line):
            svg_constructor = re.findall(r'xlink:href="(.*\.svg)"', i_line)[0]
            break
    if svg_constructor == 'obj_Station_stat.svg':
        for i_line in set_line_text:
            if re.search('OnClick', i_line):
                try:
                    name_vis = re.findall(r'&quot;([^, &]*).*&quot;', i_line)[0]
                    return name_vis
                except IndexError:
                    return ''
    return ''


def checking_svg_files() -> None:
    """
    Функция запускающая сбор файла Alt-station на видеокадрах соответствующего блока.
    :return: None
    """
    dict_directory = {'1': 'SVBU_1',
                      '2': 'SVBU_2',
                      '3': 'SKU_VP_1',
                      '4': 'SKU_VP_2'}
    while True:
        user_response = input('Alt-station какого блока собираем?\n'
                              '1 - 1-й блок с видеокадров на которе есть ссылки (1+ - 1-й блок со всех видеокадров)\n'
                              '2 - 2-й блок с видеокадров на которе есть ссылки (2+ - 2-й блок со всех видеокадров)\n'
                              '[0] - выйти\n'
                              ' -> ')
        if user_response in ('1', '2', '1+', '2+'):
            chdir(dict_directory[user_response[:1]])  # смена папки работы программы
            break
        elif user_response == '0' or user_response == '':
            return
        else:
            print('Нет такого варианта')

    list_svg = listdir('NPP_models')

    with open('log.txt', 'w', encoding='UTF-8') as log_file:
        log_file.write(f'Старт сбора Alt-station на видеокадрах блока {user_response}')

    with open('altStation.dic', 'w', encoding='windows-1251'):
        pass

    log_info_print.info(f'Старт сбора Alt-station на видеокадрах блока {user_response}')
    if len(user_response) == 2:
        new_start_parsing_svg_files(svg=list_svg, flag=False)
    else:
        new_start_parsing_svg_files(svg=list_svg, flag=True)
    chdir('..')  # смена директории работы программы на одну выше
    log_info_print.info(f'Сбор Alt-station завершен.')
    input('Для продолжения нажмите Enter\n')


def run_the_program_to_create_alt_stations() -> None:
    """
    Меню выбора действия.
    :return: None
    """
    system('cls')
    while True:
        user_response = input('Программа создания alt_stations\n'
                              '1. Обновить базу сигналов\n'
                              '2. Создание Alt-station из svg файлов\n'
                              '[0]. Выйти из программы\n'
                              ' -> ')
        if user_response == '1':
            system('cls')
            database_update()
            system('cls')
        elif user_response == '2':
            system('cls')
            checking_svg_files()
            system('cls')
        elif user_response == '0' or user_response == '':
            system('cls')
            return
        else:
            system('cls')
            print('Нет такого варианта')


if __name__ == '__main__':
    pass
