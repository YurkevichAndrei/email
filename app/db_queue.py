import sqlite3
import queue
import threading
from typing import Any, Optional

class DatabaseQueue:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.request_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._database_worker, daemon=True)
        self.worker_thread.start()

    def _database_worker(self):
        """Рабочий поток для выполнения запросов"""
        conn = sqlite3.connect(self.db_path, timeout=10.0)  # Таймаут 10 секунд
        conn.execute("PRAGMA busy_timeout = 5000")  # 5 секунд ожидания блокировки

        while True:
            try:
                # Получаем запрос из очереди
                query, params, result_queue, event = self.request_queue.get()

                if query is None:  # Сигнал завершения
                    break

                try:
                    cursor = conn.cursor()
                    cursor.execute(query, params)

                    if query.strip().upper().startswith('SELECT'):
                        result = cursor.fetchall()
                    else:
                        conn.commit()
                        result = cursor.rowcount

                    # Отправляем результат
                    result_queue.put(('success', result))

                except Exception as e:
                    conn.rollback()
                    result_queue.put(('error', str(e)))

                # Сигнализируем о завершении обработки
                event.set()

            except Exception as e:
                # Обработка ошибок в рабочем потоке
                if 'result_queue' in locals():
                    result_queue.put(('error', f"Worker error: {str(e)}"))

    def execute(self, query: str, params: Optional[list] = None) -> Any:
        """Выполнение запроса с ожиданием результата"""
        if params is None:
            params = []

        result_queue = queue.Queue()
        completion_event = threading.Event()

        # Помещаем запрос в очередь
        self.request_queue.put((query, params, result_queue, completion_event))

        # Ждем завершения обработки
        completion_event.wait()

        # Получаем результат
        status, result = result_queue.get()

        if status == 'error':
            raise Exception(f"Database error: {result}")

        return result

    def close(self):
        """Завершение работы очереди"""
        self.request_queue.put((None, None, None, None))

# Использование
# db_queue = DatabaseQueue('my_database.db')
#
# try:
#     # Этот вызов будет ждать завершения запроса
#     result = db_queue.execute("SELECT * FROM users WHERE id = ?", [1])
#     print(f"Результат: {result}")
#
#     # Вставка данных
#     rows_affected = db_queue.execute(
#         "INSERT INTO users (name, email) VALUES (?, ?)",
#         ["John", "john@example.com"]
#     )
#     print(f"Добавлено строк: {rows_affected}")
#
# finally:
#     db_queue.close()