import re
import json
from config.general_functions import check_directory, check_file
import interface.searching_for_signals_in_submodels as submodels
# from interface.searching_for_signals_in_submodels import base_name_svg
from interface.window_name_system import NameSystemWindow
from csv import reader

import interface.conf as conf
from config.point_description import AnchorPoint
from os import getcwd, path, listdir, rename, remove
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextBrowser, QLabel, QMessageBox

import shutil
from typing import Set, Dict, List
from qasync import asyncSlot


class ParsingSvg(QMainWindow):
    def __init__(self, main_menu):  # изменим начальные настройки
        super().__init__()  # получим доступ к изменениям настроек
        self.setWindowTitle(f'{conf.name_program} - v.{conf.version_program}')  # изменим текст заглавия
        self.setMinimumSize(QSize(750, 350))  # Устанавливаем минимальный размер окна 750(ширина) на 350(высота)
        self.setWindowIcon(QIcon(path.join('image', 'icon.png')))

        self.main_menu = main_menu
        font = QFont()
        font.setFamily('MS Shell Dlg 2')
        font.setPointSize(12)

        layout = QVBoxLayout()

        self.btn_update_vis_svbu = QPushButton('Обновить видеокадры SVBU')
        self.btn_update_vis_svbu.setMinimumHeight(50)
        self.btn_update_vis_svbu.setFont(font)
        self.btn_update_vis_svbu.clicked.connect(self.update_vis_svbu)
        layout.addWidget(self.btn_update_vis_svbu)  # добавить кнопку на подложку для виджетов

        self.btn_update_data_sig = QPushButton('Обновление баз данных сигналов')
        self.btn_update_data_sig.setMinimumHeight(50)
        self.btn_update_data_sig.setFont(font)
        self.btn_update_data_sig.clicked.connect(self.update_data_system)
        layout.addWidget(self.btn_update_data_sig)  # добавить кнопку на подложку для виджетов

        self.btn_parsing_svg = QPushButton('Поиск замечаний на видеокадрах')
        self.btn_parsing_svg.setMinimumHeight(50)
        self.btn_parsing_svg.setFont(font)
        self.btn_parsing_svg.clicked.connect(self.start_parsing_svg)
        layout.addWidget(self.btn_parsing_svg)  # добавить кнопку на подложку для виджетов

        self.text_log = QTextBrowser()
        layout.addWidget(self.text_log)  # добавить QTextBrowser на подложку для виджетов

        self.btn_main_menu = QPushButton('Вернуться в главное меню')
        self.btn_main_menu.setMinimumHeight(50)
        self.btn_main_menu.setFont(font)
        self.btn_main_menu.clicked.connect(self.main_menu_window)  # задать действие при нажатии
        layout.addWidget(self.btn_main_menu)  # добавить кнопку на подложку для виджетов

        self.name_system_vk = NameSystemWindow(func=self.actualizations_vk_svbu,
                                               text='Видеокадры какого блока обновить?',
                                               set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        self.update_data = NameSystemWindow(func=self.new_data_ana_bin_nary,
                                            text='Базу какой из систем обновить?',
                                            set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        self.name_system_parsing_svg = NameSystemWindow(func=self.checking_svg_files,
                                                        text='На каких видеокадрах найти замечания?',
                                                        set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        # self.name_system_distribution = NameSystemWindow(func=self.start_svsu_import,
        #                                                  text='Для какой системы распределить замечания?',
        #                                                  set_name_system={'SVSU', 'SVBU_1', 'SVBU_2'})

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)  # Разместим подложку в окне

    def update_vis_svbu(self):
        self.name_system_vk.show()

    def update_data_system(self):
        self.update_data.show()

    def start_parsing_svg(self):
        self.name_system_parsing_svg.show()

    def main_menu_window(self):
        self.main_menu.show()
        self.close()

    @asyncSlot()
    async def actualizations_vk_svbu(self, name_directory: str) -> None:
        """Функция обновления видеокадров в папке SVBU_(1/2)/NPP_models из папки SVBU_(1/2)/NPP_models_new"""
        set_vis: Set[str] = set(listdir(path.join(name_directory, 'NPP_models')))
        set_vis_new: Set[str] = set(listdir(path.join(name_directory, 'NPP_models_new')))
        numbers_vis = len(set_vis)
        number = 1
        for i_vis in sorted(set_vis):
            if i_vis in set_vis_new:
                shutil.copy2(path.join(name_directory, 'NPP_models_new', i_vis),
                             path.join(name_directory, 'NPP_models', i_vis))
                await self.print_log(text=f'[{number}/{numbers_vis}]   +++{i_vis} видеокадр обновлен+++')
            else:
                await self.print_log(text=f'[{number}/{numbers_vis}]   '
                                          f'---Видеокадра {i_vis} нет в {name_directory}/NPP_models_new ---',
                                     color='red')
            number += 1
        await self.print_log(text=f'Выполнение программы обновления видеокадров {name_directory} завершено',
                             color='green')

    @asyncSlot()
    async def new_data_ana_bin_nary(self, name_system: str) -> None:
        """
        Функция обновления файлов со списком KKS сигналов. По завершению обновляются (создаются если не было) 3 файла:
        BIN_list_kks.txt со списком бинарных сигналов
        NARY_list_kks.txt со списком много битовых сигналов
        ANA_list_kks.txt со списков аналоговых сигналов
        :param name_system: папка в которой будут обновления.
        :return: None
        """
        check_directory(path_directory=name_system, name_directory='DbDumps')
        check_directory(path_directory=name_system, name_directory='data')

        set_kks_bin_date = set()
        set_kks_nary_date = set()
        set_kks_ana_date = set()

        await self.print_log(text='Сбор BIN сигналов')

        with open(path.join(name_system, 'DbDumps', 'PLS_BIN_CONF.dmp'), 'r', encoding='windows-1251') as file:
            new_text = reader(file, delimiter='|')
            for i_line in new_text:
                try:
                    full_kks = i_line[42]
                    if i_line[14] == '-1':

                        set_kks_bin_date.add(full_kks)
                    else:
                        set_kks_nary_date.add(full_kks)
                except IndexError:
                    ...

        with open(path.join(name_system, 'data', 'BIN_list_kks.txt'), 'w', encoding='UTF-8') as file:
            for i_kks in set_kks_bin_date:
                file.write(f'{i_kks}\n')

        with open(path.join(name_system, 'data', 'NARY_list_kks.txt'), 'w', encoding='UTF-8') as file:
            for i_kks in set_kks_nary_date:
                file.write(f'{i_kks}\n')

        await self.print_log(text='Сигналы BIN собраны успешно', color='green')

        await self.print_log(text='Сбор ANA сигналов')

        with open(path.join(name_system, 'DbDumps', 'PLS_ANA_CONF.dmp'), 'r', encoding='windows-1251') as file:
            new_text = reader(file, delimiter='|', quotechar=' ')
            for i_line in new_text:
                try:
                    set_kks_ana_date.add(i_line[78])
                except IndexError:
                    pass

        with open(path.join(name_system, 'data', 'ANA_list_kks.txt'), 'w', encoding='UTF-8') as file:
            for i_kks in set_kks_ana_date:
                file.write(f'{i_kks}\n')
        await self.print_log(text='Сигналы ANA собраны успешно', color='green')
        await self.print_log(text=f'Обновление базы данных сигналов {name_system} завершено\n', color='green')

    @asyncSlot()
    async def checking_svg_files(self, name_directory: str) -> None:
        """
        Функция запускающая поиск неверных привязок на видеокадрах соответствующей системы.
        :return: None
        """
        set_svg = set(listdir(path.join(name_directory, 'NPP_models')))
        await self.print_log(text=f'Старт проверки видеокадров {name_directory}')
        await self.new_start_parsing_svg_files(svg=set_svg, directory=name_directory)
        await self.print_log(text='Поиск замечаний завершен\n', color='green')

    async def new_start_parsing_svg_files(self, svg: Set[str], directory: str) -> None:
        set_kks_bin_data, set_kks_ana_data, dict_kks_bin_data, dict_kks_ana_data = await self.loading_data(
            directory=directory)

        numbers = len(svg)
        number = 1
        for i_svg in svg:
            text_log = f'[{number}/{numbers}]\t Проверка {i_svg}'
            if i_svg.endswith('.svg') or i_svg.endswith('.SVG'):
                dict_kks_svg: Dict[str] = dict()  # все найденных KKS на видеокадре с подмоделями
                await self.parsing_svg(svg=i_svg, directory=directory, dict_kks_svg=dict_kks_svg)

                list_error_kks: Set = set()  # список записей о замечаниях

                for i_kks in dict_kks_svg:
                    submodels.checking_kks_and_preparing_comment(kks_signal=i_kks,
                                                                 list_error_kks=list_error_kks,
                                                                 name_submodel=dict_kks_svg[i_kks],
                                                                 set_svg=svg,
                                                                 set_kks_ana_data=set_kks_ana_data,
                                                                 set_kks_bin_data=set_kks_bin_data,
                                                                 dict_kks_ana_data=dict_kks_ana_data,
                                                                 dict_kks_bin_data=dict_kks_bin_data
                                                                 )

                number_errors = len(list_error_kks)
                if number_errors:
                    submodels.recording_comments_to_a_file(directory=directory,
                                                           list_error_kks=list_error_kks,
                                                           name_file=i_svg[:-4])

                dict_kks_svg.clear()
                text_log = f'{text_log:<55}Кривых KKS: {number_errors}'
                await self.print_log(text=text_log)
            else:
                text_log = f'{text_log:<55}Файл {i_svg} не svg!'
                await self.print_log(text=text_log, color='red')
            number += 1

    async def parsing_svg(self, svg: str, directory: str, dict_kks_svg: Dict[str, str]) -> None:
        """
        Функция принимающая KKS видеокадра на котором построчно ведется поиск начала кода подмодели.
        При нахождении кода, записывает его построчно во множество set_constructor и запускает функцию add_kks
        с аргументом set_constructor.
        :param svg: Имя видеокадра формата svg.
        :param directory: Директория в которой хранится папка с видеокадрами.
        :param dict_kks_svg: Список сигналов найденных на видеокадре с названием подмодели
        :return: None
        """
        with open(path.join(directory, 'NPP_models', f'{svg}'), encoding='windows-1251') as svg_file:
            set_constructor: Set[str] = set()
            flag_constructor = False
            for i_line in svg_file:
                if flag_constructor:
                    if re.search(r'<image', i_line):
                        await self.add_kks(set_line_text=set_constructor,
                                           svg=await submodels.base_name_svg(svg=svg),
                                           dict_kks_svg=dict_kks_svg)
                        set_constructor.clear()
                        set_constructor.add(i_line)
                    else:
                        set_constructor.add(i_line)
                else:
                    if re.search(r'<image', i_line):
                        flag_constructor = True
                        set_constructor.add(i_line)
            else:
                await self.add_kks(set_line_text=set_constructor,
                                   svg=await submodels.base_name_svg(svg=svg),
                                   dict_kks_svg=dict_kks_svg)

    async def add_kks(self, set_line_text: Set, svg: str, dict_kks_svg: Dict[str, str]) -> None:
        """
        Функция проверяет полученный код подмодели и найдя имя, запускает соответствующую функцию поиска KKS.
        :param set_line_text: Множество строк с кодом подмодели из svg файла.
        :param svg: KKS видеокадра.
        :param dict_kks_svg: Список сигналов найденных на видеокадре с названием подмодели
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
            submodels.out_kks_suffix(set_line_text=set_line_text,
                                     id_kks='FKKS',
                                     id_suffix='Suffix',
                                     svg_constructor=svg_constructor,
                                     default_suffix='XQ01',
                                     dict_kks_svg=dict_kks_svg)
            return

        elif svg_constructor == 'DS_TPTS_Reg_degree.svg':
            submodels.out_kks_suffix(set_line_text=set_line_text,
                                     id_kks='KKS',
                                     id_suffix='SIGNAL',
                                     svg_constructor=svg_constructor,
                                     default_suffix='XQ01',
                                     dict_kks_svg=dict_kks_svg)
            return

        elif svg_constructor == 'DS_Reg_degree.svg':
            submodels.out_kks_suffix(set_line_text=set_line_text,
                                     id_kks='KKS',
                                     id_suffix='SIGNAL',
                                     svg_constructor=svg_constructor,
                                     default_suffix='AA1',
                                     dict_kks_svg=dict_kks_svg)
            return

        elif svg_constructor == 'bin_indicator.svg':
            submodels.out_kks_suffix(set_line_text=set_line_text,
                                     id_kks='PointID',
                                     id_suffix='BinMask',
                                     svg_constructor=svg_constructor,
                                     dict_kks_svg=dict_kks_svg)
            return
        elif svg_constructor == 'spds_csf_block.svg':
            submodels.out_kks_suffix(set_line_text=set_line_text,
                                     id_kks='LB_Point',
                                     id_suffix='Suffix',
                                     svg_constructor=svg_constructor,
                                     dict_kks_svg=dict_kks_svg)
            return

        elif svg_constructor in ('DS_TNT_HEAD.svg', 'DS_switch.svg', 'DS_T_valve.svg'):
            submodels.out_kks(set_line_text=set_line_text,
                              id_kks='KKS',
                              svg_constructor=svg_constructor,
                              dict_kks_svg=dict_kks_svg)
            return
        elif svg_constructor == 'spds_ana_to_time.svg':
            submodels.out_kks(set_line_text=set_line_text,
                              id_kks='AnaTime',
                              svg_constructor=svg_constructor,
                              dict_kks_svg=dict_kks_svg)
            return

        elif svg_constructor in ('bin_tablo.svg', 'bitwise_tablo_4bits.svg', 'bin_indicator_txt.svg'):
            submodels.out_kks(set_line_text=set_line_text,
                              id_kks='PointID',
                              svg_constructor=svg_constructor,
                              dict_kks_svg=dict_kks_svg)
            return

        elif svg_constructor in ('DS_CO_valve.svg', 'DS_motor.svg', 'DS_TPTS_TE_spec.svg', 'DS_pivot_valve.svg',
                                 'DS_Reg_valve.svg', 'DS_CO_valve_rect.svg', 'DS_breaker.svg', 'DS_setter.svg',
                                 'DS_TPTS_IBR_set.svg', 'DS_Reg_set.svg'):
            submodels.out_kks_nary(set_line_text=set_line_text,
                                   id_kks='KKS',
                                   svg_constructor=svg_constructor,
                                   dict_kks_svg=dict_kks_svg)
            return
        elif svg_constructor == 'DS_TPTS_KO.svg':
            submodels.out_kks_nary(set_line_text=set_line_text,
                                   id_kks='KKS',
                                   svg_constructor=svg_constructor,
                                   flag_teo=False,
                                   dict_kks_svg=dict_kks_svg)
            return
        elif svg_constructor == 'DS_pulse_valve.svg':
            submodels.out_kks_nary(set_line_text=set_line_text,
                                   id_kks='KKS',
                                   svg_constructor=svg_constructor,
                                   flag_teo=False,
                                   dict_kks_svg=dict_kks_svg)
            return
        elif svg_constructor in ('DS_TPTS_VL_num.svg', 'DS_TPTS_VL_spec.svg'):
            submodels.out_kks_nary(set_line_text=set_line_text,
                                   id_kks='KKS',
                                   svg_constructor=svg_constructor,
                                   end_kks='VL0',
                                   dict_kks_svg=dict_kks_svg)
            return

        elif svg_constructor == 'DS_TNT_DM_EXT.svg':
            submodels.out_vis_kks_nary(set_line_text=set_line_text,
                                       id_kks='KKS',
                                       svg_constructor=svg_constructor,
                                       name_svg=svg,
                                       dict_kks_svg=dict_kks_svg)
            return

        elif svg_constructor in ('bin_mode_1o6.svg', 'DS_TNT_MOD1.svg', 'bin_tablo_flogic.svg',
                                 'DS_ana_ext_bounds.svg', 'bin_checkbox.svg', 'bin_tablo_OR3.svg',
                                 'DS_TurbValve_control.svg', 'bin_tablo_flogic.svg', 'DS_ana_bar_AKNP.svg',
                                 'DS_ana_bar_usr.svg', 'ps_ana_bar_piecewise_lin_log_1.svg', 'ps_NVO_StepNumber.svg',
                                 'ps_Len2_ana_AKNP.svg'):
            submodels.out_some_kks(set_line_text=set_line_text,
                                   id_kks='PointID',
                                   svg_constructor=svg_constructor,
                                   dict_kks_svg=dict_kks_svg)
            return
        elif svg_constructor in ('spds_timernd.svg', 'spds_timer_csf.svg', 'spds_graph_p_t.svg',
                                 'spds_graph_DTs_BLR12.svg', 'spds_menu_vert.svg', 'spds_fb_menu.svg',
                                 'DS_pulse3_valve.svg', 'spds_menu_hor_BLR12.svg',
                                 'spds_graph_ts1k_BLR12.svg'):
            submodels.out_some_kks(set_line_text=set_line_text,
                                   id_kks='type=',
                                   svg_constructor=svg_constructor,
                                   dict_kks_svg=dict_kks_svg)
            return
        elif svg_constructor in ('DS_TurbValve_cutout.svg', 'DS_TurbValve_cutout.svg', 'DS_reflux_valve.svg',
                                 'DS_pulse3_valve.svg'):
            submodels.out_some_kks(set_line_text=set_line_text,
                                   id_kks='SIG',
                                   svg_constructor=svg_constructor,
                                   dict_kks_svg=dict_kks_svg)
            return
        elif svg_constructor == 'spds_arrow.svg':
            # Сигнал вбивается полностью (наверное). Несколько сигналов:
            # arr_col - 1-й сигнал
            # arr_log - 2-й сигнал
            submodels.out_some_kks(set_line_text=set_line_text,
                                   id_kks='arr',
                                   svg_constructor=svg_constructor,
                                   dict_kks_svg=dict_kks_svg)
            return

        elif svg_constructor in ('diag_WS_3mon.svg', 'diag_WS_2mon.svg', 'diag_LSD.svg', 'diag_Server.svg',
                                 'diag_DTU.svg', 'aux_Server.svg'):
            submodels.out_some_kks(set_line_text=set_line_text,
                                   id_kks='_PID',
                                   svg_constructor=svg_constructor,
                                   dict_kks_svg=dict_kks_svg)
            return

        elif svg_constructor == 'spds_tablo.svg':  # Сигнал вбивается полностью
            submodels.out_some_kks(set_line_text=set_line_text,
                                   id_kks='tab_log',
                                   svg_constructor=svg_constructor,
                                   dict_kks_svg=dict_kks_svg)
            return
        elif svg_constructor == 'ps_Len2_ANA_Scale.svg' or svg_constructor == 'ps_Kz_Trends.svg':
            submodels.out_some_kks(set_line_text=set_line_text,
                                   id_kks='FKKS',
                                   svg_constructor=svg_constructor,
                                   dict_kks_svg=dict_kks_svg)
            return

        elif svg_constructor in ('DS_TPTS_AVR_sel.svg', 'DS_TPTS_TZB_universal.svg', 'DS_TPTS_nakladka.svg'):
            submodels.out_kks_with_te_vl(set_line_text=set_line_text,
                                         id_kks='KKS',
                                         svg_constructor=svg_constructor,
                                         dict_kks_svg=dict_kks_svg)
            return

        elif svg_constructor in ('GW.svg', 'TNT_indic_tips.svg', 'obj_Button.svg', 'ps_Blr_MotorStatistics.svg'):
            return
        else:
            await self.print_log(text=f'--------> Найдена необрабатываемая подмодель {svg_constructor}', color='red')

    async def loading_data(self, directory: str = '') -> \
            (Set[str], Set[str], Dict[str, Dict[str, str]], Dict[str, Dict[str, str]]):
        """
        Функция считывающая базу сигналов.
        :return: 1-множество аналоговых сигналов, 2-множество бинарных сигналов,
        3-словарь аналоговых сигналов с описанием, 4-словарь бинарных сигналов с описанием
        """
        set_kks_bin_data: Set[str] = set()
        set_kks_ana_data: Set[str] = set()
        dict_kks_bin_data: Dict[str, Dict[str, str]] = dict()
        dict_kks_ana_data: Dict[str, Dict[str, str]] = dict()

        await self.print_log(text=f'Загрузка БД {directory}')
        with open(path.join(directory, 'data', 'ANA_list_kks.txt')) as file:
            for i_line in file:
                set_kks_ana_data.add(i_line[:-1])

        with open(path.join(directory, 'data', 'ANA_json_kks.json'), 'r', encoding='UTF-8') as json_file:
            dict_ana_kks = json.load(json_file)
            dict_kks_ana_data.update(dict_ana_kks)

        with open(path.join(directory, 'data', 'BIN_list_kks.txt')) as file:
            for i_line in file:
                set_kks_bin_data.add(i_line[:-1])

        with open(path.join(directory, 'data', 'BIN_json_kks.json'), 'r', encoding='UTF-8') as json_file:
            dict_bin_kks = json.load(json_file)
            dict_kks_bin_data.update(dict_bin_kks)
        return set_kks_bin_data, set_kks_ana_data, dict_kks_bin_data, dict_kks_ana_data

    @asyncSlot()
    async def print_log(self, text: str, color: str = 'black') -> None:
        """Программа выводящая переданный текст в окно лога. Цвета можно использовать зеленый - green, красный - red"""
        dict_colors = {'black': QColor(0, 0, 0),
                       'red': QColor(255, 0, 0),
                       'green': QColor(50, 155, 50)}
        self.text_log.setTextColor(dict_colors[color])
        self.text_log.append(text)
