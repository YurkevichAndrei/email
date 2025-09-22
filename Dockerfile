FROM python:3.11-slim

# Системные библиотеки (Pillow/OpenCV и т.п.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

# pipreqs — не лучшая идея для продакшена, но оставим как у тебя
# torch/torchvision отсюда будут CPU-сборки
RUN pip install --no-cache-dir pipreqs torch torchvision

# Кладём код до генерации requirements
COPY app/ ./app/

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
CMD ["streamlit", "run", "app/app.py"]