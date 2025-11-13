from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.mood import MoodOut


class DishBase(BaseModel):
    name: str = Field(..., max_length=180)
    description: Optional[str] = None
    restaurant_id: uuid.UUID
    cuisine_id: uuid.UUID
    price: Optional[float] = Field(default=None, ge=0)
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    is_featured: bool = False
    featured_week: Optional[date] = None
    calories: Optional[int] = Field(default=None, ge=0)
    preparation_time_minutes: Optional[int] = Field(default=None, ge=0)


class DishCreate(DishBase):
    mood_ids: Optional[List[uuid.UUID]] = Field(default=None)


class DishUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=180)
    description: Optional[str] = None
    restaurant_id: Optional[uuid.UUID] = None
    cuisine_id: Optional[uuid.UUID] = None
    price: Optional[float] = Field(default=None, ge=0)
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    is_featured: Optional[bool] = None
    featured_week: Optional[date] = None
    calories: Optional[int] = Field(default=None, ge=0)
    preparation_time_minutes: Optional[int] = Field(default=None, ge=0)
    mood_ids: Optional[List[uuid.UUID]] = Field(default=None)


class DishOut(DishBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    moods: List[MoodOut] = []

    class Config:
        from_attributes = True


class DishFilterParams(BaseModel):
    cuisine_id: Optional[uuid.UUID] = None
    restaurant_id: Optional[uuid.UUID] = None
    mood_id: Optional[uuid.UUID] = None
    min_rating: Optional[float] = Field(default=None, ge=0, le=5)
    max_price: Optional[float] = Field(default=None, ge=0)
    is_featured: Optional[bool] = None
