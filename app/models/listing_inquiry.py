from typing import Optional
from uuid import UUID

from sqlmodel import Field

from app.models.base import BaseModel, TimestampMixin


class ListingInquiry(BaseModel, TimestampMixin, table=True):
    __tablename__ = "listing_inquiries"

    listing_id: UUID = Field(foreign_key="listings.id", nullable=False, index=True)
    message: str = Field(nullable=False, max_length=2000)
    preferred_move_in_date: Optional[str] = Field(default=None, max_length=32)
    contact_name: Optional[str] = Field(default=None, max_length=255)



