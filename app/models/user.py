from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, String, Text
from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.content import (
        ContentReview,
        UserContentInteraction,
        UserWatchHistory,
        WatchSession,
    )
    from app.models.token import RefreshToken, Token
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


class User(BaseModel, TimestampMixin, table=True):
    __tablename__ = "users"

    # username: str = Field(max_length=150, unique=True, index=True, default=None)
    email: str = Field(max_length=254, unique=True, index=True)
    first_name: Optional[str] = Field(max_length=150, default=None)
    last_name: Optional[str] = Field(max_length=150, default=None)
    password: str = Field(max_length=128)
    is_active: bool = Field(default=True, index=True)
    is_staff: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    last_login: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    role: UserRole = Field(sa_type=String(20), default=UserRole.USER, index=True)
    profile_status: ProfileStatus = Field(
        sa_type=String(30), default=ProfileStatus.PENDING_VERIFICATION, index=True
    )
    bio: Optional[str] = Field(default=None, sa_type=Text)
    avatar_url: Optional[str] = Field(max_length=500, default=None)

    # Relationships
    tokens: List["Token"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )
    refresh_tokens: List["RefreshToken"] = Relationship(
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
    user_content_interactions: List["UserContentInteraction"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )
    content_reviews: List["ContentReview"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )
    watch_history: List["UserWatchHistory"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )
    watch_sessions: List["WatchSession"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
