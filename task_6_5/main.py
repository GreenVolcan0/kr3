import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# ---------- Настройки ----------
SECRET_KEY = "super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ---------- Приложение с rate limiter ----------
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Task 6.5 - JWT + Register + Rate Limit")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

bearer_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------- In-memory БД ----------
fake_users_db: dict[str, str] = {}  # username -> hashed_password

# ---------- Модели ----------

class UserCredentials(BaseModel):
    username: str
    password: str


# ---------- JWT утилиты ----------

def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------- Зависимость: Bearer-токен ----------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    return decode_token(credentials.credentials)


# ---------- Маршруты ----------

@app.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
def register(request: Request, body: UserCredentials):
    """Регистрация: 1 запрос в минуту. Хранит хеш пароля."""
    # Проверяем существование через secrets.compare_digest
    for stored in fake_users_db:
        if secrets.compare_digest(body.username.encode(), stored.encode()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            )

    fake_users_db[body.username] = pwd_context.hash(body.password)
    return {"message": "New user created"}


@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, body: UserCredentials):
    """Логин: 5 запросов в минуту. Возвращает JWT-токен."""
    # Ищем пользователя через secrets.compare_digest
    found_hash: str | None = None
    for stored_username, stored_hash in fake_users_db.items():
        if secrets.compare_digest(body.username.encode(), stored_username.encode()):
            found_hash = stored_hash
            break

    if found_hash is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not pwd_context.verify(body.password, found_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
        )

    token = create_access_token(body.username)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/protected_resource")
def protected_resource(username: str = Depends(get_current_user)):
    """Защищённый ресурс: требует валидный Bearer JWT-токен."""
    return {"message": "Access granted", "user": username}
