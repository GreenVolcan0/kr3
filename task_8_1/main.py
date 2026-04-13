from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from database import create_tables, get_db_connection

# Создаём таблицу при старте приложения
create_tables()

app = FastAPI(title="Task 8.1 - SQLite Register")


# ---------- Модель ----------

class User(BaseModel):
    username: str
    password: str


# ---------- Маршруты ----------

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: User):
    """Регистрирует пользователя — сохраняет в таблицу users (SQLite)."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (user.username, user.password),
        )
        conn.commit()
    finally:
        conn.close()

    return {"message": "User registered successfully!"}
