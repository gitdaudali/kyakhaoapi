"""
Database models for recommendation engine and user interaction tracking.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
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
from app.models.food import UUIDPrimaryKeyMixin, TimestampMixin
from sqlmodel import Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class InteractionType(str, Enum):
    """Types of user interactions with dishes."""
    CLICK = "click"
    VIEW = "view"
    RESERVATION = "reservation"
    ORDER = "order"
    FAVORITE = "favorite"
    REVIEW = "review"


class SpiceLevel(str, Enum):
    """Spice level options."""
    MILD = "Mild"
    MEDIUM = "Medium"
    SPICY = "Spicy"
    EXTRA_SPICY = "Extra Spicy"


class DietaryTag(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Dietary tags for dishes (e.g., Vegetarian, Vegan, Gluten-Free, Halal)."""
    __tablename__ = "dietary_tags"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    identifier: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, unique=True, index=True
    )  # Machine-readable identifier (e.g., 'vegetarian', 'vegan')
    
    # Relationship to dishes (many-to-many)
    dishes: Mapped[List["Dish"]] = relationship(
        "Dish",
        secondary="dish_dietary_tags",
        back_populates="dietary_tags",
    )


# Association table for many-to-many between dishes and dietary tags
DishDietaryTagAssociation = Table(
    "dish_dietary_tags",
    Base.metadata,
    Column("dish_id", UUID(as_uuid=True), ForeignKey("dishes.id", ondelete="CASCADE"), primary_key=True),
    Column("dietary_tag_id", UUID(as_uuid=True), ForeignKey("dietary_tags.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("dish_id", "dietary_tag_id", name="uq_dish_dietary_tag"),
)


class UserPreference(BaseModel, SQLModelTimestampMixin, table=True):
    """User preferences for recommendations (budget, dietary preferences)."""
    __tablename__ = "user_preferences"

    user_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="users.id",
        nullable=False,
        unique=True,
        index=True,
        description="One preference record per user"
    )
    
    # Budget preferences (in local currency)
    min_budget: Optional[float] = Field(
        default=None,
        sa_type=Numeric(10, 2),
        description="Minimum budget per meal"
    )
    max_budget: Optional[float] = Field(
        default=None,
        sa_type=Numeric(10, 2),
        description="Maximum budget per meal"
    )
    
    # Dietary preferences (stored as JSON string of dietary tag IDs)
    preferred_dietary_tags: Optional[str] = Field(
        default=None,
        sa_type=String(500),
        description="JSON string array of preferred dietary tag IDs"
    )
    
    # Additional preferences
    preferred_spice_level: Optional[str] = Field(
        default=None,
        sa_type=String(50),
        description="Preferred spice level: Mild, Medium, Spicy, Extra Spicy"
    )


class UserInteraction(BaseModel, SQLModelTimestampMixin, table=True):
    """Track user interactions with dishes for ML training data."""
    __tablename__ = "user_interactions"

    user_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="users.id",
        nullable=False,
        index=True
    )
    dish_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="dishes.id",
        nullable=False,
        index=True
    )
    interaction_type: str = Field(
        sa_type=String(50),
        nullable=False,
        index=True,
        description="Type of interaction: click, view, reservation, order, favorite, review"
    )
    interaction_metadata: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="JSON metadata about the interaction (e.g., session_id, device_type)"
    )
    interaction_timestamp: datetime = Field(
        default_factory=utcnow,
        sa_type=DateTime(timezone=True),
        nullable=False,
        index=True
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "dish_id",
            "interaction_type",
            "interaction_timestamp",
            name="uq_user_dish_interaction",
        ),
    )

