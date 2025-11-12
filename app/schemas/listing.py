from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class ListingCard(BaseModel):
    id: UUID
    title: str
    price: int
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    image_url: Optional[str]
    city: str


class HomeSectionResponse(BaseModel):
    section_title: str
    section_key: str
    listings: List[ListingCard]


class HomeResponse(BaseModel):
    city: str
    sections: List[HomeSectionResponse]

