from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Users:
    username: str
    password_hash: int


class TaskType(str, Enum):
    """Класс схемы статуса выполнения задачи"""

    ATWORK = "in work"
    COMPLITED = "complited"
    FAILED = "failed"


class Tasks:
    title: str
    description: str
    status: TaskType = Field(
        description="Type of task: 'in work', 'complited', 'failed'"
    )
    user_id: int | None = None

    @field_validator("title", "description", "status")
    def to_lower(cls, v):
        return v.lower() if isinstance(v, str) else v


class TaskUpdate(BaseModel):
    """Класс модели обновления задачи"""

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
    due_date: datetime
    actual_due_date: datetime | None = None
    hours_spent: int = 0
    user_id: int | None = None
    project_id: int
    type: TaskType = Field(description="Type of task: 'at work', 'complited', 'failed'")

    @field_validator("title", "description")
    def to_lower(cls, v):
        return v.lower() if isinstance(v, str) else v

    class Meta:
        """Класс таблицы задач"""

        table = "tasks"
