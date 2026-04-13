import secrets

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI(title="Task 6.2 - Hashed Passwords")

security = HTTPBasic()

# ---------- PassLib ----------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------- Модели ----------

class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


# ---------- In-memory БД ----------
fake_users_db: dict[str, UserInDB] = {}


# ---------- Зависимость аутентификации ----------

def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInDB:
    """Проверяет учётные данные; возвращает объект пользователя или 401."""
    # Ищем пользователя в БД через secrets.compare_digest (защита от тайм-атак)
    found_user: UserInDB | None = None
    for stored_username, user_obj in fake_users_db.items():
        if secrets.compare_digest(
            credentials.username.encode("utf-8"),
            stored_username.encode("utf-8"),
        ):
            found_user = user_obj
            break

    if found_user is None or not pwd_context.verify(
        credentials.password, found_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return found_user


# ---------- Маршруты ----------

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: User):
    """Регистрирует нового пользователя с хешированным паролем."""
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    hashed = pwd_context.hash(user.password)
    fake_users_db[user.username] = UserInDB(
        username=user.username,
        hashed_password=hashed,
    )
    return {"message": f"User '{user.username}' registered successfully"}


@app.get("/login")
def login(current_user: UserInDB = Depends(auth_user)):
    """Аутентифицирует пользователя через HTTP Basic Auth."""
    return {"message": f"Welcome, {current_user.username}!"}
