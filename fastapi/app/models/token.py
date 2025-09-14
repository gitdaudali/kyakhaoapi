import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, Relationship

from .base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from .user import User


class Token(BaseModel, TimestampMixin, table=True):
    """Token model for storing access and refresh tokens"""

    __tablename__ = "tokens"

    # Token fields
    token: str = Field(sa_type=String(500), nullable=False, index=True)
    token_type: str = Field(sa_type=String(50), nullable=False, default="bearer")
    expires_at: datetime = Field(sa_type=DateTime(timezone=True), nullable=False)
    is_revoked: bool = Field(sa_type=Boolean, nullable=False, default=False)

    # User relationship
    user_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="users.id", nullable=False, index=True
    )

    # Token family for refresh token rotation
    token_family: Optional[uuid.UUID] = Field(
        sa_type=UUID(as_uuid=True), nullable=True, index=True
    )

    # Device information
    device_id: Optional[str] = Field(sa_type=String(255), nullable=True)
    device_name: Optional[str] = Field(sa_type=String(255), nullable=True)
    ip_address: Optional[str] = Field(sa_type=String(45), nullable=True)
    user_agent: Optional[str] = Field(sa_type=String(500), nullable=True)

    # Token scope (for future use)
    scope: Optional[str] = Field(sa_type=String(500), nullable=True)

    # Relationships
    user: "User" = Relationship(
        back_populates="tokens", sa_relationship_kwargs={"lazy": "selectin"}
    )

    class Config:
        from_attributes = True


class RefreshToken(BaseModel, TimestampMixin, table=True):
    """Refresh token model for token rotation"""

    __tablename__ = "refresh_tokens"

    # Token fields
    token: str = Field(sa_type=String(500), nullable=False, index=True, unique=True)
    expires_at: datetime = Field(sa_type=DateTime(timezone=True), nullable=False)
    is_revoked: bool = Field(sa_type=Boolean, nullable=False, default=False)

    # User relationship
    user_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="users.id", nullable=False, index=True
    )

    # Token family for rotation
    token_family: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), nullable=False, index=True
    )

    # Device information
    device_id: Optional[str] = Field(sa_type=String(255), nullable=True)
    device_name: Optional[str] = Field(sa_type=String(255), nullable=True)
    ip_address: Optional[str] = Field(sa_type=String(45), nullable=True)
    user_agent: Optional[str] = Field(sa_type=String(500), nullable=True)

    # Parent access token (if any)
    parent_token_id: Optional[uuid.UUID] = Field(
        sa_type=UUID(as_uuid=True), nullable=True
    )

    # Relationships
    user: "User" = Relationship(
        back_populates="refresh_tokens", sa_relationship_kwargs={"lazy": "selectin"}
    )

    class Config:
        from_attributes = True


class TokenBlacklist(BaseModel, TimestampMixin, table=True):
    """Token blacklist for revoked tokens"""

    __tablename__ = "token_blacklist"

    # Token information
    token: str = Field(sa_type=String(500), nullable=False, index=True, unique=True)
    token_type: str = Field(sa_type=String(50), nullable=False)
    expires_at: datetime = Field(sa_type=DateTime(timezone=True), nullable=False)

    # User information
    user_id: Optional[uuid.UUID] = Field(
        sa_type=UUID(as_uuid=True), foreign_key="users.id", nullable=True, index=True
    )

    # Revocation reason
    reason: str = Field(sa_type=String(100), nullable=False, default="user_logout")

    # Revoked by
    revoked_by: Optional[uuid.UUID] = Field(sa_type=UUID(as_uuid=True), nullable=True)

    class Config:
        from_attributes = True
