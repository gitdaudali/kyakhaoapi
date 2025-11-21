"""Order model for tracking restaurant popularity and orders."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin as SQLModelTimestampMixin
from app.models.food import TimestampMixin, UUIDPrimaryKeyMixin


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Order(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Order model for tracking restaurant orders and popularity metrics."""
    __tablename__ = "orders"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="completed", index=True
    )  # pending, completed, cancelled
    total_amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, index=True
    )
    delivery_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivery_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    delivery_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="orders")

