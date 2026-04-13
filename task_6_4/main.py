import random
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

app = FastAPI(title="Task 6.4 - JWT Auth")

# ---------- Настройки JWT ----------
SECRET_KEY = "super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

bearer_scheme = HTTPBearer()

# ---------- Модели ----------

class LoginRequest(BaseModel):
    username: str
    password: str


# ---------- Заглушка аутентификации ----------

def authenticate_user(username: str, password: str) -> bool:
    """
    Заглушка: случайно возвращает True/False.
    В реальном приложении — проверка по БД.
    """
    return random.choice([True, False])


# ---------- JWT утилиты ----------

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


# ---------- Зависимость: проверка Bearer-токена ----------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    payload = decode_token(credentials.credentials)
    username: str | None = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return username


# ---------- Маршруты ----------

@app.post("/login")
def login(request: LoginRequest):
    """Аутентификация: возвращает JWT-токен при успехе."""
    if not authenticate_user(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token({"sub": request.username})
    return {"access_token": token}


@app.get("/protected_resource")
def protected_resource(username: str = Depends(get_current_user)):
    """Защищённый ресурс: требует валидный Bearer JWT-токен."""
    return {"message": "Access granted", "user": username}
