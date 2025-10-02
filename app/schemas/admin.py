from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, validator

from app.models.content import ContentRating, ContentStatus, ContentType, MovieJobTitle
from app.models.streaming import StreamingChannelCategory
from app.models.user import ProfileStatus, SignupType, UserRole

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
    CONTENT_VIDEOS = "content/videos"
    CONTENT_EPISODES = "content/episodes"

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


class FileType(str, Enum):
    """Enum for allowed file types in admin uploads"""

    # Image types
    ICON = "icon"
    COVER = "cover"
    THUMBNAIL = "thumbnail"
    POSTER = "poster"
    BACKDROP = "backdrop"
    AVATAR = "avatar"
    BANNER = "banner"
    LOGO = "logo"
    TRAILER = "trailer"

    # Video types
    VIDEO = "video"
    EPISODE = "episode"
    MOVIE = "movie"
    PREVIEW = "preview"

    # Audio types
    AUDIO = "audio"
    SOUNDTRACK = "soundtrack"

    # Document types
    SUBTITLE = "subtitle"
    SCRIPT = "script"


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
    cover_image_url: Optional[str] = Field(None, description="Cover image URL")
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
    cover_image_url: Optional[str] = Field(None, description="Cover image URL")
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
# PEOPLE ADMIN SCHEMAS
# =============================================================================


class PersonAdminCreate(BaseModel):
    """Schema for creating people via admin"""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Person's full name"
    )
    slug: str = Field(
        ..., min_length=1, max_length=300, description="URL-friendly slug"
    )
    biography: Optional[str] = Field(None, description="Person's biography")

    # Personal Information
    birth_date: Optional[date] = Field(None, description="Birth date")
    death_date: Optional[date] = Field(None, description="Death date")
    birth_place: Optional[str] = Field(None, max_length=255, description="Birth place")
    nationality: Optional[str] = Field(None, max_length=100, description="Nationality")
    gender: Optional[str] = Field(None, max_length=20, description="Gender")

    # Visual Assets
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="Profile image URL"
    )
    cover_image_url: Optional[str] = Field(
        None, max_length=500, description="Cover image URL"
    )

    # Career Information
    known_for_department: Optional[str] = Field(
        None, max_length=100, description="Known for department"
    )

    # Status
    is_verified: bool = Field(False, description="Is verified person")
    is_featured: bool = Field(False, description="Is featured person")

    class Config:
        from_attributes = True


class PersonAdminUpdate(BaseModel):
    """Schema for updating people via admin"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Person's full name"
    )
    slug: Optional[str] = Field(
        None, min_length=1, max_length=300, description="URL-friendly slug"
    )
    biography: Optional[str] = Field(None, description="Person's biography")

    # Personal Information
    birth_date: Optional[date] = Field(None, description="Birth date")
    death_date: Optional[date] = Field(None, description="Death date")
    birth_place: Optional[str] = Field(None, max_length=255, description="Birth place")
    nationality: Optional[str] = Field(None, max_length=100, description="Nationality")
    gender: Optional[str] = Field(None, max_length=20, description="Gender")

    # Visual Assets
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="Profile image URL"
    )
    cover_image_url: Optional[str] = Field(
        None, max_length=500, description="Cover image URL"
    )

    # Career Information
    known_for_department: Optional[str] = Field(
        None, max_length=100, description="Known for department"
    )

    # Status
    is_verified: Optional[bool] = Field(None, description="Is verified person")
    is_featured: Optional[bool] = Field(None, description="Is featured person")

    class Config:
        from_attributes = True


class PersonAdminResponse(BaseModel):
    """Response schema for people admin"""

    id: UUID = Field(..., description="Person ID")
    name: str = Field(..., description="Person's full name")
    slug: str = Field(..., description="URL-friendly slug")
    biography: Optional[str] = Field(None, description="Person's biography")

    # Personal Information
    birth_date: Optional[date] = Field(None, description="Birth date")
    death_date: Optional[date] = Field(None, description="Death date")
    birth_place: Optional[str] = Field(None, description="Birth place")
    nationality: Optional[str] = Field(None, description="Nationality")
    gender: Optional[str] = Field(None, description="Gender")

    # Visual Assets
    profile_image_url: Optional[str] = Field(None, description="Profile image URL")
    cover_image_url: Optional[str] = Field(None, description="Cover image URL")

    # Career Information
    known_for_department: Optional[str] = Field(
        None, description="Known for department"
    )

    # Status
    is_verified: bool = Field(..., description="Is verified person")
    is_featured: bool = Field(..., description="Is featured person")

    # Timestamps
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")

    # Relationships
    content_cast: List[dict] = Field(
        default_factory=list, description="Content cast appearances"
    )
    content_crew: List[dict] = Field(
        default_factory=list, description="Content crew appearances"
    )

    class Config:
        from_attributes = True


class PersonAdminListResponse(BaseModel):
    """Response schema for people admin list"""

    items: List[PersonAdminResponse] = Field(..., description="List of people")
    total: int = Field(..., description="Total number of people")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")

    class Config:
        from_attributes = True


class PersonAdminQueryParams(BaseModel):
    """Query parameters for people admin endpoints"""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=500, description="Page size")
    search: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Search term"
    )
    is_verified: Optional[bool] = Field(None, description="Filter by verified status")
    is_featured: Optional[bool] = Field(None, description="Filter by featured status")
    known_for_department: Optional[str] = Field(
        None, max_length=100, description="Filter by department"
    )
    nationality: Optional[str] = Field(
        None, max_length=100, description="Filter by nationality"
    )
    gender: Optional[str] = Field(None, max_length=20, description="Filter by gender")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    class Config:
        from_attributes = True


# =============================================================================
# CONTENT ADMIN SCHEMAS
# =============================================================================


class MovieFileCreate(BaseModel):
    """Schema for creating movie files in content creation"""

    # Required fields
    quality_level: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Quality level (1080p, 720p, etc.)",
    )
    resolution_width: int = Field(..., ge=1, description="Resolution width in pixels")
    resolution_height: int = Field(..., ge=1, description="Resolution height in pixels")
    file_url: str = Field(..., min_length=1, max_length=500, description="File URL")
    duration_seconds: float = Field(..., ge=0.1, description="Duration in seconds")

    # Optional fields
    file_size_bytes: Optional[int] = Field(None, ge=1, description="File size in bytes")
    bitrate_kbps: Optional[int] = Field(None, ge=1, description="Bitrate in kbps")
    video_codec: Optional[str] = Field(None, max_length=50, description="Video codec")
    audio_codec: Optional[str] = Field(None, max_length=50, description="Audio codec")
    container_format: Optional[str] = Field(
        None, max_length=20, description="Container format"
    )

    # Storage Information
    storage_bucket: Optional[str] = Field(
        None, max_length=255, description="Storage bucket"
    )
    storage_key: Optional[str] = Field(None, max_length=500, description="Storage key")
    storage_region: Optional[str] = Field(
        None, max_length=50, description="Storage region"
    )
    cdn_url: Optional[str] = Field(None, max_length=500, description="CDN URL")

    # Processing Status
    is_ready: bool = Field(True, description="Is file ready for streaming")

    # Subtitle and Audio Information
    subtitle_tracks: Optional[str] = Field(None, description="Subtitle tracks (JSON)")
    audio_tracks: Optional[str] = Field(None, description="Audio tracks (JSON)")
    available_languages: Optional[str] = Field(
        None, description="Available languages (JSON)"
    )

    class Config:
        from_attributes = True


class CastMemberCreate(BaseModel):
    """Schema for creating cast members in content creation"""

    person_id: UUID = Field(..., description="Person ID")
    character_name: Optional[str] = Field(
        None, max_length=255, description="Character name"
    )
    cast_order: int = Field(0, ge=0, description="Billing order")
    is_main_cast: bool = Field(False, description="Is main cast member")
    character_image_url: Optional[str] = Field(
        None, max_length=500, description="Character image URL"
    )
    job_title: MovieJobTitle = Field(
        MovieJobTitle.ACTOR, description="Job title (Actor, Actress, etc.)"
    )

    class Config:
        from_attributes = True


class CrewMemberCreate(BaseModel):
    """Schema for creating crew members in content creation"""

    person_id: UUID = Field(..., description="Person ID")
    job_title: MovieJobTitle = Field(..., description="Job title")
    department: str = Field(..., min_length=1, max_length=100, description="Department")
    credit_order: int = Field(0, ge=0, description="Credit order")

    class Config:
        from_attributes = True


class ContentAdminCreate(BaseModel):
    """Schema for creating content via admin"""

    title: str = Field(..., min_length=1, max_length=255, description="Content title")
    slug: str = Field(..., min_length=1, max_length=300, description="Content slug")
    description: Optional[str] = Field(None, description="Content description")
    tagline: Optional[str] = Field(None, max_length=500, description="Content tagline")
    content_type: ContentType = Field(..., description="Content type")
    content_rating: Optional[ContentRating] = Field(None, description="Content rating")

    # Visual Assets
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    backdrop_url: Optional[str] = Field(None, description="Backdrop image URL")
    trailer_url: Optional[str] = Field(None, description="Trailer video URL")
    logo_url: Optional[str] = Field(None, description="Logo image URL")

    # Release Information
    release_date: Optional[date] = Field(None, description="Release date")
    premiere_date: Optional[date] = Field(None, description="Premiere date")
    end_date: Optional[date] = Field(None, description="End date (for series)")

    # Technical Information
    runtime: Optional[int] = Field(None, ge=1, description="Runtime in minutes")
    language: str = Field("en", max_length=10, description="Primary language")
    original_language: Optional[str] = Field(
        None, max_length=10, description="Original language"
    )

    # Series-specific Information
    total_seasons: int = Field(0, ge=0, description="Total seasons")
    total_episodes: int = Field(0, ge=0, description="Total episodes")
    is_ongoing: bool = Field(False, description="Is ongoing series")

    # Platform Features
    is_featured: bool = Field(False, description="Is featured content")
    is_trending: bool = Field(False, description="Is trending content")
    is_new_release: bool = Field(False, description="Is new release")
    is_premium: bool = Field(False, description="Is premium content")

    # Availability
    available_from: Optional[datetime] = Field(None, description="Available from date")
    available_until: Optional[datetime] = Field(
        None, description="Available until date"
    )

    # Discovery
    keywords: Optional[str] = Field(None, description="Content keywords")

    # Genre IDs
    genre_ids: List[UUID] = Field(default_factory=list, description="Genre IDs")

    # Movie Files (optional - for integrated approach)
    movie_files: Optional[List[MovieFileCreate]] = Field(
        None, description="Movie files data"
    )

    # Cast and Crew (optional - for integrated approach)
    cast: Optional[List[CastMemberCreate]] = Field(None, description="Cast members")
    crew: Optional[List[CrewMemberCreate]] = Field(None, description="Crew members")


class ContentAdminUpdate(BaseModel):
    """Schema for updating content via admin"""

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Content title"
    )
    slug: Optional[str] = Field(
        None, min_length=1, max_length=300, description="Content slug"
    )
    description: Optional[str] = Field(None, description="Content description")
    tagline: Optional[str] = Field(None, max_length=500, description="Content tagline")
    content_type: Optional[ContentType] = Field(None, description="Content type")
    content_rating: Optional[ContentRating] = Field(None, description="Content rating")

    # Visual Assets
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    backdrop_url: Optional[str] = Field(None, description="Backdrop image URL")
    trailer_url: Optional[str] = Field(None, description="Trailer video URL")
    logo_url: Optional[str] = Field(None, description="Logo image URL")

    # Release Information
    release_date: Optional[date] = Field(None, description="Release date")
    premiere_date: Optional[date] = Field(None, description="Premiere date")
    end_date: Optional[date] = Field(None, description="End date (for series)")

    # Technical Information
    runtime: Optional[int] = Field(None, ge=1, description="Runtime in minutes")
    language: Optional[str] = Field(None, max_length=10, description="Primary language")
    original_language: Optional[str] = Field(
        None, max_length=10, description="Original language"
    )

    # Series-specific Information
    total_seasons: Optional[int] = Field(None, ge=0, description="Total seasons")
    total_episodes: Optional[int] = Field(None, ge=0, description="Total episodes")
    is_ongoing: Optional[bool] = Field(None, description="Is ongoing series")

    # Platform Features
    is_featured: Optional[bool] = Field(None, description="Is featured content")
    is_trending: Optional[bool] = Field(None, description="Is trending content")
    is_new_release: Optional[bool] = Field(None, description="Is new release")
    is_premium: Optional[bool] = Field(None, description="Is premium content")

    # Availability
    available_from: Optional[datetime] = Field(None, description="Available from date")
    available_until: Optional[datetime] = Field(
        None, description="Available until date"
    )

    # Discovery
    keywords: Optional[str] = Field(None, description="Content keywords")

    # Genre IDs
    genre_ids: Optional[List[UUID]] = Field(None, description="Genre IDs")


class ContentAdminResponse(BaseModel):
    """Admin response schema for content"""

    id: UUID = Field(..., description="Content ID")
    title: str = Field(..., description="Content title")
    slug: str = Field(..., description="Content slug")
    description: Optional[str] = Field(None, description="Content description")
    tagline: Optional[str] = Field(None, description="Content tagline")
    content_type: ContentType = Field(..., description="Content type")
    status: ContentStatus = Field(..., description="Content status")
    content_rating: Optional[ContentRating] = Field(None, description="Content rating")

    # Visual Assets
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    backdrop_url: Optional[str] = Field(None, description="Backdrop image URL")
    trailer_url: Optional[str] = Field(None, description="Trailer video URL")
    logo_url: Optional[str] = Field(None, description="Logo image URL")

    # Release Information
    release_date: Optional[date] = Field(None, description="Release date")
    premiere_date: Optional[date] = Field(None, description="Premiere date")
    end_date: Optional[date] = Field(None, description="End date")

    # Technical Information
    runtime: Optional[int] = Field(None, description="Runtime in minutes")
    language: str = Field(..., description="Primary language")
    original_language: Optional[str] = Field(None, description="Original language")
    keywords: Optional[str] = Field(None, description="Content keywords")

    # Series-specific Information
    total_seasons: int = Field(..., description="Total seasons")
    total_episodes: int = Field(..., description="Total episodes")
    is_ongoing: bool = Field(..., description="Is ongoing series")

    # Platform Features
    is_featured: bool = Field(..., description="Is featured content")
    is_trending: bool = Field(..., description="Is trending content")
    is_new_release: bool = Field(..., description="Is new release")
    is_premium: bool = Field(..., description="Is premium content")

    # Availability
    available_from: Optional[datetime] = Field(None, description="Available from date")
    available_until: Optional[datetime] = Field(
        None, description="Available until date"
    )

    # Metrics
    total_views: int = Field(..., description="Total views")
    likes_count: int = Field(..., description="Likes count")
    reviews_count: int = Field(..., description="Reviews count")
    platform_rating: Optional[float] = Field(None, description="Platform rating")
    platform_votes: int = Field(..., description="Platform votes")

    # Timestamps
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")

    # Relationships
    genres: List[dict] = Field(default_factory=list, description="Content genres")
    seasons: List[dict] = Field(default_factory=list, description="Content seasons")
    cast: List[dict] = Field(default_factory=list, description="Content cast")
    crew: List[dict] = Field(default_factory=list, description="Content crew")
    movie_files: List[dict] = Field(default_factory=list, description="Movie files")

    class Config:
        from_attributes = True


class ContentAdminListResponse(BaseModel):
    """Response schema for content admin list"""

    items: List[ContentAdminResponse] = Field(..., description="List of content")
    total: int = Field(..., description="Total number of content")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")


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


class UserAdminCreate(BaseModel):
    """Schema for creating a user (Admin only)"""

    email: str = Field(..., min_length=5, max_length=254, description="User email")
    first_name: Optional[str] = Field(None, max_length=150, description="First name")
    last_name: Optional[str] = Field(None, max_length=150, description="Last name")
    password: Optional[str] = Field(
        None, min_length=8, max_length=128, description="Password"
    )
    role: UserRole = Field(UserRole.USER, description="User role")
    profile_status: ProfileStatus = Field(
        ProfileStatus.ACTIVE, description="Profile status"
    )
    is_active: bool = Field(True, description="Active status")
    is_staff: bool = Field(False, description="Staff status")
    is_superuser: bool = Field(False, description="Superuser status")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")
    signup_type: SignupType = Field(SignupType.EMAIL, description="Signup type")
    google_id: Optional[str] = Field(None, max_length=100, description="Google ID")
    apple_id: Optional[str] = Field(None, max_length=100, description="Apple ID")

    class Config:
        from_attributes = True


class UserAdminUpdate(BaseModel):
    """Schema for updating a user (Admin only)"""

    email: Optional[str] = Field(
        None, min_length=5, max_length=254, description="User email"
    )
    first_name: Optional[str] = Field(None, max_length=150, description="First name")
    last_name: Optional[str] = Field(None, max_length=150, description="Last name")
    password: Optional[str] = Field(
        None, min_length=8, max_length=128, description="Password"
    )
    role: Optional[UserRole] = Field(None, description="User role")
    profile_status: Optional[ProfileStatus] = Field(None, description="Profile status")
    is_active: Optional[bool] = Field(None, description="Active status")
    is_staff: Optional[bool] = Field(None, description="Staff status")
    is_superuser: Optional[bool] = Field(None, description="Superuser status")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")
    signup_type: Optional[SignupType] = Field(None, description="Signup type")
    google_id: Optional[str] = Field(None, max_length=100, description="Google ID")
    apple_id: Optional[str] = Field(None, max_length=100, description="Apple ID")

    class Config:
        from_attributes = True


class UserAdminResponse(BaseModel):
    """Schema for user response (Admin only)"""

    id: UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    is_active: bool = Field(..., description="Active status")
    is_staff: bool = Field(..., description="Staff status")
    is_superuser: bool = Field(..., description="Superuser status")
    last_login: Optional[datetime] = Field(None, description="Last login")
    role: UserRole = Field(..., description="User role")
    profile_status: ProfileStatus = Field(..., description="Profile status")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    signup_type: SignupType = Field(..., description="Signup type")
    google_id: Optional[str] = Field(None, description="Google ID")
    apple_id: Optional[str] = Field(None, description="Apple ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_deleted: bool = Field(..., description="Deleted status")

    class Config:
        from_attributes = True


class UserAdminListResponse(BaseModel):
    """Schema for user list response (Admin only)"""

    items: List[UserAdminResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")

    class Config:
        from_attributes = True


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
    signup_type: Optional[SignupType] = Field(None, description="Filter by signup type")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    class Config:
        from_attributes = True
