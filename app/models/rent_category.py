from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin


class RentCategoryGroup(BaseModel, TimestampMixin, table=True):
    __tablename__ = "rent_category_groups"

    title: str = Field(max_length=255, nullable=False)
    city: str = Field(max_length=150, nullable=False, index=True)
    display_order: int = Field(default=0, nullable=False)

    categories: List["RentCategory"] = Relationship(
        back_populates="group",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )


class RentCategory(BaseModel, TimestampMixin, table=True):
    __tablename__ = "rent_categories"

    title: str = Field(max_length=255, nullable=False)
    slug: str = Field(max_length=255, nullable=False, index=True)
    url_path: Optional[str] = Field(default=None, max_length=500)
    display_order: int = Field(default=0, nullable=False)
    group_id: UUID = Field(foreign_key="rent_category_groups.id", nullable=False, index=True)

    group: Optional[RentCategoryGroup] = Relationship(back_populates="categories")

