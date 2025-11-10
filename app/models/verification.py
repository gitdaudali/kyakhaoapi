"""
Verification token models for password reset and email verification.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, TYPE_CHECKING

from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, Relationship, SQLModel

from app.core.config import settings
from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class PasswordResetToken(BaseModel, TimestampMixin, table=True):
    """Model for password reset tokens"""

    __tablename__ = "password_reset_tokens"

    token: str = Field(max_length=255, unique=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    expires_at: datetime = Field(
        sa_type=TIMESTAMP(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc)
        + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS),
    )
    is_used: bool = Field(default=False, index=True)
    used_at: Optional[datetime] = Field(default=None, sa_type=TIMESTAMP(timezone=True))

    # Relationship
    user: Optional["User"] = Relationship(back_populates="password_reset_tokens")


class EmailVerificationToken(BaseModel, TimestampMixin, table=True):
    """Model for email verification tokens"""

    __tablename__ = "email_verification_tokens"

    token: str = Field(max_length=255, unique=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    email: str = Field(max_length=254, index=True)
    expires_at: datetime = Field(
        sa_type=TIMESTAMP(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc)
        + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS),
    )
    is_used: bool = Field(default=False, index=True)
    used_at: Optional[datetime] = Field(default=None, sa_type=TIMESTAMP(timezone=True))

    # Relationship
    user: Optional["User"] = Relationship(back_populates="email_verification_tokens")


class EmailVerificationOTP(BaseModel, TimestampMixin, table=True):
    """Model for email verification OTP codes"""

    __tablename__ = "email_verification_otps"

    otp_code: str = Field(max_length=6, index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    email: str = Field(max_length=254, index=True)
    expires_at: datetime = Field(
        sa_type=TIMESTAMP(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    is_used: bool = Field(default=False, index=True)
    used_at: Optional[datetime] = Field(default=None, sa_type=TIMESTAMP(timezone=True))
    attempts: int = Field(default=0, description="Number of verification attempts")

    # Relationship
    user: Optional["User"] = Relationship(back_populates="email_verification_otps")


class PasswordResetOTP(BaseModel, TimestampMixin, table=True):
    """Model for password reset OTP codes"""

    __tablename__ = "password_reset_otps"

    otp_code: str = Field(max_length=6, index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    email: str = Field(max_length=254, index=True)
    expires_at: datetime = Field(
        sa_type=TIMESTAMP(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    is_used: bool = Field(default=False, index=True)
    used_at: Optional[datetime] = Field(default=None, sa_type=TIMESTAMP(timezone=True))
    attempts: int = Field(default=0, description="Number of verification attempts")

    # Relationship
    user: Optional["User"] = Relationship(back_populates="password_reset_otps")
