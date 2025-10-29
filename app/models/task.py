from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class Task(BaseModel, TimestampMixin, table=True):
    """Model for managing tasks"""

    __tablename__ = "tasks"

    task_title: str = Field(sa_type=String(255), nullable=False, index=True)
    description: Optional[str] = Field(sa_type=Text, default=None)
    assigned_to: UUID = Field(
        foreign_key="users.id", nullable=False, index=True
    )
    deadline: Optional[datetime] = Field(
        sa_type=DateTime(timezone=True), default=None, index=True
    )
    priority: TaskPriority = Field(
        sa_type=String(20), default=TaskPriority.MEDIUM, index=True
    )
    status: TaskStatus = Field(
        sa_type=String(20), default=TaskStatus.PENDING, index=True
    )
    project: Optional[str] = Field(sa_type=String(255), default=None, index=True)
    is_active: bool = Field(default=True, index=True)

    # Relationships
    assignee: Optional["User"] = Relationship()

    class Config:
        from_attributes = True

