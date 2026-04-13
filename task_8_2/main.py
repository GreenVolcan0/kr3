from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from database import create_tables, get_db_connection

create_tables()

app = FastAPI(title="Task 8.2 - Todo CRUD")


# ---------- Модели ----------

class TodoCreate(BaseModel):
    """Тело запроса для создания Todo."""
    title: str
    description: str


class TodoUpdate(BaseModel):
    """Тело запроса для обновления Todo."""
    title: str
    description: str
    completed: bool


class TodoResponse(BaseModel):
    """Ответ с данными Todo."""
    id: int
    title: str
    description: str
    completed: bool


# ---------- Вспомогательная функция ----------

def row_to_todo(row) -> TodoResponse:
    return TodoResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"]),
    )


# ---------- Маршруты ----------

@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate):
    """Создаёт новый элемент Todo."""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO todos (title, description, completed) VALUES (?, ?, 0)",
            (todo.title, todo.description),
        )
        conn.commit()
        new_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (new_id,)).fetchone()
    finally:
        conn.close()

    return row_to_todo(row)


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    """Возвращает Todo по id."""
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id={todo_id} not found",
        )
    return row_to_todo(row)


@app.get("/todos", response_model=list[TodoResponse])
def list_todos():
    """Возвращает список всех Todo."""
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT * FROM todos").fetchall()
    finally:
        conn.close()
    return [row_to_todo(r) for r in rows]


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate):
    """Обновляет Todo по id."""
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id={todo_id} not found",
            )
        conn.execute(
            "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
            (todo.title, todo.description, int(todo.completed), todo_id),
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    finally:
        conn.close()

    return row_to_todo(updated)


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    """Удаляет Todo по id."""
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id={todo_id} not found",
            )
        conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
    finally:
        conn.close()

    return {"message": f"Todo with id={todo_id} deleted successfully"}
