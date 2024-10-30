from fastapi import FastAPI
from router import user_router, task_router

app = FastAPI(
        title="TestCase",
        version="1.0.0",
        description="Сервис для регистрации и создания пользователей, так же для создания и хранения задач.",
    )

app.include_router(user_router)
app.include_router(task_router)

