"""Favorite schemas for request and response models."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FavoriteCreate(BaseModel):
    """Schema for creating a new favorite."""

    item_id: UUID = Field(..., description="ID of the item to favorite (dish or restaurant)")
    item_type: str = Field(default="dish", description="Type of item: 'dish' or 'restaurant'")


class FavoriteOut(BaseModel):
    """Schema for favorite response."""

    id: UUID
    item_id: UUID
    item_type: str
    added_at: datetime

    class Config:
        from_attributes = True


class FavoriteListItem(BaseModel):
    """Schema for favorite list item with item details."""

    item_id: UUID
    name: str
    added_at: datetime

    class Config:
        from_attributes = True


class FavoriteAdminOut(BaseModel):
    """Schema for admin favorite view."""

    user_id: UUID
    item_id: UUID
    item_name: str
    item_type: str
    added_at: datetime

    class Config:
        from_attributes = True

