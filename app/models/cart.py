"""Cart and Order models for e-commerce functionality."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.food import Dish, TimestampMixin, UUIDPrimaryKeyMixin


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class OrderStatus(str, Enum):
    """Order status enumeration."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Cart(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Shopping cart model - one per user."""

    __tablename__ = "carts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    item_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    items: Mapped[List["CartItem"]] = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )


class CartItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Cart item model - represents a dish in the cart."""

    __tablename__ = "cart_items"

    cart_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("carts.id"), nullable=False, index=True
    )
    dish_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dishes.id"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    special_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    dish: Mapped["Dish"] = relationship("Dish")

    __table_args__ = (
        # Ensure one dish per cart (can update quantity instead)
        # This constraint is handled at application level for flexibility
    )


class Order(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Order model - represents a completed order."""

    __tablename__ = "orders"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(30), default=OrderStatus.PENDING.value, nullable=False, index=True
    )
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    delivery_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    discount_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)

    # Customer information
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    customer_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Delivery information
    delivery_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivery_city: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    delivery_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    prepared_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Order item model - represents a dish in an order."""

    __tablename__ = "order_items"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True
    )
    dish_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dishes.id"), nullable=False, index=True
    )
    dish_name: Mapped[str] = mapped_column(String(180), nullable=False)  # Snapshot of dish name
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    special_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    dish: Mapped["Dish"] = relationship("Dish")

