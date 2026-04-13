# Task 6.2 — Hashed Passwords + Register/Login

## Установка и запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Тестирование

```bash
# Регистрация
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"correctpass"}' \
  http://localhost:8000/register

# Успешный логин
curl -u user1:correctpass http://localhost:8000/login

# Неверный пароль → 401
curl -u user1:wrongpass http://localhost:8000/login
```
