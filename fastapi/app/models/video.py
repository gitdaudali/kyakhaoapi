import uuid
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Video(Base):
    __tablename__ = "videos_video"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_url = Column(String(500), nullable=False)
    duration = Column(Float, nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users_user.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    status = Column(String(20), default="uploading")
    file_size = Column(Integer, nullable=True)
    resolution = Column(String(20), nullable=True)
    format = Column(String(10), nullable=True)
    s3_bucket = Column(String(255), nullable=True)
    s3_key = Column(String(500), nullable=True)
    
    # Relationships
    uploaded_by = relationship("User", back_populates="uploaded_videos")
    views = relationship("VideoView", back_populates="video")
    likes = relationship("VideoLike", back_populates="video")
    
    def __repr__(self):
        return f"<Video(id={self.id}, title='{self.title}')>"

class VideoView(Base):
    __tablename__ = "videos_video_view"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos_video.id"), nullable=False)
    viewer_id = Column(UUID(as_uuid=True), ForeignKey("users_user.id"), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    video = relationship("Video", back_populates="views")
    viewer = relationship("User", back_populates="video_views")
    
    def __repr__(self):
        return f"<VideoView(video_id={self.video_id}, viewed_at={self.viewed_at})>"

class VideoLike(Base):
    __tablename__ = "videos_video_like"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos_video.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users_user.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    video = relationship("Video", back_populates="likes")
    user = relationship("User", back_populates="video_likes")
    
    def __repr__(self):
        return f"<VideoLike(video_id={self.video_id}, user_id={self.user_id})>"
