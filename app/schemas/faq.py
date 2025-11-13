"""FAQ schemas for request and response models."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer


class FAQBase(BaseModel):
    """Base FAQ schema with common fields."""

    question: str = Field(..., min_length=1, max_length=1000)
    answer: str = Field(..., min_length=1)
    category: Optional[str] = Field(None, max_length=100)
    order: int = Field(default=0, ge=0)


class FAQCreate(FAQBase):
    """Schema for creating a new FAQ."""

    is_published: bool = Field(default=False)


class FAQUpdate(BaseModel):
    """Schema for updating an FAQ."""

    question: Optional[str] = Field(None, min_length=1, max_length=1000)
    answer: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=100)
    is_published: Optional[bool] = None
    order: Optional[int] = Field(None, ge=0)


class FAQResponse(FAQBase):
    """Schema for FAQ response."""

    id: UUID
    is_published: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)

    class Config:
        from_attributes = True


class FAQListResponse(BaseModel):
    """Schema for FAQ list response."""

    faqs: list[FAQResponse]
    total: int

    class Config:
        from_attributes = True

