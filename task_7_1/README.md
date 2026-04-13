# Task 7.1 — RBAC (Role-Based Access Control) with JWT

## Установка и запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Роли и разрешения

| Роль  | create | read | update | delete |
|-------|--------|------|--------|--------|
| admin | ✅     | ✅   | ✅     | ✅     |
| user  | ❌     | ✅   | ✅     | ❌     |
| guest | ❌     | ✅   | ❌     | ❌     |

## Тестирование

```bash
# Регистрация admin
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"adminuser","password":"adminpass","role":"admin"}' \
  http://localhost:8000/register

# Регистрация user
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"regularuser","password":"userpass","role":"user"}' \
  http://localhost:8000/register

# Регистрация guest
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"guestuser","password":"guestpass","role":"guest"}' \
  http://localhost:8000/register

# Логин (получаем токен)
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"adminuser","password":"adminpass"}' \
  http://localhost:8000/login

# Защищённый ресурс (admin/user) — подставь свой токен
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/protected_resource

# Только admin: создать ресурс
curl -X POST -H "Authorization: Bearer <ADMIN_TOKEN>" http://localhost:8000/admin/resource

# Только admin: удалить ресурс
curl -X DELETE -H "Authorization: Bearer <ADMIN_TOKEN>" http://localhost:8000/admin/resource/1

# user/admin: чтение
curl -H "Authorization: Bearer <USER_TOKEN>" http://localhost:8000/user/resource

# user/admin: обновление
curl -X PUT -H "Authorization: Bearer <USER_TOKEN>" http://localhost:8000/user/resource/1

# guest попытается удалить → 403
curl -X DELETE -H "Authorization: Bearer <GUEST_TOKEN>" http://localhost:8000/admin/resource/1
```
