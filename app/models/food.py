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
from sqlalchemy.dialects.postgresql import JSON, UUID
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

# Association table for many-to-many between users and allergies
UserAllergyAssociation = Table(
    "user_allergies",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("allergy_id", UUID(as_uuid=True), ForeignKey("allergies.id", ondelete="CASCADE"), primary_key=True),
    Column("added_at", DateTime(timezone=True), default=utcnow, nullable=False),
    UniqueConstraint("user_id", "allergy_id", name="uq_user_allergy"),
)

# Association table for many-to-many between users and cuisines (favorite cuisines)
UserCuisineAssociation = Table(
    "user_cuisines",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("cuisine_id", UUID(as_uuid=True), ForeignKey("cuisines.id", ondelete="CASCADE"), primary_key=True),
    Column("added_at", DateTime(timezone=True), default=utcnow, nullable=False),
    UniqueConstraint("user_id", "cuisine_id", name="uq_user_cuisine"),
)

# Association table for many-to-many between users and restaurants (preferred restaurants)
UserRestaurantAssociation = Table(
    "user_restaurants",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("restaurant_id", UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), primary_key=True),
    Column("added_at", DateTime(timezone=True), default=utcnow, nullable=False),
    UniqueConstraint("user_id", "restaurant_id", name="uq_user_restaurant"),
)


class Cuisine(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cuisines"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    dishes: Mapped[List["Dish"]] = relationship(
        "Dish", back_populates="cuisine", cascade="all, delete-orphan"
    )
    # Note: users relationship not defined here - accessed via queries in endpoints


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
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    delivery_radius_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=10.0)

    dishes: Mapped[List["Dish"]] = relationship(
        "Dish", back_populates="restaurant", cascade="all, delete-orphan"
    )
    reservations: Mapped[List["Reservation"]] = relationship(
        "Reservation", back_populates="restaurant", cascade="all, delete-orphan"
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order", back_populates="restaurant", cascade="all, delete-orphan"
    )
    # Note: users relationship not defined here - accessed via queries in endpoints


class Dish(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Dish model - table name 'dishes' must match ForeignKey references in Review model."""
    __tablename__ = "dishes"  # This table name is referenced as "dishes.id" in Review model

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


# Review model for dish ratings and comments
class Review(BaseModel, SQLModelTimestampMixin, table=True):
    __tablename__ = "reviews"

    user_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="users.id", nullable=False, index=True
    )
    dish_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), 
        foreign_key="dishes.id",
        nullable=False, 
        index=True,
        description="Foreign key to dishes table (table name must be 'dishes')"
    )
    rating: int = Field(
        sa_type=Integer, nullable=False, index=True,
        description="Rating from 1 to 5"
    )
    title: Optional[str] = Field(
        sa_type=String(120), nullable=True, default=None, max_length=120,
        description="Review title (max 120 characters)"
    )
    comment: str = Field(
        sa_type=Text, nullable=False, max_length=1000,
        description="Review comment/body (max 1000 characters, required)"
    )
    visit_date: Optional[Date] = Field(
        sa_type=Date, nullable=True, default=None,
        description="Date when the user visited/ordered (e.g., October 2025)"
    )
    spice_level: Optional[str] = Field(
        sa_type=String(50), nullable=True, default=None,
        description="Spice level: Mild, Medium, Spicy, Extra Spicy"
    )
    delivery_time: Optional[str] = Field(
        sa_type=String(50), nullable=True, default=None,
        description="Delivery time: Early, On-Time, Late"
    )
    companion_type: Optional[str] = Field(
        sa_type=String(50), nullable=True, default=None,
        description="Who they went with: Solo, Couples, Family, Friends, Business"
    )
    photos: Optional[List[str]] = Field(
        sa_type=JSON, nullable=True, default=None,
        description="JSON array of photo URLs"
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "dish_id",
            name="uq_user_dish_review",
        ),
    )


class Allergy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Allergy model for food allergies."""
    __tablename__ = "allergies"

    # Use UUID as primary key
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="food")
    # Store the original string identifier for reference (e.g., "wheat", "peanut")
    identifier: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True, index=True)

    # Note: users relationship not defined here - accessed via queries in endpoints