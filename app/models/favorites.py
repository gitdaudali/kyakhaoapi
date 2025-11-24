"""User favorites model for food items."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.food import TimestampMixin, UUIDPrimaryKeyMixin


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserFavorite(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """User favorite food items (many-to-many relationship)."""

    __tablename__ = "user_favorites"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dish_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    dish: Mapped["Dish"] = relationship("Dish", lazy="selectin")

    # Unique constraint: a user can only favorite a dish once
    __table_args__ = (UniqueConstraint("user_id", "dish_id", name="uq_user_dish_favorite"),)


