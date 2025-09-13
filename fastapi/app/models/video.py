from typing import Optional

from sqlalchemy import Text
from sqlmodel import Field

from app.models.base import BaseModel, TimestampMixin


class Video(BaseModel, TimestampMixin, table=True):
    __tablename__ = "videos_video"

    title: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, sa_type=Text)
    file_url: str = Field(max_length=500)
    duration: float = Field(ge=0)
    thumbnail_url: Optional[str] = Field(max_length=500, default=None)
    uploaded_by_id: str = Field(foreign_key="users_user.id", index=True)
    views_count: int = Field(default=0, index=True)
    likes_count: int = Field(default=0, index=True)
    status: str = Field(max_length=20, default="uploading", index=True)
    file_size: Optional[int] = Field(default=None)
    resolution: Optional[str] = Field(max_length=20, default=None)
    format: Optional[str] = Field(max_length=10, default=None)
    s3_bucket: Optional[str] = Field(max_length=255, default=None)
    s3_key: Optional[str] = Field(max_length=500, default=None)

    # Relationships will be handled separately

    def __repr__(self):
        return f"<Video(id={self.id}, title='{self.title}')>"


class VideoView(BaseModel, TimestampMixin, table=True):
    __tablename__ = "videos_video_view"

    video_id: str = Field(foreign_key="videos_video.id", index=True)
    viewer_id: Optional[str] = Field(
        foreign_key="users_user.id", default=None, index=True
    )
    ip_address: Optional[str] = Field(max_length=45, default=None)
    user_agent: Optional[str] = Field(default=None, sa_type=Text)

    # Relationships will be handled separately

    def __repr__(self):
        return f"<VideoView(video_id={self.video_id}, viewed_at={self.created_at})>"


class VideoLike(BaseModel, TimestampMixin, table=True):
    __tablename__ = "videos_video_like"

    video_id: str = Field(foreign_key="videos_video.id", index=True)
    user_id: str = Field(foreign_key="users_user.id", index=True)

    # Relationships will be handled separately

    def __repr__(self):
        return f"<VideoLike(video_id={self.video_id}, user_id={self.user_id})>"
