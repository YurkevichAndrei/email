import json
from datetime import datetime, date
import smtplib
import os
from email.message import EmailMessage
from openpyxl import Workbook

from db import DataBase

class Report:
    def __init__(self):
        self.db = DataBase()
        self.db.update_db()
        self.config = {}
        self.load_config()

    def load_config(self):
        with open('../config.json', 'r') as config_file:
            self.config = json.load(config_file)

    @staticmethod
    def filter_report(data, keys):
        return {key: value for key, value in data.items() if key in keys}

    def generate_report(self):
        reports = self.db.get_reports(date.today())
        reports = self.filter_report(reports, self.config['report']['users'])
        data = self.add_all_count_data(self.transform_data(reports))
        report_path = self.create_excel_from_dict_list(data,
                                                  f'report_{datetime.now().strftime('%d-%m-%Y_%H:%M')}.xlsx',
                                                  'report')
        return report_path

    def send_email(self, report_path):
        sender_email = self.config['email']['sender']['email']
        sender_password = self.config['email']['sender']['password']

        messages = []
        with open(report_path, 'rb') as file:
            report_data = file.read()
            report_name = os.path.basename(report_path)
            for recipient_email in self.config['email']['recipient']['emails']:
                msg = EmailMessage()
                msg['Subject'] = 'Ежедневный отчет'
                msg['From'] = sender_email
                msg['To'] = recipient_email
                msg.set_content("Ежедневный отчет")
                msg.add_attachment(report_data, maintype='application', subtype='octet-stream', filename=report_name)
                messages.append(msg)

        with smtplib.SMTP(self.config['email']['smtp']['host'], self.config['email']['smtp']['port']) as smtp:
            smtp.starttls()
            smtp.login(self.config['email']['sender']['username'], sender_password)
            for msg in messages:
                smtp.send_message(msg)

    def daily_task(self):
        report_path = self.generate_report()
        self.send_email(report_path)
        return True

    def transform_data(self, input_dict):
        """
        Преобразует словарь с данными пользователей в список словарей с количеством элементов.

        Args:
            input_dict (dict): Исходный словарь формата {user_id: {category: list, ...}}

        Returns:
            list: Список словарей формата [{user_id: int, category: count, ...}]
        """
        result = []

        users = self.db.get_users()

        for user_id, user_data in input_dict.items():
            if user_id == -1:
                continue
            user_dict = {'Номер': user_id,
                         'Имя пользователя': users[user_id]['username'],
                         'Имя Фамилия': users[user_id]['name']}

            for category, item in user_data.items():
                # Добавляем количество элементов для каждой категории
                user_dict[category] = item

            result.append(user_dict)

        return result

    @staticmethod
    def add_all_count_data(data: list[dict]):
        count_data_dict = {'Номер': '',
                           'Имя пользователя': '',
                           'Имя Фамилия': 'Итого'}
        for user_dict in data:
            item_list = [(category, item) for category, item in user_dict.items()]

            for i in range(3, len(item_list)):
                if count_data_dict.get(item_list[i][0]) is None:
                    count_data_dict[item_list[i][0]] = item_list[i][1]
                else:
                    count_data_dict[item_list[i][0]] += item_list[i][1]
        data.append(count_data_dict)
        return data

    def create_excel_from_dict_list(self, dict_list: list, output_filename: str, sheet_name='Sheet1'):
        # Создаем директорию, если она не существует
        if not os.path.exists(self.config['report']['folder_path']):
            os.makedirs(self.config['report']['folder_path'])

        filepath = os.path.join(self.config['report']['folder_path'], output_filename)

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

# rep = Report()
# rep.daily_task()
