name_program = 'PORTAL_Fixer'
version_program = '2.8.2'
program_compilation_date = '2024.12.27'

program_directory_map = {
    'logs': None,
    'SVBU_1': {
        'data': {
            'TcpGate': None
        },
        'DbDumps': None,
        'DbSrc': None,
        'NPP_models': None,
        'NPP_models_new': None,
        'screen': None,
        'screen_with_numbering': None,
        'TcpGate': None,
        'Замечания по видеокадрам': None,
        'Ошибки в уставках': None,
        'Исходники': None
    },
    'SVBU_2': {
        'data': {
            'TcpGate': None
        },
        'DbDumps': None,
        'DbSrc': None,
        'NPP_models': None,
        'NPP_models_new': None,
        'screen': None,
        'screen_with_numbering': None,
        'TcpGate': None,
        'Замечания по видеокадрам': None,
        'Ошибки в уставках': None,
        'Исходники': None
    },
    'SVSU': {
        'data': {
            'TcpGate': None
        },
        'DbDumps': None,
        'DbSrc': None,
        'NPP_models': None,
        'new_NPP_models_SVSU': None,
        'screen': None,
        'screen_with_numbering': None,
        'TcpGate': None,
        'Замечания по видеокадрам': None,
        'Ошибки в уставках': None,
        'Исходники': None
    },
    'SKU_VP_1': {
        'data': None,
        'DbDumps': None,
        'DbSrc': None,
        'NPP_models': None,
        'NPP_models_new': None,
        'screen': None,
        'screen_with_numbering': None,
        'TcpGate': None,
        'Замечания по видеокадрам': None,
        'Ошибки в уставках': None,
        'Исходники': None
    },
    'SKU_VP_2': {
        'data': None,
        'DbDumps': None,
        'DbSrc': None,
        'NPP_models': None,
        'NPP_models_new': None,
        'screen': None,
        'screen_with_numbering': None,
        'TcpGate': None,
        'Замечания по видеокадрам': None,
        'Ошибки в уставках': None,
        'Исходники': None
    }
}

color_button = '#A0C49D'
color_background = '#C4D7B2'

dict_level_signale = {
    'YP11': 'Аварийная',
    'YP61': 'Аварийная',
    'YP12': 'Предупредительная',
    'YP62': 'Предупредительная',
    'YP13': 'Технологическая',
    'YP47': 'Архивирование',
}

dict_suffix_level_signale = {
    'XH49': 'Аварийная',
    'XH99': 'Аварийная',
    'XH45': 'Аварийная',
    'XH95': 'Аварийная',
    'XH44': 'Аварийная',
    'XH94': 'Аварийная',
    'XH48': 'Аварийная',
    'XH98': 'Аварийная',
    'XH05': 'Аварийная',
    'XH55': 'Аварийная',
    'XH06': 'Аварийная',
    'XH56': 'Аварийная',
    'XH47': 'Предупредительная',
    'XH97': 'Предупредительная',
    'XH43': 'Предупредительная',
    'XH93': 'Предупредительная',
    'XH42': 'Предупредительная',
    'XH92': 'Предупредительная',
    'XH46': 'Предупредительная',
    'XH96': 'Предупредительная',
    'XH03': 'Предупредительная',
    'XH53': 'Предупредительная',
    'XH04': 'Предупредительная',
    'XH54': 'Предупредительная',
    'XH41': 'Технологическая',
    'XH91': 'Технологическая',
    'XH40': 'Технологическая',
    'XH90': 'Технологическая',
    'XH01': 'Технологическая',
    'XH51': 'Технологическая',
    'XH02': 'Технологическая',
    'XH52': 'Технологическая',
    'ZH49': 'Аварийная',
    'ZH99': 'Аварийная',
    'ZH45': 'Аварийная',
    'ZH95': 'Аварийная',
    'ZH44': 'Аварийная',
    'ZH94': 'Аварийная',
    'ZH48': 'Аварийная',
    'ZH98': 'Аварийная',
    'ZH05': 'Аварийная',
    'ZH55': 'Аварийная',
    'ZH06': 'Аварийная',
    'ZH56': 'Аварийная',
    'ZH47': 'Предупредительная',
    'ZH97': 'Предупредительная',
    'ZH43': 'Предупредительная',
    'ZH93': 'Предупредительная',
    'ZH42': 'Предупредительная',
    'ZH92': 'Предупредительная',
    'ZH46': 'Предупредительная',
    'ZH96': 'Предупредительная',
    'ZH03': 'Предупредительная',
    'ZH53': 'Предупредительная',
    'ZH04': 'Предупредительная',
    'ZH54': 'Предупредительная',
    'ZH41': 'Технологическая',
    'ZH91': 'Технологическая',
    'ZH40': 'Технологическая',
    'ZH90': 'Технологическая',
    'ZH01': 'Технологическая',
    'ZH51': 'Технологическая',
    'ZH02': 'Технологическая',
    'ZH52': 'Технологическая',
}


column_descriptions_ana = {
    'PVNR': 'Номер переменной',
    'CATEGORYTEXT': 'Обозначение в системе РТМ',
    'PVTEXT': 'Сокращенное описание на русском языке',
    'BOUND_HIGH3': 'Верхняя аварийная граница',
    'BOUND_HIGH2': 'Верхняя предупредительная граница',
    'BOUND_HIGH1': 'Верхняя технологическая граница',
    'BOUND_LOW1': 'Нижняя технологическая граница',
    'BOUND_LOW2': 'Нижняя предупредительная граница',
    'BOUND_LOW3': 'Нижняя аварийная граница',
    'DIMSTRING': 'Единицы измерения на русском языке (табл. PLS_DIMENSION_CONF)',
    'DEADBAND': 'Зона нечувствительности изменения сигнала',
    'HIST_DEADBAND': 'Зона нечувствительности изменения сигнала для архивации',
    'PLC_ITEMID': 'номер канала ППД',
    'CATEGORYNR': 'тип телеграммы-источника или приёмника',
    'PVCATEGORIES': 'Категория переменной',
    'PRJSPECNR': 'Адресат сигнализации табл. PLS_PROC_CATEGORIES',
    'ALARMPRIORITYLEVEL': 'Уровень сигнализации (табл. PLS_PROC_CATEGORIES)',
    'HISTORIANSUPPORTED': 'Разрешение архивирования (табл. PLS_PROC_CATEGORIES)',
    'CHANGETIME': 'Время последнего изменения конфигурации',
    'CHANGEUSERNR': 'Автор изменения конфигурации',
    'INITTYPE': 'Способ иницализации при старте системы',
    'INITVAL': 'Начальное значение при INITTYPE = PVINIT_VALUE',
    'ACCINTERVALNR1': 'Длительность интервала аккумуляции 1',
    'ACCMASK1': 'Способы аккумуляции интервала 1',
    'ACCINTERVALNR2': 'Длительность интервала аккумуляции 2',
    'PLC_LINENR': 'Адрес оборудования ввода-вывода',
    'PLC_RANGELOW': 'Нижний предел от оборудования',
    'PLC_RANGEHIGH': 'Верхний предел от оборудования',
    'DEADBANDRELATIVE': 'Относительная зона нечувствительности',
    'STATIONID': 'Имя станции (группы). Используется для классификации PV по системам',
    'DERIVED_EXPR': 'Выражение для вычисления производной переменной',
    'CATEGORYMAP3': 'Битовая маска пользователей - получателей сигнализации',
    'ROUNDDIGITS': 'Количество знаков после запятой',
    'RANGELOW': 'Нижняя граница диапазона значений',
    'RANGEHIGH': 'Верхняя граница диапазона значений',
    'DAEDBAND': 'Значение зоны нечувствительности',
    'HIST_DAEDBAND': 'Зона нечувствительности при архивировании',
    'HIST_TIME_SEC': 'Шаг архивирования',
    'HIST_FLAGS': 'Флаг архивирования',
    'PVID': 'Имя переменной',
    'PVDESCRIPTION': 'Описание переменной',
    'ALTSTATIONID': 'Имя альтернитивной станции'
}

column_descriptions_bin = {
    'PVNR': 'Номер PV',
    'ISVALID': 'Флаг корректности записи',
    'PVCATEGORIES': 'Категория переменной',
    'CATEGORYNR': 'Код категории',
    'STATIONNR': 'Номер станции',
    'ALTSTATIONNR': 'Номер альтернативной станции',
    'CHANGETIME': 'Время последнего изменения конфигурации',
    'CHANGEUSERNR': 'Автор изменения конфигурации',
    'NUMBITS': 'Количество значащих бит',
    'CATEGORYMAP3': 'Битовая маска пользователей - получателей сигнализации',
    'PRJSPECNR1': 'Битовая маска пользователей - получателей управления'
}
# priority_level = {
#     'H0': 7,
#     'A1': 7,
#
#     'A2': 4,
#     'W2': 3,
#     'T3': 2,
#     'C3': 2,
#     'D4': 2,
#     'YP11': 6,
#     'YP12': 4,
#
# }
