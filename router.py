from fastapi import APIRouter
from repository import Repository

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
    "/create"
)  # (POST /tasks) с полями: название, описание, статус (например, "в процессе" или "завершена").
async def create_task():
    pass


@task_router.get(
    "/get_tasks"
)  # Получение списка всех задач (GET /tasks) с возможностью фильтрации по статусу.
async def get_list():
    """Функция для получения всех задачи"""
    return await repo.get_tasks()


@task_router.put(
    "/{id}"
)  # Обновление задачи (PUT /tasks/{id}) — редактирование названия, описания и статуса.
async def update_task():
    pass


@task_router.delete("/{id}")
async def delete_task():
    pass
