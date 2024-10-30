from datetime import datetime, timedelta
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from models import Users
from repository import Repository
from schemas import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    Tasks,
    TokenRefreshRequest,
    User,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from psycopg2 import IntegrityError
from redis import Redis

user_router = APIRouter(prefix="/auth", tags=["Auth"])

repo = Repository()

redis_client = Redis(host="redis", port=6379, db=0)

SECRET_KEY = "testcase"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Проверка access токена и извлечение пользователя."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )


def verify_password(plain_password, hashed_password):
    """Функция для верификации пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password_hash):
    """Функция для получения хешированного пароля"""
    return pwd_context.hash(password_hash)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Создание access токена"""
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    """Создание refresh токена"""
    expire = datetime.now() + timedelta(days=7)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@user_router.post("/register")
async def register_user(user: Annotated[User, Depends()]):
    """Регистрация пользователя"""
    hashed_password = get_password_hash(user.password_hash)
    user_data = user.model_dump()
    user_data["password_hash"] = hashed_password

    try:
        new_employee = await Users.create(**user_data)
        access_token = create_access_token(data={"sub": new_employee.username})
        refresh_token = create_refresh_token(data={"sub": new_employee.username})
        redis_client.set(new_employee.username, refresh_token, ex=604800)

        return {
            "Successful Registration": {
                "username": new_employee.username,
                "user_id": new_employee.id,
            }
        }
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="Пользователь с username уже существует"
        )


@user_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Логин пользователя и получение токена"""
    user = await Users.get_or_none(username=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Неправильный логин или пароль")

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    redis_client.set(user.username, refresh_token, ex=604800)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@user_router.post("/refresh")
async def refresh_access_token(token_data: TokenRefreshRequest = Depends()):
    """Обновление access токена"""
    refresh_token = redis_client.get(token_data.username)
    if not refresh_token or refresh_token.decode() != token_data.refresh_token:
        raise HTTPException(status_code=403, detail="Invalid refresh token")

    data = jwt.decode(refresh_token.decode(), SECRET_KEY, algorithms=[ALGORITHM])
    new_access_token = create_access_token(data={"sub": data["sub"]})

    return {"New access_token": new_access_token}


task_router = APIRouter(prefix="/tasks", tags=["Tasks"])


@task_router.post(
    "/create", response_model=TaskResponse, dependencies=[Depends(get_current_user)]
)
async def create_task(
    task: Annotated[TaskCreate, Depends()],
):
    """Создание задачи."""
    try:
        created_task = await repo.create_task(task)
        return created_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@task_router.get(
    "/search", response_model=List[Tasks], dependencies=[Depends(get_current_user)]
)
async def search_task(
    status: Optional[str] = Query(
        default=None, description="Type of task: 'in work', 'complited', 'failed'"
    ),
):
    """Получение всех задач и фильтра."""
    tasks = await repo.get_task(
        status=status,
    )
    if not tasks:
        raise HTTPException(status_code=404, detail="Tasks not found")
    return tasks


@task_router.put(
    "/{id}", response_model=TaskResponse, dependencies=[Depends(get_current_user)]
)
async def update_task(
    id: int,
    task: Annotated[TaskUpdate, Depends()],
):
    """Обновление задачи."""
    try:
        updated_task = await repo.update_task(id, task)
        if updated_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@task_router.delete("/{id}", dependencies=[Depends(get_current_user)])
async def delete_task(id: int):
    """Удаление задачи."""
    success = await repo.delete_task(id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted"}
