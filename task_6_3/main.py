import secrets
import os

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# ---------- Конфигурация окружения ----------
MODE = os.getenv("MODE", "DEV").upper()
if MODE not in ("DEV", "PROD"):
    raise ValueError(f"Invalid MODE value: '{MODE}'. Allowed: DEV, PROD")

DOCS_USER = os.getenv("DOCS_USER", "docsadmin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "docspassword")

# Отключаем стандартную документацию FastAPI — будем управлять вручную
app = FastAPI(
    title="Task 6.3 - Docs Access Control",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

security = HTTPBasic()
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

# ---------- Зависимость: аутентификация пользователей API ----------

def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInDB:
    found_user: UserInDB | None = None
    for stored_username, user_obj in fake_users_db.items():
        if secrets.compare_digest(
            credentials.username.encode(), stored_username.encode()
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


# ---------- Зависимость: аутентификация для документации (DEV) ----------

def verify_docs_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_user = secrets.compare_digest(
        credentials.username.encode(), DOCS_USER.encode()
    )
    correct_pass = secrets.compare_digest(
        credentials.password.encode(), DOCS_PASSWORD.encode()
    )
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid docs credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


# ---------- Эндпоинты документации ----------

if MODE == "DEV":
    @app.get("/docs", include_in_schema=False)
    def custom_docs(_: None = Depends(verify_docs_credentials)):
        return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")

    @app.get("/openapi.json", include_in_schema=False)
    def custom_openapi(_: None = Depends(verify_docs_credentials)):
        return JSONResponse(
            get_openapi(title=app.title, version="1.0.0", routes=app.routes)
        )
    # /redoc — скрыт (не регистрируем маршрут)

elif MODE == "PROD":
    @app.get("/docs", include_in_schema=False)
    def docs_hidden():
        raise HTTPException(status_code=404)

    @app.get("/openapi.json", include_in_schema=False)
    def openapi_hidden():
        raise HTTPException(status_code=404)

    @app.get("/redoc", include_in_schema=False)
    def redoc_hidden():
        raise HTTPException(status_code=404)


# ---------- Маршруты API ----------

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=409, detail="User already exists")
    hashed = pwd_context.hash(user.password)
    fake_users_db[user.username] = UserInDB(
        username=user.username, hashed_password=hashed
    )
    return {"message": f"User '{user.username}' registered successfully"}


@app.get("/login")
def login(current_user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {current_user.username}!"}
