import schedule
import time
from datetime import datetime
import os
import json
import requests

# Проверка, что сегодня будний день (0-4 = понедельник-пятница)
def is_weekday():
    return datetime.now().weekday() < 5  # 0-4 = пн-пт

def load_config():
    try:
        if os.path.exists('../config.json'):
            with open('../config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass

    # Конфигурация по умолчанию
    default_config = {
        "report": {
            "server": {
                "host": "http://127.0.0.1",
                "port": 5152
            }
        }
    }
    return default_config

def scheduled_job():
    if is_weekday():
        config = load_config()
        print(f"{datetime.now()} - Отправлен запрос на генерацию отчета...")
        requests.get(f"{config['report']['server']['host']}:{config['report']['server']['port']}/report/new")

# Запланировать выполнение каждый день в 23:00
schedule.every().day.at("23:00").do(scheduled_job)

print(f"{datetime.now()} - Скрипт запущен. Ожидание выполнения задач...")
while True:
    schedule.run_pending()
    time.sleep(60)  # Проверка каждую минуту