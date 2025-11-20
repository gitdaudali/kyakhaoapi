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
    """
    Schema for creating order from cart.
    
    Examples:
    
    **Order from Specific Cart Items:**
    ```json
    {
      "customer_name": "John Doe",
      "customer_email": "john.doe@example.com",
      "customer_phone": "+1234567890",
      "delivery_address": "123 Main Street, Apt 4B",
      "delivery_city": "New York",
      "delivery_notes": "Please ring doorbell twice",
      "delivery_fee": 5.00,
      "tax_amount": 2.50,
      "discount_amount": 0.00,
      "cart_item_ids": [
        "550e8400-e29b-41d4-a716-446655440000",
        "550e8400-e29b-41d4-a716-446655440001"
      ]
    }
    ```
    
    **Order from All Cart Items:**
    ```json
    {
      "customer_name": "Jane Smith",
      "customer_email": "jane.smith@example.com",
      "customer_phone": "+1987654321",
      "delivery_address": "456 Oak Avenue",
      "delivery_city": "Los Angeles",
      "delivery_notes": "Leave at front door",
      "delivery_fee": 7.50,
      "tax_amount": 3.75,
      "discount_amount": 5.00,
      "cart_item_ids": null
    }
    ```
    
    **Minimal Request:**
    ```json
    {
      "customer_name": "Bob Johnson",
      "customer_email": "bob@example.com"
    }
    ```
    """

    customer_name: str = Field(..., max_length=200, description="Customer full name")
    customer_email: str = Field(..., max_length=255, description="Customer email")
    customer_phone: Optional[str] = Field(None, max_length=30, description="Customer phone number")
    delivery_address: Optional[str] = Field(None, description="Delivery address")
    delivery_city: Optional[str] = Field(None, max_length=120, description="Delivery city")
    delivery_notes: Optional[str] = Field(None, max_length=500, description="Delivery notes")
    delivery_fee: float = Field(default=0.0, ge=0, description="Delivery fee")
    tax_amount: float = Field(default=0.0, ge=0, description="Tax amount")
    discount_amount: float = Field(default=0.0, ge=0, description="Discount amount")
    cart_item_ids: Optional[list[uuid.UUID]] = Field(
        None,
        description="Optional: List of cart item IDs to include in order. If not provided, all cart items will be ordered."
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Order from Specific Cart Items",
                    "summary": "Order only selected items from cart",
                    "description": "Use this when you want to order specific items from your cart",
                    "value": {
                        "customer_name": "John Doe",
                        "customer_email": "john.doe@example.com",
                        "customer_phone": "+1234567890",
                        "delivery_address": "123 Main Street, Apt 4B",
                        "delivery_city": "New York",
                        "delivery_notes": "Please ring doorbell twice",
                        "delivery_fee": 5.00,
                        "tax_amount": 2.50,
                        "discount_amount": 0.00,
                        "cart_item_ids": [
                            "550e8400-e29b-41d4-a716-446655440000",
                            "550e8400-e29b-41d4-a716-446655440001"
                        ]
                    }
                },
                {
                    "name": "Order from All Cart Items",
                    "summary": "Order all items in cart",
                    "description": "Use this when you want to order all items in your cart. Omit cart_item_ids or set to null.",
                    "value": {
                        "customer_name": "Jane Smith",
                        "customer_email": "jane.smith@example.com",
                        "customer_phone": "+1987654321",
                        "delivery_address": "456 Oak Avenue",
                        "delivery_city": "Los Angeles",
                        "delivery_notes": "Leave at front door",
                        "delivery_fee": 7.50,
                        "tax_amount": 3.75,
                        "discount_amount": 5.00,
                        "cart_item_ids": None
                    }
                },
                {
                    "name": "Minimal Request",
                    "summary": "Minimal order request",
                    "description": "Simplest request with only required fields. All cart items will be ordered.",
                    "value": {
                        "customer_name": "Bob Johnson",
                        "customer_email": "bob@example.com"
                    }
                }
            ]
        }


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

