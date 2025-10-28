from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel, TimestampMixin
from sqlmodel import Field
from typing import Optional
from uuid import UUID
import uuid

class UserSettings(BaseModel, TimestampMixin, table=True):
    __tablename__ = "user_settings"
    
    id: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    user_id: UUID = Field(foreign_key="users.id", unique=True, nullable=False, index=True)
    
    # Language & Regional Settings
    language: str = Field(default="en", max_length=10)
    timezone: str = Field(default="UTC", max_length=50)
    date_format: str = Field(default="MM/DD/YYYY", max_length=20)
    currency: str = Field(default="USD", max_length=3)
    
    # Content Preferences
    autoplay: bool = Field(default=True)
    quality_preference: str = Field(default="auto", max_length=20)
    subtitle_language: str = Field(default="en", max_length=10)
    audio_language: str = Field(default="en", max_length=10)
    
    # Notification Preferences
    email_notifications: bool = Field(default=True)
    push_notifications: bool = Field(default=True)
    marketing_emails: bool = Field(default=False)
    security_alerts: bool = Field(default=True)
    billing_notifications: bool = Field(default=True)
    
    # Privacy Settings
    profile_visibility: str = Field(default="private", max_length=20)
    data_sharing: bool = Field(default=False)
    analytics_tracking: bool = Field(default=True)
    personalized_recommendations: bool = Field(default=True)
    
    # Parental Controls
    parental_controls_enabled: bool = Field(default=False)
    content_rating_limit: int = Field(default=18)
    viewing_time_limit: Optional[int] = Field(default=None)  # minutes per day
    bedtime_start: Optional[str] = Field(default=None, max_length=5)  # HH:MM
    bedtime_end: Optional[str] = Field(default=None, max_length=5)  # HH:MM
    
    # Security Settings
    two_factor_enabled: bool = Field(default=False)
    login_notifications: bool = Field(default=True)
    session_timeout: int = Field(default=3600)  # seconds