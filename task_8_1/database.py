import sqlite3

DB_PATH = "users.db"


def get_db_connection():
    """Возвращает подключение к SQLite с включёнными row_factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """Создаёт таблицу users, если её ещё нет."""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL,
            password TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()
