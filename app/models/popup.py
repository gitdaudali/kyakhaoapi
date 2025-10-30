from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Text, Date, DateTime, ForeignKey
from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin


class PopupStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class PopupPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Popup(BaseModel, TimestampMixin, table=True):
    """Model for pop-up notifications/messages"""

    __tablename__ = "popups"

    popup_name: str = Field(sa_type=String(255), nullable=False, index=True)
    description: Optional[str] = Field(sa_type=Text, default=None)
    status: PopupStatus = Field(
        sa_type=String(20), default=PopupStatus.DRAFT, index=True
    )
    priority: PopupPriority = Field(
        sa_type=String(20), default=PopupPriority.MEDIUM, index=True
    )
    assignee_id: UUID = Field(
        foreign_key="users.id", nullable=False, index=True
    )
    due_date: Optional[date] = Field(sa_type=Date, default=None, index=True)
    project: Optional[str] = Field(sa_type=String(255), default=None, index=True)
    is_active: bool = Field(default=True, index=True)

    # Relationships
    assignee: Optional["User"] = Relationship()

    class Config:
        from_attributes = True

