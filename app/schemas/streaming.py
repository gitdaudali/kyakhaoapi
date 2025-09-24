from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, validator

from app.models.streaming import StreamingChannelCategory


class StreamingChannelBase(BaseModel):
    """Base streaming channel schema"""

    name: str = Field(..., min_length=1, max_length=255, description="Channel name")
    stream_url: str = Field(..., min_length=1, description="Stream URL")
    icon: Optional[HttpUrl] = Field(None, description="Channel icon URL")
    description: Optional[str] = Field(
        None, max_length=1000, description="Channel description"
    )
    category: Optional[StreamingChannelCategory] = Field(
        None, description="Channel category"
    )
    language: Optional[str] = Field(None, max_length=50, description="Channel language")
    country: Optional[str] = Field(None, max_length=100, description="Channel country")
    quality: Optional[str] = Field(None, max_length=20, description="Stream quality")

    @validator("stream_url")
    def validate_stream_url(cls, v):
        """Validate stream URL format"""
        if not v or not v.strip():
            raise ValueError("Stream URL cannot be empty")
        return v.strip()

    @validator("name")
    def validate_name(cls, v):
        """Validate channel name"""
        if not v or not v.strip():
            raise ValueError("Channel name cannot be empty")
        return v.strip()


class StreamingChannelCreate(StreamingChannelBase):
    """Schema for creating a streaming channel"""

    pass


class StreamingChannelUpdate(BaseModel):
    """Schema for updating a streaming channel"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Channel name"
    )
    stream_url: Optional[str] = Field(None, min_length=1, description="Stream URL")
    icon: Optional[HttpUrl] = Field(None, description="Channel icon URL")
    description: Optional[str] = Field(
        None, max_length=1000, description="Channel description"
    )
    category: Optional[StreamingChannelCategory] = Field(
        None, description="Channel category"
    )
    language: Optional[str] = Field(None, max_length=50, description="Channel language")
    country: Optional[str] = Field(None, max_length=100, description="Channel country")
    quality: Optional[str] = Field(None, max_length=20, description="Stream quality")

    @validator("stream_url")
    def validate_stream_url(cls, v):
        """Validate stream URL format"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Stream URL cannot be empty")
        return v.strip() if v else v

    @validator("name")
    def validate_name(cls, v):
        """Validate channel name"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Channel name cannot be empty")
        return v.strip() if v else v


class StreamingChannel(StreamingChannelBase):
    """Streaming channel response schema"""

    id: UUID = Field(..., description="Channel ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_deleted: bool = Field(False, description="Whether channel is deleted")

    class Config:
        from_attributes = True


class StreamingChannelSimple(BaseModel):
    """Simplified streaming channel schema for lists"""

    id: UUID = Field(..., description="Channel ID")
    name: str = Field(..., description="Channel name")
    icon: Optional[str] = Field(None, description="Channel icon URL")
    description: Optional[str] = Field(None, description="Channel description")
    category: Optional[StreamingChannelCategory] = Field(
        None, description="Channel category"
    )
    language: Optional[str] = Field(None, description="Channel language")
    country: Optional[str] = Field(None, description="Channel country")
    quality: Optional[str] = Field(None, description="Stream quality")

    class Config:
        from_attributes = True


class StreamingChannelListResponse(BaseModel):
    """Response schema for streaming channel list - following content patterns"""

    items: List[StreamingChannelSimple] = Field(
        ..., description="List of streaming channels"
    )
    total: int = Field(..., description="Total number of channels")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    class Config:
        from_attributes = True


class StreamingChannelQueryParams(BaseModel):
    """Query parameters for streaming channel list"""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=500, description="Page size")
    search: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Search by channel name"
    )
    category: Optional[StreamingChannelCategory] = Field(
        None, description="Filter by category"
    )
    language: Optional[str] = Field(
        None, max_length=50, description="Filter by language"
    )
    country: Optional[str] = Field(
        None, max_length=100, description="Filter by country"
    )
    quality: Optional[str] = Field(
        None, max_length=20, description="Filter by stream quality"
    )
    sort_by: str = Field("name", description="Sort field")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="Sort order")

    class Config:
        from_attributes = True
