# Task 6.4 — JWT Authentication

## Установка и запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Тестирование

> Заглушка `authenticate_user` возвращает True/False случайно.
> Попробуй несколько раз, пока не получишь токен.

```bash
# Логин (может вернуть 401 или токен — случайно)
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"securepassword123"}' \
  http://localhost:8000/login

# Доступ к защищённому ресурсу (подставь свой токен)
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/protected_resource

# Без токена → 403
curl http://localhost:8000/protected_resource

# С неверным токеном → 401
curl -H "Authorization: Bearer invalid.token.here" \
  http://localhost:8000/protected_resource
```
