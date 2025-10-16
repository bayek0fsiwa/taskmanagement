from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import select

from configs.db import SessionDep
from taskmanagement.models import CreateTaskPayload, Task, TaskStatus
from utils.loger import LoggerSetup

_logger_setup: Optional[LoggerSetup] = None


def get_logger():
    global _logger_setup
    if _logger_setup is None:
        _logger_setup = LoggerSetup(logger_name=__name__)
    return _logger_setup.logger


logger = get_logger()


async def create_task(session: SessionDep, payload: CreateTaskPayload):
    validated = CreateTaskPayload.model_validate(payload)
    task = Task(**validated.model_dump())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    logger.info(msg=f"Task is create with id {task.id}")
    return task


async def get_all_tasks(session: SessionDep, page: int = 1, size: int = 20):
    if page < 1:
        page = 1
    if size < 1:
        size = 20
    offset = (page - 1) * size
    result = await session.exec(select(Task).limit(size).offset(offset))
    tasks = result.all()
    return tasks


async def update_task(
    session: SessionDep,
    task_id: str,
    title: Optional[str] = None,
    status: Optional[TaskStatus] = None,
):
    result = await session.exec(select(Task).where(Task.id == task_id))
    task = result.one_or_none()
    if not task:
        raise HTTPException(detail="Task not found")

    if title is not None:
        task.title = title
    if status is not None:
        task.status = status if isinstance(status, TaskStatus) else TaskStatus(status)

    session.add(task)
    await session.commit()
    await session.refresh(task)
    logger.info(msg=f"Task is update with id {task.id}")
    return task


async def delete_task(session: SessionDep, task_id: str):
    result = await session.exec(select(Task).where(Task.id == task_id))
    task = result.one_or_none()
    if not task:
        raise HTTPException(
            detail=f"Task not found: {task_id}", status_code=status.HTTP_400_BAD_REQUEST
        )

    await session.delete(task)
    await session.commit()
    logger.info(msg=f"Task is deleted with id {task.id}")
