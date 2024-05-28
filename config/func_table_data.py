from pandas import DataFrame, ExcelWriter
from typing import List
from modernization_objects.q_widget import InformationWindow
from PyQt6.QtWidgets import QApplication


def save_data_to_txt_file(data: List[List[str]], list_name_column: List[str], path: str):
    """
    Функция сохранения данных в текстовый файл
    """
    df = DataFrame(data, columns=list_name_column)
    df.to_csv(path, sep='|', index=False)
    app = QApplication([])
    window = InformationWindow(text=f' Файл {path} \n успешно сохранен', message_type='successfully')

    window.show()
    app.exec()


def save_data_to_xlsx_file(data: List[List[str]], list_name_column: List[str], path: str):
    """
    Функция сохранения данных в файл excel
    """
    sheet_name = f'{path.split('/')[-1][:-5]}'
    excel_writer = ExcelWriter(path, engine='xlsxwriter')
    df = DataFrame(data, columns=list_name_column)
    df.to_excel(excel_writer, index=False, sheet_name=sheet_name)

    worksheet = excel_writer.sheets[sheet_name]

    for i, name_col in enumerate(df.columns):
        max_len = max(df[name_col].astype(str).map(len).max(), len(name_col)*1.3)
        worksheet.set_column(i, i, max_len)
    excel_writer.close()
    app = QApplication([])
    window = InformationWindow(text=f' Файл {path} \n успешно сохранен', message_type='successfully')

    window.show()
    app.exec()
