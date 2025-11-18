from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseModel, TimestampMixin as SQLModelTimestampMixin
from sqlmodel import Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Reusable timestamp + soft delete mixin for SQLAlchemy models."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)


class UUIDPrimaryKeyMixin:
    """Mixin that provides a UUID primary key column."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )


# Association table for many-to-many between dishes and moods
DishMoodAssociation = Table(
    "dish_moods",
    Base.metadata,
    Column("dish_id", UUID(as_uuid=True), ForeignKey("dishes.id"), primary_key=True),
    Column("mood_id", UUID(as_uuid=True), ForeignKey("moods.id"), primary_key=True),
    UniqueConstraint("dish_id", "mood_id", name="uq_dish_mood"),
)


class Cuisine(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cuisines"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    dishes: Mapped[List["Dish"]] = relationship(
        "Dish", back_populates="cuisine", cascade="all, delete-orphan"
    )


class Mood(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "moods"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    dishes: Mapped[List["Dish"]] = relationship(
        "Dish",
        secondary=DishMoodAssociation,
        back_populates="moods",
    )


class Restaurant(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "restaurants"

    name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address_line: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(120), nullable=True, index=True)
    state: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    price_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    dishes: Mapped[List["Dish"]] = relationship(
        "Dish", back_populates="restaurant", cascade="all, delete-orphan"
    )
    reservations: Mapped[List["Reservation"]] = relationship(
        "Reservation", back_populates="restaurant", cascade="all, delete-orphan"
    )


class Dish(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "dishes"

    name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False, index=True
    )
    cuisine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cuisines.id"), nullable=False, index=True
    )
    price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    featured_week: Mapped[Optional[Date]] = mapped_column(Date, nullable=True, index=True)
    calories: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    preparation_time_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    cuisine: Mapped["Cuisine"] = relationship("Cuisine", back_populates="dishes")
    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="dishes")
    moods: Mapped[List["Mood"]] = relationship(
        "Mood",
        secondary=DishMoodAssociation,
        back_populates="dishes",
    )


class Reservation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reservations"

    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False, index=True
    )
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    reservation_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    party_size: Mapped[int] = mapped_column(Integer, nullable=False)
    special_requests: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="reservations")

    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "reservation_time",
            "customer_email",
            name="uq_reservation_unique_slot",
        ),
    )


# Note: Favorite model uses SQLModel (BaseModel) instead of SQLAlchemy Base
# to ensure it's in the same metadata as User model for proper foreign key resolution
class Favorite(BaseModel, SQLModelTimestampMixin, table=True):
    __tablename__ = "favorites"

    user_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="users.id", nullable=False, index=True
    )
    item_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), nullable=False, index=True
    )
    # item_type can be 'dish' or 'restaurant' to support different types of favorites
    item_type: str = Field(sa_type=String(50), nullable=False, default="dish", index=True)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "item_id",
            "item_type",
            name="uq_user_item_favorite",
        ),
    )