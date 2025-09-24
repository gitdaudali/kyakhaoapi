import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class StreamingChannelCategory(str, Enum):
    NEWS = "news"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    RELIGIOUS = "religious"
    KIDS = "kids"
    DOCUMENTARY = "documentary"
    MOVIES = "movies"
    MUSIC = "music"
    EDUCATIONAL = "educational"
    LIFESTYLE = "lifestyle"


class StreamingChannel(BaseModel, TimestampMixin, table=True):
    """Streaming channel model for live TV channels"""

    __tablename__ = "streaming_channels"

    # Basic Information
    name: str = Field(
        sa_type=String(255), nullable=False, index=True, description="Channel name"
    )
    stream_url: str = Field(sa_type=Text, nullable=False, description="Stream URL")
    icon: Optional[str] = Field(
        sa_type=Text, default=None, description="Channel icon URL"
    )

    # Channel Metadata
    description: Optional[str] = Field(
        sa_type=Text, default=None, description="Channel description"
    )
    category: Optional[StreamingChannelCategory] = Field(
        default=None, index=True, description="Channel category"
    )
    language: Optional[str] = Field(
        sa_type=String(50), default=None, index=True, description="Channel language"
    )
    country: Optional[str] = Field(
        sa_type=String(100), default=None, index=True, description="Channel country"
    )

    # Status and Quality
    quality: Optional[str] = Field(
        sa_type=String(20), default=None, description="Stream quality"
    )

    def __repr__(self):
        return f"<StreamingChannel(id={self.id}, name='{self.name}')>"
