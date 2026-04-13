# Task 8.1 — SQLite Register Endpoint

## Установка и запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Таблица `users` создаётся автоматически при первом запуске (`CREATE TABLE IF NOT EXISTS`).

## Тестирование

```bash
# Регистрация пользователя
curl -X POST 'http://127.0.0.1:8000/register' \
  -H 'Content-Type: application/json' \
  -d '{"username": "test_user", "password": "12345"}'

# Ожидаемый ответ:
# {"message": "User registered successfully!"}
```

## Проверка данных в БД

Открой `users.db` через **DB Browser for SQLite** или выполни:

```bash
sqlite3 users.db "SELECT * FROM users;"
```
