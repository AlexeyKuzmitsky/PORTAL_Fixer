from os import path, system, mkdir


if not path.isdir('logs'):
    mkdir('logs')
    print('Нет папки "logs". Папка "logs" создана.')


from config.altstation_main import run_the_program_to_create_alt_stations
from config.SVSU_import_file import start_program_svsu_import
from config.parsing_svg import start_program_parsing_svg
from config.get_logger import log_info
from config.new_passport_main import start_program_new_passport
from config.generation_tcp_gate_file import start_program_generation_tcp_gate


name_program = 'PORTAL_Fixer'
version_program = '1.7.7'
program_compilation_date = '2023.08.19'


def instruction() -> None:
    with open(path.join('config', 'Инструкция.txt'), 'r', encoding='ANSI') as file:
        print()
        print('='*92)
        for i_line in file:
            print('|{:90}|'.format(i_line[:-1]))
        print('='*92)
        print()


def main_menu_of_the_program() -> None:
    print(f'{name_program} - v.{version_program}. Дата сборки - {program_compilation_date}\n')
    log_info.info('+++Загрузка программы+++')
    while True:
        try:
            menu_item = input('Какую программу запустить?\n'
                              '1. Программа создания файла SVSU_import и обновления ВК SVSU\n'
                              '2. Программа поиска замечаний на ВК\n'
                              '3. Программа создания файла altStation\n'
                              '4. Программа создания новых паспортов для видеокадров\n'
                              '5. Программа создания файлов для TcpGate\n'
                              '6. Инструкция\n'
                              '[0]. Закрыть программу\n'
                              ' -> ')
            if menu_item == '1':
                system('cls')
                log_info.info('Старт программы создания файла SVSU_import и обновления ВК SVSU')
                start_program_svsu_import()
                system('cls')
            elif menu_item == '2':
                system('cls')
                log_info.info('Старт программы поиска замечаний на видеокадрах')
                start_program_parsing_svg()
                system('cls')
            elif menu_item == '3':
                system('cls')
                log_info.info('Старт программы создания файла altStation')
                run_the_program_to_create_alt_stations()
                system('cls')
            elif menu_item == '4':
                system('cls')
                log_info.info('Старт программы создания новых паспортов для видеокадров')
                start_program_new_passport()
                system('cls')
            elif menu_item == '5':
                system('cls')
                log_info.info('Программа создания файлов для TcpGate')
                start_program_generation_tcp_gate()
                system('cls')
            elif menu_item == '6':
                system('cls')
                instruction()
            elif menu_item == '0' or menu_item == '':
                log_info.info('---Закрытие программы---')
                break
            else:
                system('cls')
                print('Неверно введен пункт меню!!\n')

        # except ZeroDivisionError as e:
        except Exception as e:
            print('Произошла критическая ошибка. Сообщите разработчику об этом и передайте файл logs/ERRORS.log')
            print(e)
            log_info.error('Критическая ошибка', exc_info=True)


if __name__ == '__main__':
    main_menu_of_the_program()
