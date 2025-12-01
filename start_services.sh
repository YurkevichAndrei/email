#!/bin/bash

# Перейдем в директорию с приложением
cd app || { echo "Директория 'app' не найдена"; exit 1; }

# Проверка наличия конфигурационного файла
CONFIG_JSON="../config.json"
if [ ! -f "$CONFIG_JSON" ]; then
    echo "Файл конфигурации $CONFIG_JSON не найден"
    exit 1
fi

# Проверка наличия утилиты jq (для работы с JSON)
if ! command -v jq &> /dev/null; then
    echo "Ошибка: Утилита jq не установлена. Установите её: sudo apt install jq"
    exit 1
fi

# Извлечение параметров сервера из конфигурации
SERVER_HOST=$(jq -r '.report.server.host' "$CONFIG_JSON" | sed 's#http://##')
SERVER_PORT=$(jq -r '.report.server.port' "$CONFIG_JSON")

# Проверка успешности извлечения параметров
if [ -z "$SERVER_HOST" ] || [ -z "$SERVER_PORT" ]; then
    echo "Ошибка: Не удалось прочитать параметры сервера из конфигурации"
    exit 1
fi

# Запуск сервера FastAPI
echo "Запуск сервера FastAPI на $SERVER_HOST:$SERVER_PORT..."
uvicorn server:app --host "$SERVER_HOST" --port "$SERVER_PORT" &
FASTAPI_PID=$!

# Ждем, пока сервер запустится (примерно 2 секунды)
sleep 2

# Запуск Streamlit-приложения в фоновом режиме
echo "Запуск панели управления конфигурацией..."
streamlit run config_app.py &
STREAMLIT_PID=$!

# Ждем, пока Streamlit полностью запустится
sleep 3

# Проверка наличия утилиты для открытия браузера
OPEN_CMD="xdg-open"
if ! command -v $OPEN_CMD &> /dev/null; then
    OPEN_CMD="open"
fi

# Открываем веб-интерфейс Streamlit в браузере
$OPEN_CMD "http://localhost:8501"

# Запуск скрипта генерации отчета по расписанию
echo "Запуск скрипта генерации отчета по расписанию..."
python autoreport.py &
AUTOREPORT_PID=$!

# Ожидание завершения только FastAPI-сервера
wait $FASTAPI_PID
