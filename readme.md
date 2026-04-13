# Task 6.1 — Basic HTTP Auth `/login`

## Установка и запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Тестирование

```bash
# Успешный логин
curl -u admin:secret123 http://localhost:8000/login

# Неверный пароль → 401
curl -u admin:wrongpass http://localhost:8000/login

# Без учётных данных → 401
curl http://localhost:8000/login
```