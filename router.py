from fastapi import APIRouter, HTTPException, Query, Depends
from repository import Repository

repo = Repository()

@task_router.get("/read_all")
async def read_all_tasks():
    '''Функция для получения всех задачи'''
    return await repo.get_all_tasks()

@task_router.post("/add")
async def create_task(task: Annotated[TaskCreate, Depends()]):
    '''Функция для создания задачи'''
    try:
        created_task = await repo.create_task(task)
        return created_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))