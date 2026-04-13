# Task 8.2 — Todo CRUD (SQLite)

## Установка и запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Таблица `todos` создаётся автоматически при старте.

## Тестирование

### Создать Todo (POST)
```bash
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread"}'
```

### Получить один Todo (GET)
```bash
curl http://localhost:8000/todos/1
```

### Получить все Todo (GET)
```bash
curl http://localhost:8000/todos
```

### Обновить Todo (PUT)
```bash
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread, butter","completed":true}'
```

### Удалить Todo (DELETE)
```bash
curl -X DELETE http://localhost:8000/todos/1
```

### Несуществующий Todo → 404
```bash
curl http://localhost:8000/todos/9999
```
