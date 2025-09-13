from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, HttpUrl


class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_url: HttpUrl
    duration: float
    thumbnail_url: Optional[HttpUrl] = None
    file_size: Optional[int] = None
    resolution: Optional[str] = None
    format: Optional[str] = None


class VideoCreate(VideoBase):
    pass


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[HttpUrl] = None
    status: Optional[str] = None


class VideoInDB(VideoBase):
    id: UUID4
    uploaded_by_id: UUID4
    uploaded_at: datetime
    updated_at: datetime
    views_count: int
    likes_count: int
    status: str
    s3_bucket: Optional[str] = None
    s3_key: Optional[str] = None

    class Config:
        from_attributes = True


class Video(VideoInDB):
    uploaded_by: Optional[str] = None  # username


class VideoViewCreate(BaseModel):
    video_id: UUID4
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class VideoView(VideoViewCreate):
    id: UUID4
    viewer_id: Optional[UUID4] = None
    viewed_at: datetime

    class Config:
        from_attributes = True


class VideoLikeCreate(BaseModel):
    video_id: UUID4


class VideoLike(VideoLikeCreate):
    id: UUID4
    user_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True
