from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Users:
    username: str
    password_hash: int


class TaskType(str, Enum):
    """Класс схемы статуса выполнения задачи"""

    INWORK = "in work"
    COMPLITED = "complited"
    FAILED = "failed"

class Tasks(BaseModel):
    id: int
    title: str
    description: str
    status: TaskType = Field(
        description="Type of task: 'in work', 'complited', 'failed'"
    )
    user_id: int | None = None

    @field_validator("title", "description", "status")
    def to_lower(cls, v):
        return v.lower() if isinstance(v, str) else v


class TaskCreate(BaseModel):
    """Класс модели создания задачи"""

    title: str
    description: str
    status: TaskType = Field(
        description="Type of task: 'in work', 'complited', 'failed'"
    )
    user_id: int | None = None

    @field_validator("title", "description", "status")
    def to_lower(cls, v):
        return v.lower() if isinstance(v, str) else v

    class Meta:
        """Класс таблицы задач"""

        table = "tasks"


class TaskUpdate(BaseModel):
    """Класс модели обновления задачи"""

    title: str | None = None
    description: str | None = None
    status: TaskType = Field(
        description="Type of task: 'in work', 'complited', 'failed'"
    )
    user_id: int | None = None

    @field_validator("title", "description", "status")
    def to_lower(cls, v):
        return v.lower() if isinstance(v, str) else v

class TaskResponse(BaseModel):
    """Класс модели обновления задачи"""
    id:int
    title:str
    description:str
    status:str
    user_id:int

    @field_validator("title", "description", "status")
    def to_lower(cls, v):
        return v.lower() if isinstance(v, str) else v