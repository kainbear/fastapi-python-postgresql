from typing import List, Optional
from pydantic import BaseModel
from models import Users, Tasks
from schemas import TaskCreate, TaskUpdate


class Repository(BaseModel):
    """Класс функций для роутера"""

    @classmethod
    async def create_task(cls, task: TaskCreate) -> Tasks:
        """Функция для создания новой задачи"""
        task_data = task.model_dump()
        return await Tasks.create(**task_data)

    @classmethod
    async def get_task(
        cls,
        status: Optional[str] = None,
    ) -> List[Tasks]:
        """Функция для получения задач по фильтрам"""
        query = Tasks.all()
        if status:
            query = query.filter(status__icontains=status)
        return await query

    @classmethod
    async def update_task(cls, id: int, tasks: TaskUpdate):
        """Функция для обновления задачи"""
        task = await Tasks.get_or_none(id=id)
        if not task:
            return None
        await task.update_from_dict(tasks.model_dump(exclude_none=True))
        await task.save()
        return task

    @classmethod
    async def delete_task(cls, id: int) -> bool:
        """Функция для удаления задачи"""
        task = await Tasks.get_or_none(id=id)
        if task:
            await task.delete()
            return True
        return False
