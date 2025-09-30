from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, validator

from app.models.content import ContentRating, ContentStatus, ContentType
from app.models.streaming import StreamingChannelCategory
from app.models.user import ProfileStatus, UserRole

# =============================================================================
# ADMIN UPLOAD ENUMS
# =============================================================================


class S3PathType(str, Enum):
    """Enum for allowed S3 path types in admin uploads"""

    # Streaming Channels
    STREAMING_CHANNELS_ICONS = "streaming-channels/icons"
    STREAMING_CHANNELS_THUMBNAILS = "streaming-channels/thumbnails"

    # Genres
    GENRES_COVERS = "genres/covers"
    GENRES_ICONS = "genres/icons"

    # Content
    CONTENT_THUMBNAILS = "content/thumbnails"
    CONTENT_POSTERS = "content/posters"
    CONTENT_BACKDROPS = "content/backdrops"
    CONTENT_TRAILERS = "content/trailers"

    # Users
    USERS_AVATARS = "users/avatars"
    USERS_BANNERS = "users/banners"

    # Admin
    ADMIN_LOGO = "admin/logo"
    ADMIN_BANNERS = "admin/banners"


class EntityType(str, Enum):
    """Enum for allowed entity types in admin uploads"""

    STREAMING_CHANNELS = "streaming-channels"
    GENRES = "genres"
    CONTENT = "content"
    USERS = "users"


class ImageType(str, Enum):
    """Enum for allowed image types in admin uploads"""

    # Generic types
    ICON = "icon"
    COVER = "cover"
    THUMBNAIL = "thumbnail"
    POSTER = "poster"
    BACKDROP = "backdrop"
    AVATAR = "avatar"
    BANNER = "banner"
    LOGO = "logo"

    # Content specific
    TRAILER = "trailer"


# =============================================================================
# STREAMING CHANNEL ADMIN SCHEMAS
# =============================================================================


class StreamingChannelAdminCreate(BaseModel):
    """Schema for creating streaming channel via admin"""

    name: str = Field(..., min_length=1, max_length=255, description="Channel name")
    stream_url: str = Field(..., min_length=1, description="Stream URL")
    icon: Optional[str] = Field(None, description="Channel icon URL")
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

    @validator("icon")
    def validate_icon(cls, v):
        """Validate icon URL format"""
        if v is not None and v.strip():
            # Basic URL validation
            if not v.startswith(("http://", "https://")):
                raise ValueError("Icon URL must start with http:// or https://")
            return v.strip()
        return v


class StreamingChannelAdminUpdate(BaseModel):
    """Schema for updating streaming channel via admin"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Channel name"
    )
    stream_url: Optional[str] = Field(None, min_length=1, description="Stream URL")
    icon: Optional[str] = Field(None, description="Channel icon URL")
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

    @validator("icon")
    def validate_icon(cls, v):
        """Validate icon URL format"""
        if v is not None and v.strip():
            # Basic URL validation
            if not v.startswith(("http://", "https://")):
                raise ValueError("Icon URL must start with http:// or https://")
            return v.strip()
        return v


class StreamingChannelAdminResponse(BaseModel):
    """Admin response schema for streaming channel"""

    id: UUID = Field(..., description="Channel ID")
    name: str = Field(..., description="Channel name")
    stream_url: str = Field(..., description="Stream URL")
    icon: Optional[str] = Field(None, description="Channel icon URL")
    description: Optional[str] = Field(None, description="Channel description")
    category: Optional[StreamingChannelCategory] = Field(
        None, description="Channel category"
    )
    language: Optional[str] = Field(None, description="Channel language")
    country: Optional[str] = Field(None, description="Channel country")
    quality: Optional[str] = Field(None, description="Stream quality")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_deleted: bool = Field(False, description="Whether channel is deleted")

    class Config:
        from_attributes = True


class StreamingChannelAdminListResponse(BaseModel):
    """Response schema for streaming channel admin list"""

    items: List[StreamingChannelAdminResponse] = Field(
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


class StreamingChannelAdminQueryParams(BaseModel):
    """Query parameters for streaming channel admin endpoints"""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=500, description="Page size")
    search: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Search term"
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
    quality: Optional[str] = Field(None, max_length=20, description="Filter by quality")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    class Config:
        from_attributes = True


# =============================================================================
# GENRE ADMIN SCHEMAS
# =============================================================================


class GenreAdminCreate(BaseModel):
    """Schema for creating genre via admin"""

    name: str = Field(..., min_length=1, max_length=100, description="Genre name")
    slug: str = Field(..., min_length=1, max_length=120, description="Genre slug")
    description: Optional[str] = Field(None, description="Genre description")
    icon_name: Optional[str] = Field(None, max_length=100, description="Icon name")
    cover_image_url: Optional[HttpUrl] = Field(None, description="Cover image URL")
    parent_genre_id: Optional[UUID] = Field(None, description="Parent genre ID")
    is_active: bool = Field(True, description="Whether genre is active")
    is_featured: bool = Field(False, description="Whether genre is featured")
    sort_order: int = Field(0, description="Sort order")

    @validator("name")
    def validate_name(cls, v):
        """Validate genre name"""
        if not v or not v.strip():
            raise ValueError("Genre name cannot be empty")
        return v.strip()

    @validator("slug")
    def validate_slug(cls, v):
        """Validate genre slug"""
        if not v or not v.strip():
            raise ValueError("Genre slug cannot be empty")
        return v.strip().lower().replace(" ", "-")


class GenreAdminUpdate(BaseModel):
    """Schema for updating genre via admin"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Genre name"
    )
    slug: Optional[str] = Field(
        None, min_length=1, max_length=120, description="Genre slug"
    )
    description: Optional[str] = Field(None, description="Genre description")
    icon_name: Optional[str] = Field(None, max_length=100, description="Icon name")
    cover_image_url: Optional[HttpUrl] = Field(None, description="Cover image URL")
    parent_genre_id: Optional[UUID] = Field(None, description="Parent genre ID")
    is_active: Optional[bool] = Field(None, description="Whether genre is active")
    is_featured: Optional[bool] = Field(None, description="Whether genre is featured")
    sort_order: Optional[int] = Field(None, description="Sort order")

    @validator("name")
    def validate_name(cls, v):
        """Validate genre name"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Genre name cannot be empty")
        return v.strip() if v else v

    @validator("slug")
    def validate_slug(cls, v):
        """Validate genre slug"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Genre slug cannot be empty")
        return v.strip().lower().replace(" ", "-") if v else v


class GenreAdminResponse(BaseModel):
    """Admin response schema for genre"""

    id: UUID = Field(..., description="Genre ID")
    name: str = Field(..., description="Genre name")
    slug: str = Field(..., description="Genre slug")
    description: Optional[str] = Field(None, description="Genre description")
    icon_name: Optional[str] = Field(None, description="Icon name")
    cover_image_url: Optional[str] = Field(None, description="Cover image URL")
    parent_genre_id: Optional[UUID] = Field(None, description="Parent genre ID")
    is_active: bool = Field(..., description="Whether genre is active")
    is_featured: bool = Field(..., description="Whether genre is featured")
    sort_order: int = Field(..., description="Sort order")
    content_count: int = Field(..., description="Number of content items in this genre")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_deleted: bool = Field(False, description="Whether genre is deleted")

    class Config:
        from_attributes = True


class GenreAdminListResponse(BaseModel):
    """Response schema for genre admin list"""

    items: List[GenreAdminResponse] = Field(..., description="List of genres")
    total: int = Field(..., description="Total number of genres")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    class Config:
        from_attributes = True


class GenreAdminQueryParams(BaseModel):
    """Query parameters for genre admin endpoints"""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=500, description="Page size")
    search: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Search term"
    )
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_featured: Optional[bool] = Field(None, description="Filter by featured status")
    parent_genre_id: Optional[UUID] = Field(None, description="Filter by parent genre")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    class Config:
        from_attributes = True


# =============================================================================
# CONTENT ADMIN SCHEMAS
# =============================================================================


class ContentAdminQueryParams(BaseModel):
    """Query parameters for content admin endpoints"""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=500, description="Page size")
    search: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Search term"
    )
    content_type: Optional[ContentType] = Field(
        None, description="Filter by content type"
    )
    status: Optional[ContentStatus] = Field(None, description="Filter by status")
    is_featured: Optional[bool] = Field(None, description="Filter by featured status")
    is_trending: Optional[bool] = Field(None, description="Filter by trending status")
    is_new_release: Optional[bool] = Field(
        None, description="Filter by new release status"
    )
    is_premium: Optional[bool] = Field(None, description="Filter by premium status")
    genre_id: Optional[UUID] = Field(None, description="Filter by genre")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    class Config:
        from_attributes = True


# =============================================================================
# USER ADMIN SCHEMAS
# =============================================================================


class UserAdminQueryParams(BaseModel):
    """Query parameters for user admin endpoints"""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=500, description="Page size")
    search: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Search term"
    )
    role: Optional[UserRole] = Field(None, description="Filter by role")
    profile_status: Optional[ProfileStatus] = Field(
        None, description="Filter by profile status"
    )
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_staff: Optional[bool] = Field(None, description="Filter by staff status")
    is_superuser: Optional[bool] = Field(None, description="Filter by superuser status")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    class Config:
        from_attributes = True
