from datetime import datetime
import smtplib
import os
from email.message import EmailMessage
from openpyxl import Workbook

from db import DataBase

def generate_report():
    report_content = f"Ежедневный отчет за {datetime.now().strftime('%Y-%m-%d')}\n\nДанные отчета..."
    report_path = 'daily_report.txt'
    with open(report_path, 'w') as file:
        file.write(report_content)
    return report_path

def send_email(report_path, recipient_email):
    sender_email = "ayurkevich@npomis.ru"
    sender_password = "ePu9ahga"

    msg = EmailMessage()
    msg['Subject'] = 'Ежедневный отчет'
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg.set_content("Пожалуйста, найдите прикрепленный ежедневный отчет.")

    with open(report_path, 'rb') as file:
        report_data = file.read()
        report_name = os.path.basename(report_path)
        msg.add_attachment(report_data, maintype='application', subtype='octet-stream', filename=report_name)

    with smtplib.SMTP('smtp.npomis.ru', 25) as smtp:
        smtp.starttls()
        smtp.login("ayurkevich", sender_password)
        smtp.send_message(msg)

def daily_task():
    report_path = generate_report()
    send_email(report_path, "ad6803884@yandex.ru")

def transform_data(input_dict):
    """
    Преобразует словарь с данными пользователей в список словарей с количеством элементов.

    Args:
        input_dict (dict): Исходный словарь формата {user_id: {category: list, ...}}

    Returns:
        list: Список словарей формата [{user_id: int, category: count, ...}]
    """
    result = []

    for user_id, user_data in input_dict.items():
        user_dict = {'user_id': user_id}

        for category, items in user_data.items():
            # Добавляем количество элементов для каждой категории
            user_dict[category] = len(items)

        result.append(user_dict)

    return result

def create_excel_from_dict_list(dict_list: list, output_filename: str, sheet_name='Sheet1'):
    # Создаем директорию, если она не существует
    if not os.path.exists('excel_files'):
        os.makedirs('excel_files')

    filepath = os.path.join('excel_files', output_filename)

    # Создаем новую книгу Excel
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    # Записываем данные из списка словарей в Excel
    if dict_list:
        header = list(dict_list[0].keys())
        ws.append(header)  # Записываем заголовки

        for row in dict_list:
            ws.append([row[col] for col in header])

    # Автоматическое изменение ширины столбцов
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # Сохраняем файл
    wb.save(filepath)
    return filepath
