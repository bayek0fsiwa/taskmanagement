import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import TIMESTAMP
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Column, Field, SQLModel, text


class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in-progress"
    completed = "completed"


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True, nullable=False),
    )
    title: str = Field(nullable=False, index=True, max_length=255)
    description: Optional[str] = Field(default=None, nullable=True)
    status: TaskStatus = Field(
        sa_column=Column(SAEnum(TaskStatus, name="task_status"), nullable=False),
        default=TaskStatus.pending,
    )
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        )
    )


class CreateTaskPayload(SQLModel):
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.pending
