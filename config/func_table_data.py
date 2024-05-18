import pandas as pd
from typing import List


def save_data_to_txt_file(data: List[List[str]], list_name_column: List[str], path: str):
    """
    Функция сохранения данных в текстовый файл
    """
    df = pd.DataFrame(data, columns=list_name_column)
    df.to_csv(path, sep='|', index=False)


def save_data_to_xlsx_file(data: List[List[str]], list_name_column: List[str], path: str):
    """
    Функция сохранения данных в файл excel
    """
    sheet_name = f'{path.split('/')[-1][:-5]}'
    excel_writer = pd.ExcelWriter(path, engine='xlsxwriter')
    df = pd.DataFrame(data, columns=list_name_column)
    df.to_excel(excel_writer, index=False, sheet_name=sheet_name)

    worksheet = excel_writer.sheets[sheet_name]

    for i, name_col in enumerate(df.columns):
        max_len = max(df[name_col].astype(str).map(len).max(), len(name_col)*1.3)
        worksheet.set_column(i, i, max_len)
    excel_writer.close()
