import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Text
from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from .user import User


class Video(BaseModel, TimestampMixin, table=True):
    __tablename__ = "videos"

    title: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, sa_type=Text)
    file_url: str = Field(max_length=500)
    duration: float = Field(ge=0)
    thumbnail_url: Optional[str] = Field(max_length=500, default=None)
    uploaded_by_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    views_count: int = Field(default=0, index=True)
    likes_count: int = Field(default=0, index=True)
    status: str = Field(max_length=20, default="uploading", index=True)
    file_size: Optional[int] = Field(default=None)
    resolution: Optional[str] = Field(max_length=20, default=None)
    format: Optional[str] = Field(max_length=10, default=None)
    s3_bucket: Optional[str] = Field(max_length=255, default=None)
    s3_key: Optional[str] = Field(max_length=500, default=None)

    # Relationships
    uploaded_by: "User" = Relationship(
        back_populates="videos", sa_relationship_kwargs={"lazy": "selectin"}
    )
    views: List["VideoView"] = Relationship(
        back_populates="video",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )
    likes: List["VideoLike"] = Relationship(
        back_populates="video",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )

    def __repr__(self):
        return f"<Video(id={self.id}, title='{self.title}')>"


class VideoView(BaseModel, TimestampMixin, table=True):
    __tablename__ = "video_views"

    video_id: uuid.UUID = Field(foreign_key="videos.id", index=True)
    viewer_id: Optional[uuid.UUID] = Field(
        foreign_key="users.id", default=None, index=True
    )
    ip_address: Optional[str] = Field(max_length=45, default=None)
    user_agent: Optional[str] = Field(default=None, sa_type=Text)

    # Relationships
    video: "Video" = Relationship(
        back_populates="views", sa_relationship_kwargs={"lazy": "selectin"}
    )
    viewer: Optional["User"] = Relationship(
        back_populates="video_views", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"<VideoView(video_id={self.video_id}, viewed_at={self.created_at})>"


class VideoLike(BaseModel, TimestampMixin, table=True):
    __tablename__ = "video_likes"

    video_id: uuid.UUID = Field(foreign_key="videos.id", index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    # Relationships
    video: "Video" = Relationship(
        back_populates="likes", sa_relationship_kwargs={"lazy": "selectin"}
    )
    user: "User" = Relationship(
        back_populates="video_likes", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"<VideoLike(video_id={self.video_id}, user_id={self.user_id})>"
