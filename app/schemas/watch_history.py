"""
Watch History Schemas

This module contains Pydantic schemas for watch history API endpoints.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class WatchHistoryBase(BaseModel):
    """Base schema for watch history with common fields."""
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Title of the watched content"
    )
    
    thumbnail_url: str = Field(
        ...,
        min_length=1,
        description="URL of the content thumbnail image"
    )
    
    content_id: Optional[UUID] = Field(
        None,
        description="Optional reference to content table for detailed information"
    )
    
    episode_id: Optional[UUID] = Field(
        None,
        description="Optional reference to episode for series content"
    )
    
    @validator('thumbnail_url')
    def validate_thumbnail_url(cls, v):
        """Validate that thumbnail_url is a proper URL."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('thumbnail_url must be a valid HTTP/HTTPS URL')
        return v


class WatchHistoryCreate(WatchHistoryBase):
    """Schema for creating a new watch history record."""
    
    user_id: UUID = Field(
        ...,
        description="ID of the user who watched the content"
    )
    
    last_watched_at: Optional[datetime] = Field(
        None,
        description="When the user last watched this content (defaults to now)"
    )


class WatchHistoryUpdate(BaseModel):
    """Schema for updating an existing watch history record."""
    
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Updated title of the watched content"
    )
    
    thumbnail_url: Optional[str] = Field(
        None,
        min_length=1,
        description="Updated URL of the content thumbnail image"
    )
    
    last_watched_at: Optional[datetime] = Field(
        None,
        description="Updated timestamp when the user last watched this content"
    )
    
    @validator('thumbnail_url')
    def validate_thumbnail_url(cls, v):
        """Validate that thumbnail_url is a proper URL."""
        if v is not None and not v.startswith(('http://', 'https://')):
            raise ValueError('thumbnail_url must be a valid HTTP/HTTPS URL')
        return v


class WatchHistoryResponse(WatchHistoryBase):
    """Schema for watch history response."""
    
    id: UUID = Field(
        ...,
        description="Unique identifier for the watch history record"
    )
    
    user_id: UUID = Field(
        ...,
        description="ID of the user who watched the content"
    )
    
    last_watched_at: datetime = Field(
        ...,
        description="When the user last watched this content"
    )
    
    created_at: datetime = Field(
        ...,
        description="When the record was created"
    )
    
    updated_at: datetime = Field(
        ...,
        description="When the record was last updated"
    )
    
    is_deleted: bool = Field(
        ...,
        description="Whether the record is soft deleted"
    )
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WatchHistoryListResponse(BaseModel):
    """Schema for paginated watch history list response."""
    
    items: List[WatchHistoryResponse] = Field(
        ...,
        description="List of watch history records"
    )
    
    total_items: int = Field(
        ...,
        description="Total number of items across all pages"
    )
    
    total_pages: int = Field(
        ...,
        description="Total number of pages"
    )
    
    current_page: int = Field(
        ...,
        description="Current page number"
    )
    
    page_size: int = Field(
        ...,
        description="Number of items per page"
    )
    
    has_next: bool = Field(
        ...,
        description="Whether there is a next page"
    )
    
    has_previous: bool = Field(
        ...,
        description="Whether there is a previous page"
    )


class WatchHistoryDeleteResponse(BaseModel):
    """Schema for watch history deletion response."""
    
    message: str = Field(
        ...,
        description="Success message"
    )
    
    deleted_id: UUID = Field(
        ...,
        description="ID of the deleted record"
    )


class WatchHistoryClearResponse(BaseModel):
    """Schema for clearing all watch history response."""
    
    message: str = Field(
        ...,
        description="Success message"
    )
    
    deleted_count: int = Field(
        ...,
        description="Number of records deleted"
    )


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    
    page: int = Field(
        1,
        ge=1,
        description="Page number (starts from 1)"
    )
    
    limit: int = Field(
        10,
        ge=1,
        le=100,
        description="Number of items per page (max 100)"
    )
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
