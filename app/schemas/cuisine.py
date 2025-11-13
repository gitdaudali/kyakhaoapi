from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CuisineBase(BaseModel):
    name: str = Field(..., max_length=120)
    description: Optional[str] = Field(default=None)


class CuisineCreate(CuisineBase):
    pass


class CuisineUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=120)
    description: Optional[str] = Field(default=None)


class CuisineOut(CuisineBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
