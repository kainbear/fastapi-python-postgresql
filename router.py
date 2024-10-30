from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from repository import Repository
from schemas import TaskCreate, TaskResponse, TaskUpdate, Tasks

user_router = APIRouter(prefix="/auth", tags=["Auth"])

repo = Repository()


"""
Добавьте аутентификацию пользователей по Bearer-токену:
Используйте access и refresh токены для подтверждения операций с задачами.
"""


@user_router.post(
    "/register"
)  # Регистрация пользователя (POST /auth/register): принимает username и password
async def register_user():
    pass


@user_router.post(
    "/login"
)  # Вход в систему (POST /auth/login): возвращает access и refresh токены.
async def login_user():
    pass


@user_router.post(
    "/refresh"
)  # Обновление access токена (POST /auth/refresh) с использованием refresh токена.
async def update_access_token():
    pass


@user_router.delete("/{id}")
async def delete_user():
    pass


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

