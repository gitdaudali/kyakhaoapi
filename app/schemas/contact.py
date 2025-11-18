"""Contact schemas for request and response models."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ContactCreate(BaseModel):
    """Schema for creating a contact message."""

    name: str = Field(..., max_length=255, description="Contact name")
    email: EmailStr = Field(..., description="Contact email address")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone number (optional)")
    message: str = Field(..., description="Contact message")


class ContactOut(BaseModel):
    """Schema for contact message response."""

    id: UUID
    name: str
    email: str
    phone: Optional[str]
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class ContactAdminOut(BaseModel):
    """Schema for admin contact message response."""

    id: UUID
    name: str
    email: str
    phone: Optional[str]
    message: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

