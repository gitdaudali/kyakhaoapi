from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Index
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.content import Content, Episode
    from app.models.user import User


class UserWatchProgress(BaseModel, TimestampMixin, table=True):
    """Model for tracking user watch progress on content"""
    
    __tablename__ = "user_watch_progress"
    
    # Foreign keys
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    content_id: UUID = Field(foreign_key="contents.id", nullable=False)
    episode_id: Optional[UUID] = Field(foreign_key="episodes.id", nullable=True, default=None)
    
    # Progress tracking fields
    current_position_seconds: int = Field(default=0, nullable=False)
    total_duration_seconds: int = Field(default=0, nullable=False)
    watch_percentage: float = Field(default=0.0, nullable=False)
    is_completed: bool = Field(default=False, nullable=False)
    
    # Timestamps
    last_watched_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_type=DateTime(timezone=True),
        nullable=False
    )
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="watch_progress")
    content: Optional["Content"] = Relationship(back_populates="watch_progress")
    episode: Optional["Episode"] = Relationship(back_populates="watch_progress")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_watch_progress_user_id', 'user_id'),
        Index('idx_user_watch_progress_content_id', 'content_id'),
        Index('idx_user_watch_progress_last_watched', 'last_watched_at'),
        Index('idx_user_watch_progress_user_content', 'user_id', 'content_id'),
        Index('idx_user_watch_progress_user_episode', 'user_id', 'episode_id'),
    )
    
    def __repr__(self):
        return f"<UserWatchProgress(user_id={self.user_id}, content_id={self.content_id}, progress={self.watch_percentage}%)>"
    
    @property
    def resume_position_formatted(self) -> str:
        """Return formatted resume position (e.g., '15:30')"""
        minutes = self.current_position_seconds // 60
        seconds = self.current_position_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def total_duration_formatted(self) -> str:
        """Return formatted total duration (e.g., '1:45:30')"""
        hours = self.total_duration_seconds // 3600
        minutes = (self.total_duration_seconds % 3600) // 60
        seconds = self.total_duration_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

