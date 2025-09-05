from datetime import datetime
import smtplib
import os
from email.message import EmailMessage
import schedule
import time

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

    with smtplib.SMTP('smtp.npomis.ru', 587) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)

def daily_task():
    report_path = generate_report()
    send_email(report_path, "ad6803884@yandex.ru")

daily_task()
# schedule.every().day.at("08:00").do(daily_task)
#
# print("Запуск ежедневного задания для отправки отчетов по электронной почте.")
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)
