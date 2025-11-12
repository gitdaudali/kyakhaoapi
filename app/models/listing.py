from enum import Enum
from typing import List, Optional
from uuid import UUID

from sqlalchemy import String
from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin


class ListingSection(str, Enum):
    POPULAR = "popular"
    DEALS = "deals"
    PETS = "pets"


class Listing(BaseModel, TimestampMixin, table=True):
    __tablename__ = "listings"

    title: str = Field(max_length=255, nullable=False)
    city: str = Field(max_length=150, nullable=False, index=True)
    price: int = Field(nullable=False, ge=0)
    bedrooms: Optional[int] = Field(default=None, ge=0)
    bathrooms: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = Field(default=None, max_length=500)
    is_pet_friendly: bool = Field(default=False, nullable=False, index=True)

    section_mappings: List["ListingSectionMap"] = Relationship(
        back_populates="listing",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )


class ListingSectionMap(BaseModel, TimestampMixin, table=True):
    __tablename__ = "listing_section_map"

    listing_id: UUID = Field(
        foreign_key="listings.id",
        nullable=False,
        index=True,
    )
    section_name: ListingSection = Field(
        sa_type=String(length=50),
        nullable=False,
        index=True,
    )

    listing: Optional["Listing"] = Relationship(back_populates="section_mappings")

