from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Query, status

from configs.db import SessionDep
from taskmanagement.models import CreateTaskPayload, TaskStatus

from .services import create_task, delete_task, get_all_tasks, update_task

router = APIRouter(prefix="/task", tags=["Tasks route"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task_route(session: SessionDep, payload: CreateTaskPayload):
    return await create_task(session, payload)


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_tasks_route(
    session: SessionDep, page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)
):
    return await get_all_tasks(session, page, size)


@router.patch(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
)
async def update_task_route(
    session: SessionDep,
    task_id: str = Path(..., description="UUID of task to update"),
    title: Optional[str] = Query(None, min_length=1, max_length=255),
    status: Optional[TaskStatus] = Query(None),
):
    try:
        updated = await update_task(session, task_id, title=title, status=status)
        return updated
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Task not found {e}")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_route(
    session: SessionDep,
    task_id: str = Path(..., description="UUID of the task to delete"),
):
    try:
        await delete_task(session, task_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Task not found {e}")
    return None
