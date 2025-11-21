from datetime import datetime
from enum import Enum
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin
from app.models.token import RefreshToken, Token

if TYPE_CHECKING:
    from app.models.verification import (
        EmailVerificationOTP,
        EmailVerificationToken,
        PasswordResetOTP,
        PasswordResetToken,
    )


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class ProfileStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING_VERIFICATION = "pending_verification"


class SignupType(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"
    APPLE = "apple"


class User(BaseModel, TimestampMixin, table=True):
    __tablename__ = "users"

    email: str = Field(max_length=254, unique=True, index=True)
    first_name: Optional[str] = Field(max_length=150, default=None)
    last_name: Optional[str] = Field(max_length=150, default=None)
    password: Optional[str] = Field(max_length=128, default=None)
    is_active: bool = Field(default=True, index=True)
    is_staff: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    last_login: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )

    # Add these JSON fields for flexible data storage
    analytics_data: Optional[str] = Field(default=None)  # JSON string
    activity_log: Optional[str] = Field(default=None)  # JSON string
    notification_preferences: Optional[str] = Field(default=None)  # JSON string
    device_info: Optional[str] = Field(default=None)  # JSON string

    
    role: UserRole = Field(sa_type=String(20), default=UserRole.USER, index=True)
    profile_status: ProfileStatus = Field(
        sa_type=String(30), default=ProfileStatus.PENDING_VERIFICATION, index=True
    )
    avatar_url: Optional[str] = Field(max_length=500, default=None)

    # OAuth fields
    signup_type: SignupType = Field(
        sa_type=String(20), default=SignupType.EMAIL, index=True
    )
    google_id: Optional[str] = Field(max_length=100, default=None, index=True)
    apple_id: Optional[str] = Field(max_length=100, default=None, index=True)

    # Relationships
    tokens: List[Token] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )
    refresh_tokens: List[RefreshToken] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )
    password_reset_tokens: List["PasswordResetToken"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )
    email_verification_tokens: List["EmailVerificationToken"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )
    email_verification_otps: List["EmailVerificationOTP"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )
    password_reset_otps: List["PasswordResetOTP"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )
    
    # Personalization preferences
    spice_level_preference: Optional[str] = Field(
        max_length=50, default=None,
        description="User's preferred spice level: Mild, Spicy, Extra Spicy"
    )
    
    # Note: Allergies, favorite_cuisines, and preferred_restaurants relationships
    # are not defined here because they use SQLAlchemy Base models (not SQLModel).
    # These are accessed through queries in the endpoints using the association tables.

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
