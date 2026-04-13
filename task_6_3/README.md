# Task 6.3 — DEV/PROD Docs Access Control

## Установка и запуск

```bash
pip install -r requirements.txt
cp .env.example .env   # отредактируй при необходимости
uvicorn main:app --reload
```

## Переменные окружения (.env)

| Переменная    | Описание                          | По умолчанию  |
|---------------|-----------------------------------|---------------|
| MODE          | DEV или PROD                      | DEV           |
| DOCS_USER     | Логин для доступа к /docs (DEV)   | docsadmin     |
| DOCS_PASSWORD | Пароль для доступа к /docs (DEV)  | docspassword  |

## Тестирование

### DEV-режим (MODE=DEV)

```bash
# Открыть /docs с авторизацией
curl -u docsadmin:docspassword http://localhost:8000/docs

# Без авторизации → 401
curl http://localhost:8000/docs
```

### PROD-режим (MODE=PROD)

```bash
# Любой запрос к /docs → 404
curl http://localhost:8000/docs
```

### API

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty"}' \
  http://localhost:8000/register

curl -u alice:qwerty http://localhost:8000/login
```
