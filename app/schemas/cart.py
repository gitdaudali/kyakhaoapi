"""Cart and Order schemas for API requests and responses."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.dish import DishOut


class CartItemCreate(BaseModel):
    """Schema for adding item to cart."""

    dish_id: uuid.UUID = Field(..., description="Dish ID to add to cart")
    quantity: int = Field(default=1, ge=1, le=50, description="Quantity of the dish")
    special_instructions: Optional[str] = Field(
        None, max_length=500, description="Special instructions for the dish"
    )


class CartItemUpdate(BaseModel):
    """Schema for updating cart item."""

    quantity: int = Field(..., ge=1, le=50, description="New quantity")
    special_instructions: Optional[str] = Field(
        None, max_length=500, description="Special instructions"
    )


class CartItemOut(BaseModel):
    """Schema for cart item response."""

    id: uuid.UUID
    dish_id: uuid.UUID
    dish: DishOut
    quantity: int
    unit_price: float
    subtotal: float
    special_instructions: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CartOut(BaseModel):
    """Schema for cart response."""

    id: uuid.UUID
    user_id: uuid.UUID
    items: List[CartItemOut] = []
    total_amount: float
    item_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderItemOut(BaseModel):
    """Schema for order item response."""

    id: uuid.UUID
    dish_id: uuid.UUID
    dish_name: str
    quantity: int
    unit_price: float
    subtotal: float
    special_instructions: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Schema for creating order from cart."""

    customer_name: str = Field(..., max_length=200, description="Customer full name")
    customer_email: str = Field(..., max_length=255, description="Customer email")
    customer_phone: Optional[str] = Field(None, max_length=30, description="Customer phone number")
    delivery_address: Optional[str] = Field(None, description="Delivery address")
    delivery_city: Optional[str] = Field(None, max_length=120, description="Delivery city")
    delivery_notes: Optional[str] = Field(None, max_length=500, description="Delivery notes")
    delivery_fee: float = Field(default=0.0, ge=0, description="Delivery fee")
    tax_amount: float = Field(default=0.0, ge=0, description="Tax amount")
    discount_amount: float = Field(default=0.0, ge=0, description="Discount amount")


class OrderOut(BaseModel):
    """Schema for order response."""

    id: uuid.UUID
    user_id: uuid.UUID
    order_number: str
    status: str
    items: List[OrderItemOut] = []
    subtotal: float
    tax_amount: float
    delivery_fee: float
    discount_amount: float
    total_amount: float
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_city: Optional[str] = None
    delivery_notes: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    prepared_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

