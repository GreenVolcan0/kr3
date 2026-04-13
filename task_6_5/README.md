# Task 6.5 — JWT + Register + Rate Limiting

## Установка и запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Тестирование

```bash
# Регистрация (лимит 1 запрос/минута)
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}' \
  http://localhost:8000/register

# Повторная регистрация → 409
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}' \
  http://localhost:8000/register

# Логин (лимит 5 запросов/минута)
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}' \
  http://localhost:8000/login

# Неверный пароль → 401
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"wrong"}' \
  http://localhost:8000/login

# Несуществующий пользователь → 404
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"nobody","password":"x"}' \
  http://localhost:8000/login

# Защищённый ресурс (подставь токен из /login)
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/protected_resource
```
