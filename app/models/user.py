import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.content import (
        ContentReview,
        UserContentInteraction,
        UserWatchHistory,
        WatchSession,
    )
    from app.models.subscription import Subscription
    from app.models.token import RefreshToken, Token
    from app.models.user_profile import UserProfile
    from app.models.verification import (
        EmailVerificationOTP,
        EmailVerificationToken,
        PasswordResetOTP,
        PasswordResetToken,
    )
    from app.models.watch_progress import UserWatchProgress


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
    search_history: List["UserSearchHistory"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )
    # Subscriptions
    subscriptions: List["Subscription"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )
    # Watch Progress
    watch_progress: List["UserWatchProgress"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )
    # User Profiles
    profiles: List["UserProfile"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class UserSearchHistory(BaseModel, TimestampMixin, table=True):
    """User search history model to track search queries"""

    __tablename__ = "user_search_history"

    user_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="users.id", nullable=False, index=True
    )
    search_query: str = Field(
        sa_type=String(255),
        nullable=False,
        index=True,
        description="The search query text",
    )
    search_count: int = Field(
        default=1,
        nullable=False,
        description="Number of times this search was performed",
    )
    last_searched_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
        index=True,
        description="Last time this search was performed",
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="search_history")

    class Config:
        # Ensure unique constraint on user_id + search_query
        table_args = ({"extend_existing": True},)

    def __repr__(self):
        return f"<UserSearchHistory(id={self.id}, user_id={self.user_id}, query='{self.search_query}')>"
