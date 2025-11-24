from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.dish import DishOut


class MenuCategoryOut(BaseModel):
    """Menu category information."""

    name: str = Field(..., description="Category name (e.g., 'appetizers', 'mains_teppanyaki')")
    display_name: str = Field(..., description="Human-readable category name")
    dish_count: int = Field(..., description="Number of dishes in this category")
    description: Optional[str] = Field(None, description="Category description")

    class Config:
        from_attributes = False


class MenuCategoryWithDishesOut(MenuCategoryOut):
    """Menu category with its dishes."""

    dishes: List[DishOut] = Field(default_factory=list, description="Dishes in this category")

    class Config:
        from_attributes = False


class MenuOut(BaseModel):
    """Complete menu structure with all categories."""

    categories: List[MenuCategoryWithDishesOut] = Field(
        default_factory=list, description="All menu categories with their dishes"
    )
    total_dishes: int = Field(..., description="Total number of dishes across all categories")
    total_categories: int = Field(..., description="Total number of categories")

    class Config:
        from_attributes = False


class MenuSummaryOut(BaseModel):
    """Menu summary with category overview."""

    categories: List[MenuCategoryOut] = Field(
        default_factory=list, description="All menu categories with dish counts"
    )
    total_dishes: int = Field(..., description="Total number of dishes")
    total_categories: int = Field(..., description="Total number of categories")

    class Config:
        from_attributes = False


class MenuStructureOut(BaseModel):
    """Menu structure/hierarchy information."""

    categories: List[MenuCategoryOut] = Field(
        default_factory=list, description="Menu categories with metadata"
    )
    total_dishes: int = Field(..., description="Total dishes in menu")
    total_categories: int = Field(..., description="Total categories")

    class Config:
        from_attributes = False

