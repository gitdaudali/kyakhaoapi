"""
Watch History Model

This module contains the WatchHistory model for tracking user viewing history.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlmodel import Field

from app.models.base import BaseModel, TimestampMixin


class WatchHistory(BaseModel, TimestampMixin, table=True):
    """
    Watch History model for tracking user viewing history.
    
    This model stores information about what users have watched,
    including titles, thumbnails, and timestamps.
    """
    
    __tablename__ = "watch_history"
    
    # User reference
    user_id: UUID = Field(
        sa_type=PostgresUUID(as_uuid=True),
        nullable=False,
        index=True,
        description="Reference to the user who watched the content"
    )
    
    # Content information
    title: str = Field(
        sa_type=String(500),
        nullable=False,
        description="Title of the watched content"
    )
    
    thumbnail_url: str = Field(
        sa_type=Text,
        nullable=False,
        description="URL of the content thumbnail image"
    )
    
    # Timestamp
    last_watched_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        nullable=False,
        default_factory=datetime.utcnow,
        index=True,
        description="When the user last watched this content"
    )
    
    # Optional content reference for future enhancement
    content_id: Optional[UUID] = Field(
        sa_type=PostgresUUID(as_uuid=True),
        nullable=True,
        index=True,
        description="Optional reference to content table for detailed information"
    )
    
    # Optional episode reference for series content
    episode_id: Optional[UUID] = Field(
        sa_type=PostgresUUID(as_uuid=True),
        nullable=True,
        index=True,
        description="Optional reference to episode for series content"
    )
    
    def __repr__(self) -> str:
        """String representation of the WatchHistory model."""
        return f"<WatchHistory(id={self.id}, user_id={self.user_id}, title='{self.title}')>"
    
    def to_dict(self) -> dict:
        """Convert the model instance to a dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "thumbnail_url": self.thumbnail_url,
            "last_watched_at": self.last_watched_at.isoformat() if self.last_watched_at else None,
            "content_id": str(self.content_id) if self.content_id else None,
            "episode_id": str(self.episode_id) if self.episode_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_deleted": self.is_deleted
        }
