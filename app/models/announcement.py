from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin


class AnnouncementStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Announcement(BaseModel, TimestampMixin, table=True):
    """Model for announcements that can be displayed to users"""

    __tablename__ = "announcements"

    title: str = Field(sa_type=String(255), nullable=False, index=True)
    description: str = Field(sa_type=Text, nullable=False)
    status: AnnouncementStatus = Field(
        sa_type=String(20), default=AnnouncementStatus.DRAFT, index=True
    )
    author_id: UUID = Field(
        foreign_key="users.id", nullable=False, index=True
    )
    scheduled_date_time: Optional[datetime] = Field(
        sa_type=DateTime(timezone=True), default=None, index=True
    )
    is_active: bool = Field(default=True, index=True)

    # Relationships
    author: Optional["User"] = Relationship()

    class Config:
        from_attributes = True

