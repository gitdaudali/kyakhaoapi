"""Notification schemas for request and response models."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationOut(BaseModel):
    """Schema for notification response."""

    id: UUID
    user_id: UUID
    title: str
    message: str
    is_read: bool
    notification_type: Optional[str]
    related_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationListItem(BaseModel):
    """Schema for notification list item (simplified)."""

    id: UUID
    title: str
    message: str
    is_read: bool
    notification_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationSend(BaseModel):
    """Schema for sending a notification (admin)."""

    title: str = Field(..., min_length=1, max_length=255, description="Notification title")
    message: str = Field(..., min_length=1, description="Notification message")
    user_id: Optional[UUID] = Field(
        None, description="Send to specific user (if null, send to all users)"
    )
    broadcast: bool = Field(
        False, description="If true, send to all users (ignores user_id)"
    )
    notification_type: Optional[str] = Field(
        None, max_length=50, description="Type of notification: order, promotion, system, etc."
    )
    related_id: Optional[UUID] = Field(
        None, description="ID of related entity (e.g., order_id, promotion_id)"
    )


class NotificationUnreadCount(BaseModel):
    """Schema for unread notification count."""

    unread_count: int


class NotificationMarkRead(BaseModel):
    """Schema for marking notification as read."""

    is_read: bool = Field(True, description="Mark as read (always true)")


class NotificationAdminOut(BaseModel):
    """Schema for admin notification response."""

    id: UUID
    user_id: UUID
    title: str
    message: str
    is_read: bool
    notification_type: Optional[str]
    related_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

