from typing import List, Any, Dict, Set
import re
from PIL import Image, ImageFont, ImageDraw


class AnchorPoint:
    """
    Все характеристики точки привязки на видеокадре.
    """
    def __init__(self, full_description_of_the_submodel: List, name_svg: str = ''):
        self.full_description_of_the_submodel: List = full_description_of_the_submodel  # текст описания подмодели
        # {
        # 'KKS': '', - KKS, который используется для работы с базой данных (если пусто, значит статическая подмодель)
        # 'text_kks': kks, - Запись, которая будет использована при заполнении поля KKS в паспортах
        # 'description': '' - Описание сигнала из базы данных
        # 'Type_signal': 'BIN' - Тип сигнала (BIN или ANA)
        # 'Signal_in_database': True - Наличие сигнала в базе данных
        # }
        self.x: float = 0  # расположение подмодели по горизонтали
        self.y: float = 0  # расположение подмодели по вертикали
        self.number_point: int = 0  # Порядковый номер точки на видеокадре
        self.signal_description: List[Dict[str]] = list()  # Описание сигналов из базы данных
        self.width: float = 0  # ширина подмодели
        self.height: float = 0  # высота подмодели
        self.transform: Any = None
        self.img = None  # Изображение номера точки на подложке белого круга с черным обрамлением
        self.name_submodel: str = ''
        self.name_svg: str = name_svg[:-4]

    def set_signal_description(self, signal_description):
        self.signal_description.append(signal_description)

    def get_signal_description(self):
        return self.signal_description

    def get_full_description_of_the_submodel(self):
        return self.full_description_of_the_submodel

    def check_error_kks_database(self, data_ana: Set[str], data_bin: Set[str], data_nary: Set[str]) -> Dict[str, str]:
        """Проверяет есть ли в базе дынных KKS сигнала.
        :param data_ana: База аналоговых сигналов.
        :param data_bin: База бинарных сигналов.
        :param data_nary: База много битовых сигналов.
        :return множество сигналов, которых не нашлось в базе
        """
        dict_error_kks: Dict[str, str] = dict()
        # set_error_kks: Set[str] = set()
        for i_point in self.signal_description:
            kks = i_point['KKS']
            if kks:
                if kks in data_ana:
                    i_point['Type_signal'] = 'ANA'
                    i_point['Signal_in_database'] = True
                    continue
                elif kks in data_nary:
                    i_point['Type_signal'] = 'NARY'
                    i_point['Signal_in_database'] = True
                    continue
                elif kks in data_bin:
                    i_point['Type_signal'] = 'BIN'
                    i_point['Signal_in_database'] = True
                    continue
                else:
                    dict_error_kks[kks] = self.name_submodel
                    # set_error_kks.add(kks)
        return dict_error_kks
        # return set_error_kks

    def check_existence_database(self, data_ana: Set[str], data_bin: Set[str], data_nary: Set[str],
                                 set_suffix: Set[str] = None):
        """Проверяет есть ли в базе дынных KKS сигнала"""
        for i_point in self.signal_description:
            kks = i_point['KKS']
            if kks:
                if kks in data_ana:
                    i_point['Type_signal'] = 'ANA'
                    i_point['Signal_in_database'] = True
                    if set_suffix:
                        self.add_bin_signals_setting(data_bin=data_bin,
                                                     kks=kks.split('_')[0],
                                                     add_list_suffix=set_suffix)
                    else:
                        self.add_bin_signals_setting(data_bin=data_bin,
                                                     kks=kks.split('_')[0])
                    continue
                elif kks in data_nary:
                    i_point['Type_signal'] = 'NARY'
                    i_point['Signal_in_database'] = True
                    continue
                elif kks in data_bin:
                    i_point['Type_signal'] = 'BIN'
                    i_point['Signal_in_database'] = True
                    continue
            i_point['Signal_in_database'] = False

    def add_bin_signals_setting(self, data_bin, kks: str, add_list_suffix: Set[str] = None):
        """Добавляет к аналоговым сигналам бинарные сигналы уставок"""
        list_suffix: Set[str] = {'XH03', 'XH05', 'XH54', 'XH56', 'XH43', 'XH45', 'XH94', 'XH96'}
        if add_list_suffix:
            list_suffix.update(add_list_suffix)
        for i_suffix in list_suffix:
            new_kks = f'{kks}_{i_suffix}'
            if new_kks in data_bin:
                self.signal_description.append({'KKS': new_kks, 'Type_signal': 'BIN', 'Signal_in_database': True})

    def get_kks_ana_bin(self):
        """Функция возвращает 2 множества с сигналами:
        1. Множество аналоговых сигналов (ANA)
        2. Множество бинарных сигналов вместе с много битовыми (BIN, NARY)
        """
        set_kks_ana: Set[str] = set()
        set_kks_bin: Set[str] = set()
        for i_point in self.signal_description:
            if i_point['Signal_in_database']:
                if i_point['Type_signal'] == 'ANA':
                    set_kks_ana.add(i_point['KKS'])
                else:
                    set_kks_bin.add(i_point['KKS'])
        return set_kks_ana, set_kks_bin

    def get_kks_ana_bin_nary(self) -> (Set[str], Set[str], Set[str]):
        """Функция возвращает 3 множества с сигналами:
        1. Множество аналоговых сигналов (ANA)
        2. Множество бинарных сигналов (BIN)
        3. Множество много битовых сигналов (NARY)
        """
        set_kks_ana: Set[str] = set()
        set_kks_bin: Set[str] = set()
        set_kks_nary: Set[str] = set()
        for i_point in self.signal_description:
            if i_point['Signal_in_database']:
                if i_point['Type_signal'] == 'BIN':
                    set_kks_bin.add(i_point['KKS'])
                elif i_point['Type_signal'] == 'NARY':
                    set_kks_nary.add(i_point['KKS'])
                else:
                    set_kks_ana.add(i_point['KKS'])
        return set_kks_ana, set_kks_bin, set_kks_nary

    def set_name_submodel(self) -> None:
        """Поиск названия подмодели"""
        try:
            name_submodel = re.findall(r'xlink:href="(.*\.svg)"', self.full_description_of_the_submodel[0])[0]
            self.name_submodel = name_submodel
            return name_submodel
        except IndexError:
            self.name_submodel = None
            return None

    def set_number_point(self, number: int):
        self.number_point = number

    def get_img(self):
        return self.img

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_number_point(self):
        return str(self.number_point)

    def set_x(self, x):
        self.x = x

    def set_width_and_height(self):
        """Нахождение высоты и ширины подмодели"""
        try:
            width = re.findall(r'width="([\d/.]*)"', self.full_description_of_the_submodel[0])[0]
            height = re.findall(r'height="([\d/.]*)"', self.full_description_of_the_submodel[0])[0]
            self.width = float(width)
            self.height = float(height)
        except IndexError:
            print('set_width_and_height')
            self.print_info()

    def set_x_and_y(self):
        """Нахождение расположения подмодели по координатам x и y"""
        x = re.findall(r'x="(-?[\d/.]*)"', self.full_description_of_the_submodel[0])[0]
        self.x = float(x)
        try:
            y = re.findall(r'y="(-?[\d/.]*)"', self.full_description_of_the_submodel[0])[0]
            self.y = float(y)
        except IndexError:
            self.y = 0
        if self.name_submodel == 'DS_CO_valve.svg':
            self.y += round(self.height / 3)
        elif self.name_submodel == 'DS_pulse3_valve.svg':
            self.y += 248

    def set_transform(self):
        """Проверка на наличие поворотов подмодели"""
        try:
            transform = re.findall(r'rotate\((.*)\)"', self.full_description_of_the_submodel[0])[0]
            self.transform = transform.split(' ')
            self.y -= int(self.transform[2])
            if self.transform[0] == '90' or self.transform[0] == '270':
                self.width, self.height = self.height, self.height
        except IndexError:
            pass
        except ValueError:
            pass

    def creating_an_image_with_a_number(self) -> None:
        """Функция создает изображение c числом number_point в круге."""
        img = Image.new('RGBA', (300, 300), (0, 0, 0, 0))
        text = str(self.number_point)
        idraw = ImageDraw.Draw(img)
        font_2 = ImageFont.truetype("arial.ttf", size=200)
        font_3 = ImageFont.truetype("arial.ttf", size=160)
        if len(text) == 1:
            x = 95
            y = 43
            font = font_2
        elif len(text) == 2:
            x = 40
            y = 43
            font = font_2
        else:
            x = 15
            y = 70
            font = font_3
        background_color = 'white'

        if len(self.signal_description) == 1:
            try:
                if self.signal_description[0]['description'] == 'Статический элемент':
                    background_color = 'yellow'
            except KeyError:
                pass

        idraw.ellipse((0, 0, 300, 300), fill=background_color, outline=(10, 10, 10), width=8)
        idraw.text((x, y), text, font=font, fill='black')
        self.img = img.resize((30, 30))

    def print_info(self):
        print('v'*20)
        print(f'{self.x=}')
        print(f'{self.y=}')
        print(f'{self.height=}')
        print(f'{self.width=}')
        print(f'{self.transform=}')
        print(f'{self.signal_description=}')
        print(f'{self.number_point=}')
        print(f'{self.full_description_of_the_submodel=}')
        print(f'{self.name_submodel=}')
        print('^' * 20)
        print()

    def search_kks_on_submodel(self) -> None:
        if self.name_submodel in {'TNT_indic_tips.svg', 'ps_Blr_MotorStatistics.svg', 'DS_TPTS_Reg_degree.svg'}:
            pass
        elif self.name_submodel in {'ps_Len2_DS_ana.svg', 'DS_ana.svg', 'DS_ana_bar.svg', 'DS_ana_bar_h.svg',
                                    'DS_ana_tenzor.svg', 'ana_bar_scale.svg', 'DS_ana_GetLocation.svg'}:
            self.search_kks_in_ps_len2_ds_ana()
        elif self.name_submodel == 'ps_LAES2_ana_DoubleBound.svg':
            self.search_kks_in_ps_laes2_ana_double_bound()
        elif self.name_submodel in {'bin_indicator.svg', 'DS_TNT_MOD1.svg', 'ps_ana_bar_piecewise_lin_log_1.svg',
                                    'DS_ana_bar_usr.svg'}:
            self.search_kks_in_bin_indicator()
        elif self.name_submodel in {'DS_CO_valve.svg', 'DS_CO_valve_rect.svg', 'DS_breaker.svg', 'DS_reflux_valve.svg',
                                    'DS_pivot_valve.svg', 'DS_Reg_valve.svg', 'DS_pulse_valve.svg', 'DS_motor.svg',
                                    'DS_T_valve.svg', 'DS_setter.svg', 'DS_switch.svg',
                                    'DS_Reg_pump.svg', 'DSB_CO_valve.svg'}:
            self.search_kks_in_ds()
        elif self.name_submodel == 'DS_Reg_degree.svg':
            self.search_kks_in_ds_reg_degree()
        elif self.name_submodel in {'bin_mode_1o6.svg', 'bin_tablo.svg', 'obj_Button_trend.svg',
                                    'DS_TurbValve_control.svg', 'bin_tablo_OR3.svg', 'DS_ana_bar_AKNP.svg',
                                    'DS_ana_ext_bounds.svg', 'ps_Len2_ana_AKNP.svg', 'ps_NVO_StepNumber.svg',
                                    'bin_checkbox.svg'}:
            self.search_kks_in_bin_tablo()
        elif self.name_submodel == 'bitwise_tablo_4bits.svg':
            self.search_kks_in_bitwise_tablo_4bits()
        elif self.name_submodel == 'bin_indicator_txt.svg':
            self.search_kks_in_bin_indicator_txt()
        elif self.name_submodel in {'obj_Button_instruction.svg', 'obj_ButtonH_icon_instr.svg',
                                    'spds_instr_button.svg'}:
            self.instruction_submodel_processing()
        elif self.name_submodel == 'obj_Station_stat.svg':
            self.station_submodel_processing()
        elif self.name_submodel == 'obj_Button.svg':
            self.button_submodel_processing()
        elif self.name_submodel == 'DS_TPTS_TE_spec.svg':
            self.search_kks_in_ds_tpts_te_spec()
        elif self.name_submodel in {'DS_TPTS_VL_num.svg', 'DS_TPTS_VL_spec.svg'}:
            self.search_kks_in_ds_tpts_vl_num()
        elif self.name_submodel in {'DS_TPTS_KO.svg', 'ps_Blr12_SKUOS_reg_valve.svg', 'DS_TPTS_nakladka.svg',
                                    'ps_Blr12_SKUOS_AVR.svg', 'ps_Blr12_SKUOS_motor.svg', 'ps_Blr12_SKUOS_CO_valve.svg',
                                    'ps_Blr12_SKUOS_M0.svg', 'ps_Blr12_SKUOS_pivot_valve.svg'}:
            self.search_kks_in_ds_tpts()
        elif self.name_submodel in {'DS_TPTS_IBR_set.svg', 'DS_Reg_set.svg'}:
            self.search_kks_in_ds_tpts_ibr_set()
        elif self.name_submodel in {'DS_TurbValve_cutout.svg', 'DS_pulse3_valve.svg'}:
            self.search_kks_in_ds_turb_value_cutout()
        elif self.name_submodel == 'DS_TPTS_AVR_sel.svg':
            self.search_kks_in_ds_tpts_avr_sel()
        elif self.name_submodel == 'obj_Button_icon_trend.svg':
            self.search_kks_in_obj_button_icon_trend()
        elif self.name_submodel == 'DS_TNT_HEAD.svg':
            self.search_kks_in_ds_tnt_head()
        # elif self.name_submodel == 'DS_TNT_MOD1.svg':
        #     self.search_kks_in_ds_tnt_mod1()
        elif self.name_submodel == 'DS_TNT_DM_EXT.svg':
            self.search_kks_in_ds_tnt_dm_ext()
        elif self.name_submodel in {'Arm_4_1_PL_VHR.svg', 'aux_MKB.svg'}:
            self.search_kks_in_arm()
        elif self.name_submodel == 'spec_I_M.svg':
            self.search_kks_in_server()
        elif self.name_submodel == 'DS_TPTS_TZB_universal.svg':
            self.search_kks_in_ds_tpts_tzb_universal()
        elif self.name_submodel in {'spds_menu_hor_right.svg', 'spds_menu_hor_left.svg'}:
            self.no_binding_on_submodel()
        elif self.name_submodel == 'unico.svg':
            self.search_kks_in_unico()
        elif self.name_submodel == 'obj_Button_icon.svg':
            self.search_kks_svg_in_obj_button_icon()
        elif self.name_submodel == 'spds_menu_hor_BLR12.svg':
            self.search_kks_in_spds_menu_hor_blr12()
        elif self.name_submodel == 'ps_Len2_ANA_Scale.svg':
            self.search_kks_in_ps_len2_ana_scale()
        elif self.name_submodel == 'spds_arrow.svg':
            self.search_kks_in_spds_arrow()
        elif self.name_submodel in {'spds_timernd.svg', 'spds_timer_csf.svg'}:
            self.search_kks_in_spds_timernd()
        elif self.name_submodel == 'spds_csf_block.svg':
            self.search_kks_in_spds_csf_block()
        elif self.name_submodel == 'spds_menu_vert.svg':
            self.search_kks_in_spds_menu_vert()
        elif self.name_submodel == 'spds_tablo.svg':
            self.search_kks_in_spds_tablo()
        elif self.name_submodel == 'spds_fb_menu.svg':
            self.search_kks_in_spds_fb_menu()
        elif self.name_submodel in {'spds_graph_p_t.svg', 'spds_graph_ts1k_BLR12.svg'}:
            self.search_kks_in_spds_graph_p_t()
        elif self.name_submodel == 'spds_ana_to_time.svg':
            self.search_kks_in_spds_ana_to_time()
        elif self.name_submodel == 'bin_tablo_flogic.svg':
            self.search_kks_in_bin_tablo_flogic()
        elif self.name_submodel == 'spds_graph_DTs_BLR12.svg':
            self.search_kks_in_spds_graph_dts_blr12()
        elif self.name_submodel in {'diag_Server.svg', 'diag_WS_2mon.svg', 'diag_WS_3mon.svg', 'diag_LSD.svg',
                                    'diag_DTU.svg'}:
            self.search_kks_in_diag_server()
        elif self.name_submodel in {'Print.svg', 'GW.svg', 'diag_Comm.svg', 'diag_TimeServer.svg', 'aux_Comm.svg'}:
            self.treatment_submodel_print()
        elif self.name_submodel == 'ps_Kz_Trends.svg':
            self.search_kks_in_ps_kz_trends()
        elif self.name_submodel == 'aux_RSD_UPPS.svg':
            self.search_kks_in_aux_psd_upps()
        elif self.name_submodel == 'bool_checkbox.svg':
            self.search_kks_in_bool_checkbox()

        else:
            print(f'{self.name_svg} Нет обработки подмодели {self.name_submodel} ')
            # raise Exception
        # print(f'{self.name_submodel} - {self.signal_description}')

    def static_element(self):
        """Поиск подписи в строке title"""
        kks = ''
        for i_line in self.full_description_of_the_submodel:
            if '<title>' in i_line:
                try:
                    kks = re.findall(r'<title>&quot;(.*)&quot;</title>', i_line)[0]
                    break
                except IndexError:
                    kks = re.findall(r'<title>"?(.*)"?</title>', i_line)[0]
                    break
        self.signal_description.append({'KKS': '', 'text_kks': kks, 'description': 'Статический элемент'})

    def search_kks_in_aux_psd_upps(self):
        """Поиск KKS в подмодели aux_RSD_UPPS.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'KKS' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': f'{kks}E03_ZV01', 'text_kks': f'{kks}E03_ZV01'})

    def search_kks_in_ps_kz_trends(self):
        """Поиск KKS в подмодели ps_Kz_Trends.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'FKKS' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})

    def treatment_submodel_print(self):
        """Поиск описания на подмоделях Print.svg, GW.svg, diag_Comm.svg, diag_TimeServer.svg, aux_Comm.svg"""
        text = ''
        for i_line in self.full_description_of_the_submodel:
            if '<title>' in i_line:
                try:
                    text = re.findall(r'<title>&quot;(.*)&quot;</title>', i_line)[0]
                    break
                except IndexError:
                    text = re.findall(r'<title>"?(.*)"?</title>', i_line)[0]
                    break
        self.signal_description.append({'KKS': '', 'text_kks': '', 'description': text})

    def search_kks_in_diag_server(self):
        """Поиск KKS на подмоделях diag_Server.svg, diag_WS_2mon.svg, diag_WS_3mon.svg, diag_LSD.svg, diag_DTU.svg"""
        for i_line in self.full_description_of_the_submodel:
            if '"NET' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})

    def search_kks_in_spds_graph_dts_blr12(self):
        """Поиск KKS на подмоделях spds_graph_DTs_BLR12.svg"""
        for i_line in self.full_description_of_the_submodel:
            if '"Pressure"' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
                break
        for i_line in self.full_description_of_the_submodel:
            if '"DTs"' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
                break
        for i_line in self.full_description_of_the_submodel:
            if '"Tail"' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
                break
        for i_line in self.full_description_of_the_submodel:
            if '"pv_' in i_line:
                list_kks = re.findall(r'"&quot;(.*)&quot;"', i_line)
                for kks in list_kks:
                    self.signal_description.append({'KKS': kks, 'text_kks': kks})

    def search_kks_in_bin_tablo_flogic(self):
        """Поиск KKS на подмоделях bin_tablo_flogic.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'PointID' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                if '_Z0' in kks:
                    self.signal_description.append({'KKS': kks, 'text_kks': kks.split('_')[0]})
                else:
                    self.signal_description.append({'KKS': f'{kks}_Z0', 'text_kks': kks})

    def search_kks_in_spds_ana_to_time(self):
        """Поиск KKS на подмоделях bin_tablo_flogic.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'AnaTime' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
                break

    def search_kks_in_spds_graph_p_t(self):
        """Поиск KKS на подмоделях spds_graph_p_t.svg, spds_graph_ts1k_BLR12.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'Pressure' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
                break
        for i_line in self.full_description_of_the_submodel:
            if 'Temperature' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
                break
        for i_line in self.full_description_of_the_submodel:
            if 'Tail' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
                break
        for i_line in self.full_description_of_the_submodel:
            if 'vrange' in i_line:
                list_kks = re.findall(r'"&quot;(.*)&quot;"', i_line)
                for kks in list_kks:
                    self.signal_description.append({'KKS': kks, 'text_kks': kks})
                break

    def search_kks_in_spds_fb_menu(self):
        """Поиск KKS на подмоделях spds_fb_menu.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'col_' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})

    def search_kks_in_spds_tablo(self):
        """Поиск KKS на подмоделях spds_tablo.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'tab_log' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
                break

    def search_kks_in_spds_menu_vert(self):
        """Поиск KKS на подмоделях spds_menu_vert.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'dm_color' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
        for i_line in self.full_description_of_the_submodel:
            if 'Frame_' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
        for i_line in self.full_description_of_the_submodel:
            if 'PointID' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
        for i_line in self.full_description_of_the_submodel:
            if 'pv_' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})

    def search_kks_in_spds_csf_block(self):
        """Поиск KKS на подмоделях spds_csf_block.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'CSF_Color' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
                break

        for i_line in self.full_description_of_the_submodel:
            if 'LB_Point' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                break
        else:
            return

        for i_line in self.full_description_of_the_submodel:
            if 'Suffix_' in i_line:
                suffix = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': f'{kks}_{suffix}', 'text_kks': f'{kks}_{suffix}'})

    def search_kks_in_spds_timernd(self):
        """Поиск KKS на подмоделях spds_timernd.svg, spds_timer_csf.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'PID' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
                break
        for i_line in self.full_description_of_the_submodel:
            if 'STime' in i_line:
                kks = re.findall(r'value="BIN\(&quot;(.*)&quot;\)', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
                break

    def search_kks_in_spds_arrow(self):
        """Поиск KKS на подмоделях spds_arrow.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'arr_' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})

    def search_kks_in_ps_len2_ana_scale(self):
        """Поиск KKS на подмодели ps_Len2_ANA_Scale.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'FKKS1' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks, 'description': 'X: '})
                break

        for i_line in self.full_description_of_the_submodel:
            if 'FKKS2' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks, 'description': 'Y: '})
                break

        for i_line in self.full_description_of_the_submodel:
            if 'FKKS3' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks, 'description': 'Y2: '})
                break

    def search_kks_in_spds_menu_hor_blr12(self):
        """Поиск KKS на подмоделях spds_menu_hor_BLR12.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'dm_color' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': kks, 'text_kks': kks})

    def search_kks_svg_in_obj_button_icon(self):
        """Поиск KKS видеокадра на подмодели obj_Button_icon.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'OnClick">LoadNew' in i_line:
                try:
                    kks_svg = re.findall(r'type="OnClick">LoadNew\(&quot;(.*)&quot;\)', i_line)[0]
                except IndexError:
                    kks_svg = re.findall(r'type="OnClick">LoadNew\("(.*)"\)', i_line)[0]
                self.signal_description.append({'KKS': '',
                                                'text_kks': kks_svg,
                                                'description': f'Переход на ВК "{kks_svg}"'})

    def search_kks_in_unico(self):
        """Поиск KKS на подмоделях unico.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'Filter' in i_line:
                list_kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0].split(',')
                break
        else:
            self.static_element()
            return
        if list_kks:
            for i_kks in list_kks:
                self.signal_description.append({'KKS': i_kks, 'text_kks': i_kks})

    def no_binding_on_submodel(self):
        """Заполняет данные подмодели которой не требуется привязка"""
        self.signal_description.append({'KKS': '', 'text_kks': 'Объект не привязан'})

    def search_kks_in_ds_tpts_tzb_universal(self):
        """Поиск KKS на подмоделях DS_TPTS_TZB_universal.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'KKS' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                if kks.endswith('TE0'):
                    self.signal_description.append({'KKS': f'{kks}_Z0', 'text_kks': f'{kks}_Z0'})
                else:
                    self.signal_description.append({'KKS': f'{kks}TE0_Z0', 'text_kks': f'{kks}TE0_Z0'})
                break
        else:
            self.static_element()
            return

    def search_kks_in_server(self):
        """Поиск KKS на подмоделях spec_I_M.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'KKS' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': f'{kks}S42_XQ01', 'text_kks': f'{kks}S42_XQ01'})
                # self.signal_description.append({'KKS': f'{kks}E02_XQ01', 'text_kks': kks})  # разобраться что должно

    def search_kks_in_arm(self):
        """Поиск KKS на подмоделях Arm_4_1_PL_VHR.svg, aux_MKB.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'KKS' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': f'{kks}E02_XQ01', 'text_kks': f'{kks}E02_XQ01'})

    def search_kks_in_ds_tnt_dm_ext(self):
        """Поиск KKS на подмоделях DS_TNT_DM_EXT.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'KKS' in i_line:
                if 'PVId_base' in i_line:
                    end_kks = re.findall(r'value="PVId_base \+ &quot;(.*)&quot;"', i_line)[0]
                    kks = f'{self.name_svg[:7]}{end_kks}'
                else:
                    kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': f'{kks}_F0', 'text_kks': kks})

    # def search_kks_in_ds_tnt_mod1(self):
    #     """Поиск KKS на подмоделях DS_TNT_MOD1.svg"""
    #     for i_line in self.full_description_of_the_submodel:
    #         if 'PointID' in i_line:
    #             kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
    #             self.signal_description.append({'KKS': kks, 'text_kks': kks})
    #             return

    def search_kks_in_ds_tnt_head(self):
        """Поиск KKS на подмоделях DS_TNT_HEAD.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'KKS' in i_line:
                if 'PVId_base' in i_line:
                    end_kks = re.findall(r'value="PVId_base \+ &quot;(.*)&quot;"', i_line)[0]
                    kks = f'{self.name_svg[:7]}{end_kks}'
                    self.signal_description.append({'KKS': f'{kks}_F0', 'text_kks': kks})
                else:
                    list_kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0].split(',')
                    for i_kks in list_kks:
                        if i_kks:
                            self.signal_description.append({'KKS': f'{i_kks}_F0', 'text_kks': i_kks})
                break

        for i_line in self.full_description_of_the_submodel:
            if 'LIST' in i_line:
                list_kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0].split('|')
                break
        else:
            return
        for i_kks in list_kks:
            if i_kks:
                self.signal_description.append({'KKS': f'{i_kks}_XQ01', 'text_kks': f'{i_kks}_XQ01'})

    def search_kks_in_obj_button_icon_trend(self):
        """Поиск KKS на подмоделях obj_Button_icon_trend.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'OnClick' in i_line:
                try:
                    kks = re.findall(r'Value = &quot;SIGNAL_VIEW AddSignalByPvIdNewTrend S:(.*)&quot;</rt:event>',
                                     i_line)[0]
                except IndexError:
                    kks = re.findall(r'Value = "SIGNAL_VIEW AddSignalByPvIdNewTrend S:(.*)"</rt:event>',
                                     i_line)[0]
                list_kks = kks.split('|')
                break
        else:
            self.static_element()
            return
        for i_kks in list_kks:
            if i_kks:
                self.signal_description.append({'KKS': i_kks, 'text_kks': i_kks})

    def search_kks_in_ds_tpts_avr_sel(self):
        """Поиск KKS на подмоделях DS_TPTS_AVR_sel.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'KKS' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                self.signal_description.append({'KKS': f'{kks}TE0_Z0', 'text_kks': kks})
                return
        else:
            self.static_element()

    def search_kks_in_ds_turb_value_cutout(self):
        """Поиск KKS на подмодели DS_TurbValve_cutout.svg, DS_pulse3_valve.svg"""
        kks = ''
        for i_line in self.full_description_of_the_submodel:
            if 'KKS' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                break
        if kks:
            if '_' in kks:
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
                return
        for i_line in self.full_description_of_the_submodel:
            if 'SIG_' in i_line:
                suffix = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                if '_' in suffix:
                    self.signal_description.append({'KKS': suffix, 'text_kks': suffix})
                else:
                    self.signal_description.append({'KKS': f'{kks}_{suffix}', 'text_kks': f'{kks}_{suffix}'})
        if not self.signal_description:
            self.static_element()

    def search_kks_in_ds_tpts_ibr_set(self):  # Проверить
        """Поиск KKS на подмоделях DS_TPTS_IBR_set.svg, 'DS_Reg_set.svg'"""
        for i_line in self.full_description_of_the_submodel:
            if 'KKS' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                break
        else:
            print(f'На подмодели {self.name_submodel} нет привязки')
            return
        if '_' in kks:
            new_kks, suffix = kks.split(separator='_')
            self.signal_description.append({'KKS': kks, 'text_kks': new_kks})
        else:
            self.signal_description.append({'KKS': f'{kks}_Z0', 'text_kks': kks})
            self.signal_description.append({'KKS': f'{kks}_AA1', 'text_kks': kks})
            # self.signal_description.append({'KKS': f'{kks}_AA2', 'text_kks': kks})
            self.signal_description.append({'KKS': f'{kks}_XQ07', 'text_kks': kks})

    def search_kks_in_ds_tpts(self):
        """Поиск KKS на подмоделях DS_TPTS_KO.svg, ps_Blr12_SKUOS_reg_valve.svg, ps_Blr12_SKUOS_AVR.svg,
        ps_Blr12_SKUOS_motor.svg, ps_Blr12_SKUOS_CO_valve.svg, ps_Blr12_SKUOS_M0.svg, ps_Blr12_SKUOS_pivot_valve.svg,
        DS_TPTS_nakladka.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'KKS' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                break
        else:
            # print(f'На подмодели {self.name_submodel} нет привязки')
            return
        if '_' in kks:
            new_kks, suffix = kks.split(separator='_')
            self.signal_description.append({'KKS': kks, 'text_kks': new_kks})
        else:
            self.signal_description.append({'KKS': f'{kks}_Z0', 'text_kks': kks})

    def search_kks_in_ds_tpts_vl_num(self):
        """Поиск KKS на подмоделях DS_TPTS_VL_num.svg, DS_TPTS_VL_spec.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'KKS' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                break
        else:
            self.static_element()
            return
        if kks.endswith('VL0') or kks.endswith('IVL0'):
            self.signal_description.append({'KKS': f'{kks}_Z0', 'text_kks': kks})
        else:
            self.signal_description.append({'KKS': f'{kks}VL0_Z0', 'text_kks': f'{kks}VL0'})

    def search_kks_in_ds_tpts_te_spec(self):
        """Поиск KKS на подмоделях DS_TPTS_TE_spec.svg """
        for i_line in self.full_description_of_the_submodel:
            if 'KKS' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                break
        else:
            self.static_element()
            return
        if kks.endswith('TE0'):
            self.signal_description.append({'KKS': f'{kks}_Z0', 'text_kks': kks})
        else:
            self.signal_description.append({'KKS': f'{kks}TE0_Z0', 'text_kks': f'{kks}TE0'})

    def button_submodel_processing(self):
        """Обработка подмодели obj_Button.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'type="OnClick">OU_Q' in i_line:
                self.signal_description.append({'KKS': '',
                                                'description': 'Кнопка "Квитировать"',
                                                'text_kks': ''})
                break
            elif 'type="OnClick">OU_T' in i_line:
                self.signal_description.append({'KKS': '',
                                                'description': 'Кнопка "Зажечь лампу"',
                                                'text_kks': ''})
                break
            elif '"OnClick">LoadNew' in i_line:
                try:
                    kks = re.findall(r'type="OnClick">LoadNew\("(.*)"\)</rt:event>', i_line)[0]
                except IndexError:
                    kks = re.findall(r'type="OnClick">LoadNew\(&quot;(.*)&quot;\)</rt:event>', i_line)[0]
                self.signal_description.append(
                    {
                        'KKS': '',
                        'description': f'Кнопка перехода на ВК "{kks}"',
                        'text_kks': kks
                    }
                )
                break
            elif '"OnClick">SendNew' in i_line:
                try:
                    kks = re.findall(r'type="OnClick">SendNew\("(.*)"\)</rt:event>', i_line)[0]
                except IndexError:
                    kks = re.findall(r'type="OnClick">SendNew\(&quot;(.*)&quot;\)</rt:event>', i_line)[0]
                self.signal_description.append(
                    {
                        'KKS': '',
                        'description': f'Кнопка перехода на ВК "{kks}"',
                        'text_kks': kks
                    }
                )
                break

    def station_submodel_processing(self):
        """Обработка подмодели obj_Station_stat.svg"""
        for i_line in self.full_description_of_the_submodel:
            if '"OnClick">SendNew' in i_line:
                try:
                    kks = re.findall(r'type="OnClick">SendNew\("(.*)"\)</rt:event>', i_line)[0]
                except IndexError:
                    kks = re.findall(r'type="OnClick">SendNew\(&quot;(.*)&quot;\)</rt:event>', i_line)[0]
                break
            elif '"OnClick">LoadNew' in i_line:
                try:
                    kks = re.findall(r'type="OnClick">LoadNew\("(.*)"\)</rt:event>', i_line)[0]
                except IndexError:
                    kks = re.findall(r'type="OnClick">LoadNew\(&quot;(.*)&quot;\)</rt:event>', i_line)[0]
                break
        else:
            self.static_element()
            return
        self.signal_description.append({
            'KKS': '',
            'description': f'Кнопка вызова видеокадра "{kks}" с флагами обобщенной индикации',
            'text_kks': kks})

    def instruction_submodel_processing(self):
        """Обработка подмодели obj_Button_instruction.svg, obj_ButtonH_icon_instr.svg, spds_instr_button.svg"""
        self.signal_description.append({'KKS': '',
                                        'description': 'Кнопка вызова инструкции по эксплуатации',
                                        'text_kks': ''})

    def search_kks_in_bin_indicator_txt(self):
        """Поиск KKS на подмоделях bin_mode_1o6.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'PointID' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                break
        else:
            self.static_element()
            return
        for i_line in self.full_description_of_the_submodel:
            if 'BitMask' in i_line:
                bit = re.findall(r'type="BitMask" mode="constant" value="(.*)"/>', i_line)[0]
                self.signal_description.append({'KKS': kks, 'bit': bit})
                return
        self.signal_description.append({'KKS': kks, 'text_kks': kks})

    def search_kks_in_bitwise_tablo_4bits(self):
        """Поиск KKS на подмоделях bin_mode_1o6.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'PointID' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                if ' ' in kks:
                    kks, bit = kks.split()
                    self.signal_description.append({'KKS': kks, 'bit': bit, 'text_kks': f'{kks} {bit}'})
                else:
                    self.signal_description.append({'KKS': kks, 'text_kks': kks})

    def search_kks_in_bin_tablo(self):
        """Поиск KKS на подмоделях bin_mode_1o6.svg, bin_tablo.svg, obj_Button_trend.svg, DS_TurbValve_control.svg,
        bin_tablo_OR3.svg, DS_ana_bar_AKNP.svg, DS_ana_ext_bounds.svg, ps_Len2_ana_AKNP.svg, ps_NVO_StepNumber.svg,
        bin_checkbox.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'PointID' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;', i_line)[0]
                if kks == 'NOLL':
                    continue
                elif '_' in kks:
                    self.signal_description.append({'KKS': kks, 'text_kks': kks})

    def search_kks_in_ds_reg_degree(self):
        """Поиск KKS на подмодели DS_Reg_degree.svg"""
        list_suffix = ['XQ08', 'AA1', 'AA2']
        kks = ''
        for i_line in self.full_description_of_the_submodel:
            if 'KKS' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                break
        if kks:
            if '_' in kks:
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
                return
        for i_line in self.full_description_of_the_submodel:
            if 'SIGNAL' in i_line:
                suffix = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                if '_' in suffix:
                    new_kks, suffix = suffix.split(separator='_')
                    self.signal_description.append({'KKS': suffix, 'text_kks': suffix})
                    return
                else:
                    self.signal_description.append({'KKS': f'{kks}_{suffix}', 'text_kks': f'{kks}_{suffix}'})
                    return
        else:
            for i_suffix in list_suffix:
                self.signal_description.append({'KKS': f'{kks}_{i_suffix}', 'text_kks': f'{kks}_{i_suffix}'})

    def search_kks_in_ds(self):
        """Поиск KKS на подмоделях DS_motor.svg, DS_CO_valve.svg, DS_reflux_valve.svg, DS_breaker.svg,
        DS_pulse_valve.svg, DS_CO_valve_rect.svg, DS_T_valve.svg, DS_setter.svg, DS_switch.svg,
        DS_Reg_pump.svg, DSB_CO_valve.svg"""
        data_nary = 'AUTO'
        for i_line in self.full_description_of_the_submodel:
            if 'DATA_NARY' in i_line:
                try:
                    data_nary = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                    break
                except IndexError:
                    break
        if data_nary == 'BIN':
            kks = ''
            for i_line in self.full_description_of_the_submodel:
                if 'KKS' in i_line:
                    try:
                        kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                        break
                    except IndexError:
                        break
            for i_line in self.full_description_of_the_submodel:
                if 'SIG_' in i_line:
                    suffix = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                    if suffix == 'NULL':
                        continue
                    if '_' in suffix:
                        self.signal_description.append({'KKS': suffix, 'text_kks': suffix})
                    else:
                        self.signal_description.append({'KKS': f'{kks}_{suffix}', 'text_kks': kks})
        elif data_nary == 'TPTS':
            for i_line in self.full_description_of_the_submodel:
                if 'KKS' in i_line:
                    try:
                        kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                        if kks == 'NULL':
                            self.static_element()
                            break
                        self.signal_description.append({'KKS': f'{kks}_Z0', 'text_kks': kks})
                        break
                    except IndexError:
                        break
        elif data_nary == 'AUTO':
            for i_line in self.full_description_of_the_submodel:
                if 'KKS' in i_line:
                    kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                    if '_' in kks:
                        self.signal_description.append({'KKS': kks, 'text_kks': kks.split('_')[0]})
                    elif kks == 'NULL':
                        continue
                    else:
                        self.signal_description.append({'KKS': f'{kks}_Z0', 'text_kks': kks})
                elif 'SIG_' in i_line:
                    kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                    if '_' in kks:
                        self.signal_description.append({'KKS': kks, 'text_kks': kks})
            if not len(self.signal_description):
                # print(f'{self.name_submodel} Найден статический элемент {self.full_description_of_the_submodel}')
                self.static_element()

        elif data_nary in ('KTPS', 'KTSu1', 'TYPEn'):

            self.static_element()
            print(self.name_submodel, data_nary)
        else:
            for i_line in self.full_description_of_the_submodel:
                if 'KKS' in i_line:
                    kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                    self.signal_description.append({'KKS': f'{kks}_{data_nary}', 'text_kks': kks})
                    break

    def search_kks_in_bin_indicator(self):
        """Поиск KKS в подмодели bin_indicator.svg, DS_TNT_MOD1.svg, ps_ana_bar_piecewise_lin_log_1.svg,
        DS_ana_bar_usr.svg"""
        for i_line in self.full_description_of_the_submodel:
            if 'PointID' in i_line:
                kks = re.findall(r'value="&quot;([^&]*)&quot;"', i_line)[0]
                break
        else:
            return
        if len(kks):
            if '_' in kks:
                self.signal_description.append({'KKS': kks, 'text_kks': kks})

    def search_kks_in_ps_laes2_ana_double_bound(self):
        """Поиск KKS в подмодели ps_LAES2_ana_DoubleBound.svg"""
        set_suffix: Set[str] = {'XQ01'}
        for i_line in self.full_description_of_the_submodel:
            if 'KKS' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                break
        else:
            return
        if len(kks):
            if '_' in kks:
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
            else:
                for i_line in self.full_description_of_the_submodel:
                    if 'Suffix' in i_line:
                        set_suffix.add(re.findall(r'value="&quot;(.*)&quot;"', i_line)[0])
                for i_suffix in set_suffix:
                    self.signal_description.append({'KKS': f'{kks}_{i_suffix}', 'text_kks': f'{kks}_{i_suffix}'})
        else:
            self.static_element()

    def search_kks_in_ps_len2_ds_ana(self):
        """Поиск KKS в подмодели ps_Len2_DS_ana.svg, DS_ana.svg, DS_ana_bar.svg, DS_ana_bar_h.svg,
        DS_ana_tenzor.svg, ana_bar_scale.svg, DS_ana_GetLocation.svg"""
        suffix = 'XQ01'
        for i_line in self.full_description_of_the_submodel:
            if 'FKKS' in i_line:
                kks = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                break
        else:
            return
        if len(kks):
            if '_' in kks:
                self.signal_description.append({'KKS': kks, 'text_kks': kks})
            else:
                for i_line in self.full_description_of_the_submodel:
                    if 'Suffix' in i_line:
                        try:
                            suffix = re.findall(r'value="&quot;(.*)&quot;"', i_line)[0]
                        except IndexError:
                            suffix = re.findall(r'value="&apos;(.*)&apos;"', i_line)[0]
                        break
                self.signal_description.append({'KKS': f'{kks}_{suffix}', 'text_kks': f'{kks}_{suffix}'})
        else:
            self.static_element()

    def search_kks_in_bool_checkbox(self):
        """Поиск KKS в подмодели bool_checkbox"""
        ...


if __name__ == '__main__':
    pass
