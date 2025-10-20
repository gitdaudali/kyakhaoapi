from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class RecentlyWatchedItem(BaseModel):
    """Schema for recently watched list item"""
    content_id: UUID
    title: str
    thumbnail_url: Optional[str] = None
    content_type: str  # "movie" or "episode"
    season_number: Optional[int] = None
    episode_number: Optional[int] = None
    episode_title: Optional[str] = None
    completed_at: datetime
    watch_duration_seconds: int
    completion_percentage: float
    
    # Computed fields
    watch_duration_formatted: str
    days_ago: int
    
    @validator('watch_duration_formatted', pre=True, always=True)
    def format_duration(cls, v, values):
        if 'watch_duration_seconds' in values:
            seconds = values['watch_duration_seconds']
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes:02d}:{secs:02d}"
        return "0:00"
    
    @validator('days_ago', pre=True, always=True)
    def calculate_days_ago(cls, v, values):
        if 'completed_at' in values:
            now = datetime.utcnow()
            delta = now - values['completed_at']
            return delta.days
        return 0


class RecentlyWatchedResponse(BaseModel):
    """Schema for recently watched list response"""
    items: List[RecentlyWatchedItem]
    total: int
    has_more: bool


class RecentlyWatchedStats(BaseModel):
    """Schema for recently watched statistics"""
    total_completed_content: int
    total_hours_watched: float
    average_completion_time: float  # Average time to complete content
    most_watched_content_type: str
    completion_streak_days: int
    last_completed_at: Optional[datetime] = None


class RecentlyWatchedDetail(BaseModel):
    """Schema for specific recently watched content detail"""
    content_id: UUID
    episode_id: Optional[UUID] = None
    title: str
    content_type: str
    season_number: Optional[int] = None
    episode_number: Optional[int] = None
    episode_title: Optional[str] = None
    completed_at: datetime
    watch_duration_seconds: int
    completion_percentage: float
    total_duration_seconds: int
    
    # Computed fields
    watch_duration_formatted: str
    total_duration_formatted: str
    days_ago: int
    
    @validator('watch_duration_formatted', pre=True, always=True)
    def format_watch_duration(cls, v, values):
        if 'watch_duration_seconds' in values:
            seconds = values['watch_duration_seconds']
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes:02d}:{secs:02d}"
        return "0:00"
    
    @validator('total_duration_formatted', pre=True, always=True)
    def format_total_duration(cls, v, values):
        if 'total_duration_seconds' in values:
            seconds = values['total_duration_seconds']
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes:02d}:{secs:02d}"
        return "0:00"
    
    @validator('days_ago', pre=True, always=True)
    def calculate_days_ago(cls, v, values):
        if 'completed_at' in values:
            now = datetime.utcnow()
            delta = now - values['completed_at']
            return delta.days
        return 0


