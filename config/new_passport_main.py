import os

from .new_passport_screenshot_processing import video_frame_parsing
from .general_functions import check_directory
from .get_logger import log_info_print
from os import system


def start_program_new_passport():
    while True:
        number_procedure = input('Программа создания новый паспортов для видеокадров\n'
                                 '1. СВБУ_1\n' 
                                 '2. СВБУ_2\n'
                                 '3. СКУ_ВП_1\n'
                                 '4. СКУ_ВП_2\n '
                                 '[0].  Выход\n'
                                 '  -> ')
        if number_procedure == '1':
            system('cls')
            log_info_print.info(f'Старт программы обновления видеокадров из списка самых актуальных')
            program_new_passport()
            system('cls')
        elif number_procedure == '2':
            system('cls')
            program_new_passport()
            log_info_print.info(f'Старт программы блокировки неактивных кнопок вызова')
            system('cls')
        elif number_procedure == '0' or number_procedure == '':
            log_info_print.info(f'Выход из программы создания новых паспортов на видеокадры')
            break


def program_new_passport():
    name_system = 'SVBU_1'
    check_directory(path_directory=name_system, name_directory='screen')

    list_name_svg = os.listdir(os.path.join(name_system, 'NPP_models'))
    try:
        list_name_svg.remove('diag_WS.svg')
    except ValueError:
        pass
    number_name_svg = len(list_name_svg)
    num = 1020
    for name_svg in list_name_svg[num:]:
        if not name_svg.endswith('.svg'):
            print(f'Найден файл {name_svg} не являющийся svg файлом')
            continue
        num += 1
        print(f'[{num}/{number_name_svg}] Проверка {name_svg}', end='\t')

        list_submodel = video_frame_parsing(svg=name_svg, name_system=name_system)


if __name__ == '__main__':
    start_program_new_passport()
