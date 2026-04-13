from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI(title="Task 6.1 - Basic Auth")

security = HTTPBasic()

# Простая "база данных" пользователей
FAKE_USERS = {
    "admin": "secret123",
    "user1": "password1",
}


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Зависимость: проверяет логин и пароль через HTTP Basic Auth."""
    stored_password = FAKE_USERS.get(credentials.username)

    # Используем secrets.compare_digest для защиты от тайминг-атак
    username_correct = stored_password is not None
    password_correct = username_correct and secrets.compare_digest(
        credentials.password.encode("utf-8"),
        stored_password.encode("utf-8"),
    )

    if not (username_correct and password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


@app.get("/login")
def login(username: str = Depends(verify_credentials)):
    """Защищённый эндпоинт: аутентификация через HTTP Basic Auth."""
    return {"message": "You got my secret, welcome"}
