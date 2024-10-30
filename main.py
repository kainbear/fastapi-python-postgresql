from fastapi import FastAPI
from router import user_router, task_router
from tortoise.contrib.fastapi import register_tortoise
import aerich_config

app = FastAPI(
    title="Веб-приложение TestCase4",
    version="1.0.0",
    description="Сервис для регистрации и создания пользователей, так же для создания и хранения задач.",
)

app.include_router(user_router)
app.include_router(task_router)

register_tortoise(
    app,
    db_url=aerich_config.DATABASE_URL,
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
