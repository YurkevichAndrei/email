FROM python:3.11-slim

# Системные библиотеки (Pillow/OpenCV и т.п.)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential cron tzdata
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

# Копируем файл crontab в нужную директорию
COPY my-crontab /etc/cron.d/my-crontab

# Даем файлу crontab необходимые права (владелец - root, права на чтение)
RUN chmod 0644 /etc/cron.d/my-crontab

ENV TZ=Europe/Moscow

# Применяем crontab
RUN crontab /etc/cron.d/my-crontab

# Создаем файл для логов (опционально, чтобы tail мог его читать)
RUN touch /var/log/cron.log

# Запускаем cron в foreground режиме и начинаем следить за лог-файлом
CMD ["sh", "-c", "crond -f | tail -f /var/log/cron.log"]

# Кладём код до генерации requirements
COPY app/ ./app/

# pipreqs — не лучшая идея для продакшена, но оставим как у тебя
RUN pip install --no-cache-dir pipreqs

# Генерим requirements по импортам (НЕрепродюсибл, но как у тебя)
RUN pipreqs ./app --force --encoding=utf-8 --savepath /app/requirements.txt

# # Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt


# Настройки streamlit: слушаем на 127.0.0.1 и на нужном порту
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=50001 \
    STREAMLIT_SERVER_ADDRESS=127.0.0.1

EXPOSE 50001

# Запуск приложения
CMD ["cd", "app", "&&", "streamlit", "run", "config_app.py"]