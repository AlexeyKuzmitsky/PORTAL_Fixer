from PIL import Image
from typing import List, Tuple
from .point_description import AnchorPoint
from .general_functions import check_directory
from os import path
import re
from .timer import timer


def new_entry(list_submodel: List[AnchorPoint], img: Image) -> None:
    """Добавление на скриншот видеокадра нумерации подмоделей
    :param list_submodel: Список точек уже найденных на видеокадре.
    :param img: Объект Image скриншота видеокадра.
    :return None
    """
    for sub_model in list_submodel:
        x = sub_model.get_x() + sub_model.get_width() / 2 - 15
        x = round(x)
        y = sub_model.get_y() - 10
        y = round(y)
        # Добавление на скриншот изображения с номером элемента
        img.paste(sub_model.get_img(), (x, y), sub_model.get_img())


def new_submodel(list_constructor, list_submodel, name_svg: str) -> None:
    """
    Функция создания новой точки на видеокадре.
    :param list_constructor: Характеристики подмодели.
    :param list_submodel: Список точек уже найденных на видеокадре.
    :param name_svg: Название svg файла на котором находится подмодель.
    :return: None
    """
    submodel = AnchorPoint(full_description_of_the_submodel=list_constructor, name_svg=name_svg)
    submodel.set_name_submodel()
    if submodel.name_submodel:
        submodel.set_width_and_height()
        submodel.set_x_and_y()
        submodel.set_transform()
        submodel.search_kks_on_submodel()
        list_submodel.append(submodel)


def add_image(svg: str, width: int, height: int, name_directory: str) -> Image:
    """
    Функция обрабатывающая скриншот видеокадра приводящая к нужным размерам.
    :param svg: Имя обрабатываемого видеокадра в формате svg.
    :param width: Ширина видеокадра.
    :param height: Высота видеокадра.
    :param name_directory: Имя папки системы для которой подготавливается паспорт.
    :return: Обработанный объект Image скриншота видеокадра.
    """
    try:
        img = Image.open(path.join(name_directory, 'screen', f'{svg[:-3]}jpg'))
    except FileNotFoundError:
        print(f'В папке screen нет скриншота {svg[:-3]}jpg')
        return None
    number_1 = width/1916
    number_2 = height/962
    if number_1 > number_2:
        number = number_1
    else:
        number = number_2
    new_width = round(width / number)
    new_height = round(height / number)
    adjustment = round((1916 - new_width) / 2)
    img = img.crop((adjustment, 75, 1916 - adjustment, new_height + 75))
    img = img.resize((width, height))
    return img


def creating_list_of_submodel(svg_file, name_svg: str) -> List[AnchorPoint]:
    """
    Функция составляющая список подмоделей на видеокадре.
    :param svg_file: Файл svg проверяемого видеокадра.
    :param name_svg: Название svg файла.
    :return: Список найденных подмоделей.
    """
    list_submodel: List[AnchorPoint] = list()
    list_constructor: List[str] = list()
    flag_constructor = False

    for i_line in svg_file:
        if flag_constructor:
            if '</image>' in i_line:
                list_constructor.append(i_line)
                new_submodel(list_constructor=list_constructor,
                             list_submodel=list_submodel,
                             name_svg=name_svg)
                flag_constructor = False
                list_constructor.clear()
            else:
                list_constructor.append(i_line)
        else:
            if '<image' in i_line and '</image>' in i_line or '<image' in i_line and '/>' in i_line:
                list_constructor.append(i_line)
                new_submodel(list_constructor=list_constructor,
                             list_submodel=list_submodel,
                             name_svg=name_svg)
                list_constructor.clear()
            elif '<image' in i_line:
                flag_constructor = True
                list_constructor.clear()
                list_constructor.append(i_line)
    return list_submodel


def find_width_and_height(svg_file) -> Tuple:
    """
    Поиск ширины и высоты видеокадра.
    :param svg_file: Генератор строк svg файла.
    :return: Ширина и высота видеокадра
    """
    width: int = 1914
    height: int = 1000
    for i_line in svg_file:
        try:
            width = int(re.findall(r'width="([\d/.]*)"', i_line)[0])
            height = int(re.findall(r'height="([\d/.]*)"', i_line)[0])
            return width, height
        except IndexError:
            pass
    return width, height


def assigning_numbers_to_points(list_submodel) -> None:
    """
    Присваивание номеров точкам подмоделей отсортированным по расположению на видеокадре сверху вниз, слева на право.
    :param list_submodel: Список точек уже найденных на видеокадре.
    :return: None
    """
    # Сортировка точек на видеокадре сначала по y, потом по x.
    list_submodel = sorted(list_submodel, key=lambda point: (point.y, point.x))
    number_point = 0
    for i_submodel in list_submodel:
        number_point += 1
        i_submodel.set_number_point(number_point)
        i_submodel.creating_an_image_with_a_number()


@timer
def video_frame_parsing(svg: str, name_system: str) -> List[AnchorPoint]:
    """
    Функция принимающая KKS видеокадра на котором построчно ведется поиск начала кода подмодели. При нахождении кода,
    записывает его построчно в список list_constructor и запускает функцию add_kks с аргументом list_constructor.
    :param svg: Имя видеокадра формата svg.
    :param name_system: Имя папки системы для которой подготавливается паспорт.
    :return: Список найденных подмоделей.
    """
    with open(path.join(name_system, 'NPP_models', f'{svg}'), encoding='windows-1251') as svg_file:
        width, height = find_width_and_height(svg_file=svg_file)

        img = add_image(svg=svg, width=width, height=height, name_directory=name_system)
        if not img:
            print(f'Нет скриншота видеокадра {svg[:-4]}')
        list_submodel = creating_list_of_submodel(svg_file=svg_file, name_svg=svg)

        assigning_numbers_to_points(list_submodel=list_submodel)

    if path.isfile(path.join(name_system, 'screen', f'{svg[:-3]}jpg')):
        new_entry(list_submodel=list_submodel, img=img)
        try:
            img.save(path.join(name_system, 'screen_with_numbering', f'{svg[:-3]}jpg'))
        except FileNotFoundError:
            check_directory(path_directory=name_system, name_directory='screen_with_numbering')
            img.save(path.join(name_system, 'screen_with_numbering', f'{svg[:-3]}jpg'))
    else:
        print('Файл', path.join(name_system, 'screen', f'{svg[:-3]}jpg'), 'не найден')
    return list_submodel


if __name__ == "__main__":
    pass
