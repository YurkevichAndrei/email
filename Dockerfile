FROM python:3.13-slim

# Установка часового пояса и системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Europe/Moscow

WORKDIR /app

# Копируем зависимости ДО кода для лучшего кэширования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app/ ./app/

# Настройка cron
COPY app/my-crontab /etc/cron.d/my-crontab
RUN chmod 0644 /etc/cron.d/my-crontab && \
    crontab /etc/cron.d/my-crontab && \
    touch /var/log/cron.log

# Настройки Streamlit
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=50001 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 50001

# Запуск через shell чтобы управлять несколькими процессами
CMD ["sh", "-c", "cron && cd app && streamlit run config_app.py"]