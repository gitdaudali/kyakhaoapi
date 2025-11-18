"""Review schemas for request and response models."""
from datetime import date, datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# Placeholder values that should be treated as None
PLACEHOLDERS = {"", "string", "null", "none", "n/a", "-"}


def clean_placeholder(value: str | None) -> str | None:
    """Convert placeholder values to None."""
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip().lower()
        return None if cleaned in PLACEHOLDERS else value.strip()
    return value


class ReviewCreate(BaseModel):
    """Schema for creating a new review."""

    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    title: str | None = Field(None, max_length=120, description="Review title (max 120 characters)")
    comment: str = Field(..., max_length=1000, description="Review comment/body (max 1000 characters, required)")
    visit_date: date | None = Field(None, description="Date when the user visited/ordered (YYYY-MM-DD, e.g., October 2025)")
    spice_level: str | None = Field(
        None, 
        description="Spice level: Mild, Medium, Spicy, Extra Spicy"
    )
    delivery_time: str | None = Field(
        None,
        description="Delivery time: Early, On-Time, Late"
    )
    companion_type: str | None = Field(
        None,
        description="Who they went with: Solo, Couples, Family, Friends, Business"
    )
    photos: List[str] | None = Field(
        None,
        description="List of photo URLs (optional)"
    )

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        """Validate rating is between 1 and 5."""
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v

    @field_validator("spice_level")
    @classmethod
    def validate_spice_level(cls, v: str | None) -> str | None:
        """Validate spice level if provided."""
        if v is not None:
            valid_levels = ["Mild", "Medium", "Spicy", "Extra Spicy"]
            if v not in valid_levels:
                raise ValueError(f"Spice level must be one of: {', '.join(valid_levels)}")
        return v

    @field_validator("delivery_time")
    @classmethod
    def validate_delivery_time(cls, v: str | None) -> str | None:
        """Validate delivery time if provided."""
        if v is not None:
            valid_times = ["Early", "On-Time", "Late"]
            if v not in valid_times:
                raise ValueError(f"Delivery time must be one of: {', '.join(valid_times)}")
        return v

    @field_validator("companion_type")
    @classmethod
    def validate_companion_type(cls, v: str | None) -> str | None:
        """Validate companion type if provided."""
        if v is not None:
            valid_types = ["Solo", "Couples", "Family", "Friends", "Business"]
            if v not in valid_types:
                raise ValueError(f"Companion type must be one of: {', '.join(valid_types)}")
        return v


class ReviewUpdate(BaseModel):
    """Schema for updating a review."""

    rating: int | None = Field(None, ge=1, le=5, description="Rating from 1 to 5")
    title: str | None = Field(None, max_length=120, description="Review title (max 120 characters)")
    comment: str | None = Field(None, max_length=1000, description="Review comment/body (max 1000 characters, optional)")
    visit_date: date | None = Field(None, description="Date when the user visited/ordered (YYYY-MM-DD)")
    spice_level: str | None = Field(
        None, 
        description="Spice level: Mild, Medium, Spicy, Extra Spicy"
    )
    delivery_time: str | None = Field(
        None,
        description="Delivery time: Early, On-Time, Late"
    )
    companion_type: str | None = Field(
        None,
        description="Who they went with: Solo, Couples, Family, Friends, Business"
    )
    photos: List[str] | None = Field(
        None,
        description="List of photo URLs (optional)"
    )

    @field_validator("title", "comment", "spice_level", "delivery_time", "companion_type", mode="before")
    @classmethod
    def clean_placeholders(cls, v: str | None) -> str | None:
        """Convert placeholder values to None."""
        return clean_placeholder(v)

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int | None) -> int | None:
        """Validate rating is between 1 and 5 if provided."""
        if v is not None and not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v

    @field_validator("spice_level")
    @classmethod
    def validate_spice_level(cls, v: str | None) -> str | None:
        """Validate spice level if provided."""
        if v is not None:
            valid_levels = ["Mild", "Medium", "Spicy", "Extra Spicy"]
            if v not in valid_levels:
                raise ValueError(f"Spice level must be one of: {', '.join(valid_levels)}")
        return v

    @field_validator("delivery_time")
    @classmethod
    def validate_delivery_time(cls, v: str | None) -> str | None:
        """Validate delivery time if provided."""
        if v is not None:
            valid_times = ["Early", "On-Time", "Late"]
            if v not in valid_times:
                raise ValueError(f"Delivery time must be one of: {', '.join(valid_times)}")
        return v

    @field_validator("companion_type")
    @classmethod
    def validate_companion_type(cls, v: str | None) -> str | None:
        """Validate companion type if provided."""
        if v is not None:
            valid_types = ["Solo", "Couples", "Family", "Friends", "Business"]
            if v not in valid_types:
                raise ValueError(f"Companion type must be one of: {', '.join(valid_types)}")
        return v


class ReviewOut(BaseModel):
    """Schema for review response."""

    id: UUID
    user_id: UUID
    dish_id: UUID
    rating: int
    title: str | None
    comment: str | None
    visit_date: date | None
    spice_level: str | None
    delivery_time: str | None
    companion_type: str | None
    photos: List[str] | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewListItem(BaseModel):
    """Schema for review list item with user info."""

    id: UUID
    user_id: UUID
    rating: int
    title: str | None
    comment: str | None
    visit_date: date | None
    spice_level: str | None
    delivery_time: str | None
    companion_type: str | None
    photos: List[str] | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewAdminOut(BaseModel):
    """Schema for admin review view."""

    id: UUID
    user_id: UUID
    dish_id: UUID
    rating: int
    title: str | None
    comment: str | None
    visit_date: date | None
    spice_level: str | None
    delivery_time: str | None
    companion_type: str | None
    photos: List[str] | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

