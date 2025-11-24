"""Favorites schemas for request and response models."""
from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.schemas.dish import DishOut


class FavoriteCreate(BaseModel):
    """Schema for creating a favorite."""

    dish_id: UUID = Field(..., description="ID of the dish to favorite")


class FavoriteResponse(BaseModel):
    """Schema for favorite response."""

    id: UUID
    user_id: UUID
    dish_id: UUID
    dish: DishOut
    created_at: datetime

    @field_serializer("id", "user_id", "dish_id")
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)

    @field_serializer("created_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()

    class Config:
        from_attributes = True


class FavoriteListResponse(BaseModel):
    """Schema for favorite list response."""

    favorites: List[FavoriteResponse]
    total: int

    class Config:
        from_attributes = True


