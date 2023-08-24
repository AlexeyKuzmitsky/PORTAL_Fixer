from PIL import Image, ImageFont, ImageDraw
from os import path


def new_image_number(number: int) -> None:
    """
    Функция создает новое изображение с переданным числом в круге.
    :param number: Число, которое будет отображено на картинке и как будет называться файл формата png.
    :return None:
    """
    img = Image.new('RGBA', (300, 300), (0, 0, 0, 0))
    text = str(number)
    idraw = ImageDraw.Draw(img)
    font_1 = ImageFont.truetype("arial.ttf", size=300)
    font_2 = ImageFont.truetype("arial.ttf", size=200)
    font_3 = ImageFont.truetype("arial.ttf", size=160)
    font = None
    x = 0
    y = 0
    if len(text) == 1:
        x = 70
        y = -15
        font = font_1
    elif len(text) == 2:
        x = 40
        y = 43
        font = font_2
    elif len(text) == 3:
        x = 15
        y = 70
        font = font_3
    idraw.ellipse((0, 0, 300, 300), fill='white', outline=(10, 10, 10), width=8)
    idraw.text((x, y), text, font=font, fill='black')
    new_image = img.resize((30, 30))
    new_image.save(path.join('circles_with_numbers', f'{number}.png'))


def resize_image(number: int) -> None:
    """Изменение размера изображений для их правильного размещения в будущем"""
    img = Image.open(path.join('circles_with_numbers', f'{number}.png'))
    new_image = img.resize((30, 30))
    new_image.save(path.join('circles_with_numbers_normal', f'{number}.png'))
    print(number)


if __name__ == '__main__':
    numbers = 500
    for i_num in range(1, numbers + 1):
        new_image_number(number=i_num)
