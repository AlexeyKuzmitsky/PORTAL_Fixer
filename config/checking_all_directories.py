from os import path, mkdir
from typing import Dict


def checking_the_program_operating_environment(directory_map: Dict, path_directory: str = ''):
    """
    Функция проверяет наличие всех папок для работы программы. Если нужной папки нет, создает
    :return: None
    """
    for i_directory, nested_directories in directory_map.items():
        check_directory(path_directory=path_directory, name_directory=i_directory)
        if nested_directories:
            new_path = path.join(path_directory, i_directory)
            checking_the_program_operating_environment(directory_map=nested_directories, path_directory=new_path)


def check_directory(path_directory: str, name_directory: str):
    """
    Функция проверяет наличие директории по указанному адресу и при ее отсутствии создает ее.
    :param path_directory: Путь к директории.
    :param name_directory: Имя директории.
    :return: True - создана новая директория, False - новая директория не создавалась(уже существовала)
    """
    if path_directory == '':
        if not path.isdir(name_directory):
            mkdir(name_directory)
    else:
        if not path.isdir(path.join(path_directory, name_directory)):
            mkdir(path.join(path_directory, name_directory))
