"""Notification model."""
import uuid
from typing import Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from app.models.base import BaseModel, TimestampMixin


class Notification(BaseModel, TimestampMixin, table=True):
    """Model for user notifications."""

    __tablename__ = "notifications"

    user_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="users.id", nullable=False, index=True
    )
    title: str = Field(sa_type=String(255), nullable=False, max_length=255)
    message: str = Field(sa_type=Text, nullable=False)
    is_read: bool = Field(default=False, sa_type=Boolean, nullable=False, index=True)
    notification_type: Optional[str] = Field(
        sa_type=String(50), nullable=True, default=None, max_length=50, index=True,
        description="Type of notification: order, promotion, system, etc."
    )
    related_id: Optional[uuid.UUID] = Field(
        sa_type=UUID(as_uuid=True), nullable=True, default=None,
        description="ID of related entity (e.g., order_id, promotion_id)"
    )

