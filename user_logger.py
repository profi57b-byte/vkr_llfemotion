from datetime import datetime
import os

LOG_FILE = "users_log.txt"

def log_user_data(user_id, user_name, mood):
    """
    Записывает данные пользователя в файл users_log.txt.
    """
    try:
        # Создаем файл, если он не существует
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", encoding="utf-8") as file:
                file.write("Дата и время | ID пользователя | Имя | Настроение\n")

        # Записываем данные
        with open(LOG_FILE, "a", encoding="utf-8") as file:
            log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | ID: {user_id} | Имя: {user_name} | Настроение: {mood}\n"
            file.write(log_entry)

    except Exception as e:
        print(f"Ошибка при записи в лог: {e}")

def read_logs():
    """
    Читает и возвращает данные из файла users_log.txt.
    """
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError:
        return []
