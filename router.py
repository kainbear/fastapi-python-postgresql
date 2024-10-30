from datetime import datetime, timedelta
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from models import Users
from repository import Repository
from schemas import TaskCreate, TaskResponse, TaskUpdate, Tasks, User
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from psycopg2 import IntegrityError

user_router = APIRouter(prefix="/auth", tags=["Auth"])

repo = Repository()

SECRET_KEY = "testcase"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    '''Функция для верификации пароля'''
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password_hash):
    '''Функция для получения хешированного пароля'''
    return pwd_context.hash(password_hash)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Функция для создания доступа токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@user_router.post("/register")
async def register_user(user: Annotated[User, Depends()]):
    """Регистрация пользователя"""
    hashed_password = pwd_context.hash(user.password_hash)
    user_data = user.model_dump()
    user_data["password_hash"] = hashed_password

    try:
        new_employee = await Users.create(**user_data)
        access_token = create_access_token(data={"sub": new_employee.username})
        return {"access_token": access_token, "token_type": "bearer"}
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с username уже существует",
        )


@user_router.post(
    "/login"
)  # Вход в систему (POST /auth/login): возвращает access и refresh токены.
async def login(form_data: OAuth2AuthorizationCodeBearer = Depends()):
    '''Логин пользователя и получение токена'''
    user = await Users.get_or_none(username=form_data.username)
    if not user or not pwd_context.verify(form_data.password_hash, user.password_hash):
        raise HTTPException(status_code=400, detail="Неправильный логин или пароль")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.post(
    "/refresh"
)  # Обновление access токена (POST /auth/refresh) с использованием refresh токена.
async def update_access_token():
    pass


@user_router.delete("/{id}")
async def delete_user(id: int):
    """Функция для удаления пользователя"""
    success = await repo.delete_user(id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted"}


task_router = APIRouter(prefix="/tasks", tags=["Tasks"])


@task_router.post(
    "/create", response_model=TaskResponse
)  # (POST /tasks) с полями: название, описание, статус (например, "в процессе" или "завершена").
async def create_task(task: Annotated[TaskCreate, Depends()]):
    try:
        created_task = await repo.create_task(task)
        return created_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@task_router.get("/search", response_model=List[Tasks])
async def search_task(
    status: Optional[str] = Query(
        default=None, description="Type of task: 'in work', 'complited', 'failed'"
    ),
):
    """Функция для получения всех задач и фильтра"""
    tasks = await repo.get_task(
        status=status,
    )
    if not tasks:
        raise HTTPException(status_code=404, detail="Tasks not found")
    return tasks


@task_router.put(
    "/{id}", response_model=TaskResponse
)  # Обновление задачи (PUT /tasks/{id}) — редактирование названия, описания и статуса.
async def update_task(id: int, task: Annotated[TaskUpdate, Depends()]):
    """Функция для обновления задачи"""
    try:
        updated_task = await repo.update_task(id, task)
        if updated_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@task_router.delete("/{id}")
async def delete_task(id: int):
    """Функция для удаления задачи"""
    success = await repo.delete_task(id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted"}
