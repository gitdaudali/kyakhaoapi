from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ReservationBase(BaseModel):
    restaurant_id: uuid.UUID
    customer_name: str = Field(..., max_length=120)
    customer_email: EmailStr
    reservation_time: datetime
    party_size: int = Field(..., ge=1, le=20)
    special_requests: Optional[str] = None


class ReservationCreate(ReservationBase):
    pass


class ReservationOut(ReservationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
