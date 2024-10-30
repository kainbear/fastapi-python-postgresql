from datetime import datetime
from typing import List, Optional
import httpx
from pydantic import BaseModel

class Repository(BaseModel):
    '''Класс функций для роутера'''
    @classmethod
    async def check_user_exists(cls, user_id: int) -> bool:
        '''Функция для проверки существования пользователя через внешний сервис'''
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{USER_SERVICE_URL}/employee/search?id={user_id}")
            if response.status_code == 200:
                user_data = response.json()
                return bool(user_data)
            return False