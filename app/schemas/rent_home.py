from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RentInquiryRequest(BaseModel):
    listing_id: UUID
    message: str = Field(..., min_length=5, max_length=2000)
    preferred_move_in_date: Optional[date] = None
    contact_name: Optional[str] = Field(default=None, max_length=255)


class RentInquiryResponse(BaseModel):
    inquiry_id: UUID
    listing_id: UUID
    message: str
    preferred_move_in_date: Optional[date]
    contact_name: Optional[str]



