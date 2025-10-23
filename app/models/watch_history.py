"""
Watch History Model

This module contains the WatchHistory model for tracking user viewing history.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class WatchHistory(BaseModel):
    """
    Watch History model for tracking user viewing history.
    
    This model stores information about what users have watched,
    including titles, thumbnails, and timestamps.
    """
    
    __tablename__ = "watch_history"
    
    # Primary key
    id: UUID = Column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
        index=True
    )
    
    # User reference
    user_id: UUID = Column(
        PostgresUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Reference to the user who watched the content"
    )
    
    # Content information
    title: str = Column(
        String(500),
        nullable=False,
        comment="Title of the watched content"
    )
    
    thumbnail_url: str = Column(
        Text,
        nullable=False,
        comment="URL of the content thumbnail image"
    )
    
    # Timestamp
    last_watched_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When the user last watched this content"
    )
    
    # Optional content reference for future enhancement
    content_id: Optional[UUID] = Column(
        PostgresUUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Optional reference to content table for detailed information"
    )
    
    # Optional episode reference for series content
    episode_id: Optional[UUID] = Column(
        PostgresUUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Optional reference to episode for series content"
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
