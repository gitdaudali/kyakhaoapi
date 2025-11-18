"""Promotion schemas for request and response models."""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

# Placeholder values that should be treated as None
PLACEHOLDERS = {"", "string", "null", "none", "n/a", "-"}


def clean_placeholder(value: Optional[str]) -> Optional[str]:
    """Convert placeholder values to None."""
    if value is None:
        return None
    # Only process string values
    if not isinstance(value, str):
        return value
    cleaned = value.strip().lower()
    return None if cleaned in PLACEHOLDERS else value.strip()


class PromotionBase(BaseModel):
    """Base promotion schema with common fields."""

    title: Optional[str] = Field(None, max_length=255, description="Promotion title")
    description: Optional[str] = Field(None, max_length=1000, description="Promotion description")
    promo_code: Optional[str] = Field(None, max_length=50, description="Unique promo code")

    @field_validator("title", "description", "promo_code", mode="before")
    @classmethod
    def clean_placeholders(cls, v: Optional[str]) -> Optional[str]:
        """Convert placeholder values to None."""
        return clean_placeholder(v)

    @field_validator("promo_code")
    @classmethod
    def normalize_promo_code(cls, v: Optional[str]) -> Optional[str]:
        """Normalize promo code to uppercase."""
        return v.upper() if v else None

    discount_type: str = Field(..., description="Discount type: 'percentage' or 'fixed'")
    value: float = Field(..., gt=0, description="Discount value (percentage or fixed amount)")
    start_date: date = Field(..., description="Promotion start date")
    end_date: date = Field(..., description="Promotion end date")
    minimum_order_amount: float = Field(0.0, ge=0, description="Minimum order amount required")
    applicable_dish_ids: Optional[List[UUID]] = Field(
        None, description="List of dish UUIDs this promotion applies to (null = applies to all)"
    )

    @field_validator("discount_type")
    @classmethod
    def validate_discount_type(cls, v: str) -> str:
        """Validate discount type."""
        if v not in ["percentage", "fixed"]:
            raise ValueError("discount_type must be 'percentage' or 'fixed'")
        return v

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: float, info) -> float:
        """Validate discount value based on type."""
        if hasattr(info, "data") and info.data:
            discount_type = info.data.get("discount_type")
            if discount_type == "percentage" and v > 100:
                raise ValueError("Percentage discount cannot exceed 100")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: date, info) -> date:
        """Validate that end_date is after start_date."""
        if hasattr(info, "data") and info.data:
            start_date = info.data.get("start_date")
            if start_date and v <= start_date:
                raise ValueError("end_date must be after start_date")
        return v


class PromotionCreate(PromotionBase):
    """Schema for creating a new promotion."""

    @model_validator(mode="after")
    def validate_required_fields(self):
        """Validate that required fields are not None after placeholder cleaning."""
        if self.title is None:
            raise ValueError("Title is required")
        if self.promo_code is None:
            raise ValueError("Promo code is required")
        return self


class PromotionUpdate(BaseModel):
    """Schema for updating a promotion."""

    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    promo_code: Optional[str] = Field(None, max_length=50)
    discount_type: Optional[str] = Field(None)
    value: Optional[float] = Field(None, gt=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    minimum_order_amount: Optional[float] = Field(None, ge=0)
    applicable_dish_ids: Optional[List[UUID]] = Field(None)

    @field_validator("title", "description", "promo_code", mode="before")
    @classmethod
    def clean_placeholders(cls, v: Optional[str]) -> Optional[str]:
        """Convert placeholder values to None."""
        return clean_placeholder(v)

    @field_validator("promo_code")
    @classmethod
    def normalize_promo_code(cls, v: Optional[str]) -> Optional[str]:
        """Normalize promo code to uppercase."""
        return v.upper() if v else None

    class Config:
        # Use exclude_unset=True to ignore fields that weren't provided
        # This allows partial updates
        pass

    @field_validator("discount_type")
    @classmethod
    def validate_discount_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate discount type."""
        if v is not None and v not in ["percentage", "fixed"]:
            raise ValueError("discount_type must be 'percentage' or 'fixed'")
        return v

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: Optional[float], info) -> Optional[float]:
        """Validate discount value based on type."""
        if v is None:
            return v
        if hasattr(info, "data") and info.data:
            discount_type = info.data.get("discount_type")
            if discount_type == "percentage" and v > 100:
                raise ValueError("Percentage discount cannot exceed 100")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: Optional[date], info) -> Optional[date]:
        """Validate that end_date is after start_date."""
        if v is None:
            return v
        if hasattr(info, "data") and info.data:
            start_date = info.data.get("start_date")
            if start_date and v <= start_date:
                raise ValueError("end_date must be after start_date")
        return v


class PromotionOut(BaseModel):
    """Schema for promotion response."""

    id: UUID
    title: str
    description: Optional[str]
    promo_code: Optional[str]
    discount_type: str
    value: float
    start_date: date
    end_date: date
    minimum_order_amount: float
    applicable_dish_ids: Optional[List[UUID]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PromotionApply(BaseModel):
    """Schema for applying a promo code."""

    promo_code: str = Field(..., description="Promo code to apply")
    order_amount: float = Field(..., gt=0, description="Order amount before discount")
    dish_ids: Optional[List[UUID]] = Field(None, description="List of dish IDs in the order (can be a single UUID or a list)")

    @field_validator("dish_ids", mode="before")
    @classmethod
    def normalize_dish_ids(cls, v: UUID | List[UUID] | str | List[str] | None) -> Optional[List[UUID]]:
        """Normalize dish_ids to always be a list of UUIDs."""
        if v is None:
            return None
        # If it's a single UUID or string UUID, convert to list
        if isinstance(v, (UUID, str)):
            try:
                return [UUID(v) if isinstance(v, str) else v]
            except (ValueError, TypeError):
                raise ValueError("Invalid UUID format for dish_ids")
        # If it's already a list, convert all items to UUIDs
        if isinstance(v, list):
            try:
                return [UUID(item) if isinstance(item, str) else item for item in v]
            except (ValueError, TypeError):
                raise ValueError("Invalid UUID format in dish_ids list")
        return None


class PromotionApplyResponse(BaseModel):
    """Schema for promo code application response."""

    original_amount: float
    discount_amount: float
    final_amount: float
    message: str

