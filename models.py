from tortoise import fields
from tortoise.models import Model


class Users(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(64, unique=True)
    password_hash = fields.CharField(128)

    class Meta:
        """Класс таблицы проекта"""

        table = "users"


class Tasks(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField(null=True)
    title = fields.CharField(250, null=True)
    description = fields.CharField(250, null=True)
    status = fields.CharField(max_length=20)  # 'at work', 'complited', 'failed'

    class Meta:
        """Класс таблицы задач"""

        table = "tasks"
