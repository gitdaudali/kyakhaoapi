from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class WatchProgressUpdate(BaseModel):
    """Schema for updating watch progress"""
    current_position_seconds: int = Field(..., ge=0, description="Current position in seconds")
    total_duration_seconds: int = Field(..., gt=0, description="Total duration in seconds")
    
    @validator('current_position_seconds')
    def validate_current_position(cls, v, values):
        if 'total_duration_seconds' in values and v > values['total_duration_seconds']:
            raise ValueError('Current position cannot exceed total duration')
        return v


class WatchProgressResponse(BaseModel):
    """Schema for watch progress response"""
    id: UUID
    user_id: UUID
    content_id: UUID
    episode_id: Optional[UUID] = None
    current_position_seconds: int
    total_duration_seconds: int
    watch_percentage: float
    is_completed: bool
    last_watched_at: datetime
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    resume_position_formatted: str
    total_duration_formatted: str
    
    class Config:
        from_attributes = True


class ContinueWatchingItem(BaseModel):
    """Schema for continue watching list item"""
    content_id: UUID
    title: str
    thumbnail_url: Optional[str] = None
    content_type: str  # "movie" or "episode"
    season_number: Optional[int] = None
    episode_number: Optional[int] = None
    episode_title: Optional[str] = None
    resume_position_seconds: int
    total_duration_seconds: int
    watch_percentage: float
    last_watched_at: datetime
    
    # Computed fields
    resume_position_formatted: str
    total_duration_formatted: str
    time_remaining_seconds: int
    
    @validator('time_remaining_seconds', pre=True, always=True)
    def calculate_time_remaining(cls, v, values):
        if 'total_duration_seconds' in values and 'resume_position_seconds' in values:
            return values['total_duration_seconds'] - values['resume_position_seconds']
        return 0


class ContinueWatchingResponse(BaseModel):
    """Schema for continue watching list response"""
    items: List[ContinueWatchingItem]
    total: int
    has_more: bool


class ResumePositionResponse(BaseModel):
    """Schema for resume position response"""
    content_id: UUID
    episode_id: Optional[UUID] = None
    resume_position_seconds: int
    total_duration_seconds: int
    watch_percentage: float
    is_completed: bool
    last_watched_at: datetime
    
    # Computed fields
    resume_position_formatted: str
    total_duration_formatted: str
    time_remaining_seconds: int
    
    @validator('time_remaining_seconds', pre=True, always=True)
    def calculate_time_remaining(cls, v, values):
        if 'total_duration_seconds' in values and 'resume_position_seconds' in values:
            return values['total_duration_seconds'] - values['resume_position_seconds']
        return 0


class WatchProgressStats(BaseModel):
    """Schema for watch progress statistics"""
    total_content_watched: int
    total_hours_watched: float
    completion_rate: float
    continue_watching_count: int
    recently_completed_count: int
    last_watched_at: Optional[datetime] = None


class MarkAsCompletedRequest(BaseModel):
    """Schema for marking content as completed"""
    content_id: UUID
    episode_id: Optional[UUID] = None
    completed_at: Optional[datetime] = None


class RemoveFromContinueWatchingRequest(BaseModel):
    """Schema for removing content from continue watching"""
    content_id: UUID
    episode_id: Optional[UUID] = None
    reason: Optional[str] = None  # "start_over", "not_interested", etc.

