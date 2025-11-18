"""Promotion model."""
import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import Date, Float, JSON, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from app.models.base import BaseModel, TimestampMixin


class Promotion(BaseModel, TimestampMixin, table=True):
    """Model for promotions and discount codes."""

    __tablename__ = "promotions"

    title: str = Field(sa_type=String(255), nullable=False, max_length=255)
    description: Optional[str] = Field(sa_type=String(1000), nullable=True, default=None, max_length=1000)
    promo_code: Optional[str] = Field(sa_type=String(50), nullable=True, unique=True, index=True, max_length=50)
    discount_type: str = Field(sa_type=String(20), nullable=False, index=True, max_length=20)  # "percentage" or "fixed"
    value: float = Field(sa_type=Numeric(10, 2), nullable=False)  # Discount value
    start_date: date = Field(sa_type=Date, nullable=False, index=True)
    end_date: date = Field(sa_type=Date, nullable=False, index=True)
    minimum_order_amount: float = Field(sa_type=Numeric(10, 2), nullable=False, default=0.0)
    applicable_dish_ids: Optional[List[str]] = Field(
        sa_type=JSON, nullable=True, default=None,
        description="List of dish UUIDs (as strings) this promotion applies to (null = applies to all dishes)"
    )

