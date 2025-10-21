from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.watch_progress import UserWatchProgress
    from app.models.content import UserContentInteraction, UserWatchHistory


class ProfileType(str, Enum):
    STANDARD = "standard"


class ProfileStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class UserProfile(BaseModel, TimestampMixin, table=True):
    __tablename__ = "user_profiles"
    
    # Profile basic info
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    name: str = Field(max_length=100, nullable=False)
    avatar_url: Optional[str] = Field(max_length=500, nullable=True)
    profile_type: ProfileType = Field(default=ProfileType.STANDARD, nullable=False)
    status: ProfileStatus = Field(default=ProfileStatus.ACTIVE, nullable=False)
    
    # Profile settings
    is_primary: bool = Field(default=False, nullable=False)
    language_preference: str = Field(default="en", max_length=10, nullable=False)
    subtitle_preference: str = Field(default="en", max_length=10, nullable=False)
    
    # Optional parental controls (if user wants to restrict content)
    parental_controls_enabled: bool = Field(default=False, nullable=False)
    content_restrictions: Optional[str] = Field(nullable=True)  # JSON string of restrictions
    viewing_time_limit: Optional[int] = Field(nullable=True)  # Minutes per day
    bedtime_start: Optional[str] = Field(max_length=5, nullable=True)  # HH:MM format
    bedtime_end: Optional[str] = Field(max_length=5, nullable=True)  # HH:MM format
    
    # Additional timestamps
    last_used_at: Optional[datetime] = Field(nullable=True)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="profiles")
    watch_progress: list["UserWatchProgress"] = Relationship(
        back_populates="profile",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    content_interactions: list["UserContentInteraction"] = Relationship(
        back_populates="profile",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    watch_history: list["UserWatchHistory"] = Relationship(
        back_populates="profile",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, name={self.name}, type={self.profile_type})>"
