from pydantic import BaseModel
from models import Users, Tasks


class Repository(BaseModel):
    """Класс функций для роутера"""

    @classmethod
    async def get_tasks(cls):
        '''Функция для получения списка всех задач'''
        return await Tasks.all()
