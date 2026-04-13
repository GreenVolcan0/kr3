import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum

import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from pydantic import BaseModel

# ---------- Настройки ----------
SECRET_KEY = "super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="Task 7.1 - RBAC")
bearer_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------- Роли и разрешения ----------

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


ROLE_PERMISSIONS: dict[Role, list[str]] = {
    Role.ADMIN:  ["create", "read", "update", "delete"],
    Role.USER:   ["read", "update"],
    Role.GUEST:  ["read"],
}

# ---------- In-memory БД ----------
# username -> {"hashed_password": ..., "role": Role}
fake_users_db: dict[str, dict] = {}

# ---------- Модели ----------

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: Role = Role.USER   # по умолчанию — обычный пользователь


class LoginRequest(BaseModel):
    username: str
    password: str


# ---------- JWT ----------

def create_access_token(username: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": username, "role": role, "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------- Зависимости ----------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    payload = decode_token(credentials.credentials)
    username = payload.get("sub")
    role = payload.get("role")
    if not username or not role:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return {"username": username, "role": role}


def require_permission(permission: str):
    """Фабрика зависимостей: проверяет наличие нужного разрешения у роли."""
    def dependency(current_user: dict = Depends(get_current_user)):
        role = Role(current_user["role"])
        if permission not in ROLE_PERMISSIONS.get(role, []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' does not have '{permission}' permission",
            )
        return current_user
    return dependency


def require_role(*roles: Role):
    """Фабрика зависимостей: проверяет, что роль пользователя входит в список."""
    def dependency(current_user: dict = Depends(get_current_user)):
        if Role(current_user["role"]) not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for role '{current_user['role']}'",
            )
        return current_user
    return dependency


# ---------- Маршруты: Auth ----------

@app.post("/register", status_code=201)
def register(body: RegisterRequest):
    for stored in fake_users_db:
        if secrets.compare_digest(body.username.encode(), stored.encode()):
            raise HTTPException(status_code=409, detail="User already exists")

    fake_users_db[body.username] = {
        "hashed_password": pwd_context.hash(body.password),
        "role": body.role,
    }
    return {"message": f"User '{body.username}' registered with role '{body.role}'"}


@app.post("/login")
def login(body: LoginRequest):
    user_data = None
    for stored_username, data in fake_users_db.items():
        if secrets.compare_digest(body.username.encode(), stored_username.encode()):
            user_data = (stored_username, data)
            break

    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")

    stored_username, data = user_data
    if not pwd_context.verify(body.password, data["hashed_password"]):
        raise HTTPException(status_code=401, detail="Authorization failed")

    token = create_access_token(stored_username, data["role"])
    return {"access_token": token, "token_type": "bearer", "role": data["role"]}


# ---------- Маршруты: Защищённые ресурсы ----------

@app.get("/protected_resource")
def protected_resource(
    current_user: dict = Depends(require_role(Role.ADMIN, Role.USER))
):
    """Доступен только admin и user."""
    return {
        "message": "Access granted",
        "user": current_user["username"],
        "role": current_user["role"],
        "permissions": ROLE_PERMISSIONS[Role(current_user["role"])],
    }


# Только admin
@app.post("/admin/resource")
def admin_create(current_user: dict = Depends(require_permission("create"))):
    return {
        "message": f"Resource created by admin '{current_user['username']}'",
    }


@app.delete("/admin/resource/{resource_id}")
def admin_delete(
    resource_id: int,
    current_user: dict = Depends(require_permission("delete")),
):
    return {
        "message": f"Resource {resource_id} deleted by '{current_user['username']}'",
    }


# User + Admin
@app.get("/user/resource")
def user_read(current_user: dict = Depends(require_permission("read"))):
    return {
        "message": "Here is your data",
        "user": current_user["username"],
    }


@app.put("/user/resource/{resource_id}")
def user_update(
    resource_id: int,
    current_user: dict = Depends(require_permission("update")),
):
    return {
        "message": f"Resource {resource_id} updated by '{current_user['username']}'",
    }


# Guest + all
@app.get("/public/resource")
def guest_read(current_user: dict = Depends(require_permission("read"))):
    return {"message": "Public read-only data"}
