from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.content import ContentRating, ContentStatus, ContentType


class GenreBase(BaseModel):
    """Base genre schema"""

    name: str = Field(..., description="Genre name")
    slug: str = Field(..., description="Genre slug")
    description: Optional[str] = Field(None, description="Genre description")
    icon_name: Optional[str] = Field(None, description="Icon name for UI")
    color: Optional[str] = Field(None, description="Color code for UI")
    is_active: bool = Field(True, description="Whether genre is active")


class GenreCreate(GenreBase):
    """Schema for creating a genre"""

    pass


class GenreUpdate(BaseModel):
    """Schema for updating a genre"""

    name: Optional[str] = Field(None, description="Genre name")
    slug: Optional[str] = Field(None, description="Genre slug")
    description: Optional[str] = Field(None, description="Genre description")
    icon_name: Optional[str] = Field(None, description="Icon name for UI")
    color: Optional[str] = Field(None, description="Color code for UI")
    is_active: Optional[bool] = Field(None, description="Whether genre is active")


class Genre(GenreBase):
    """Genre response schema"""

    id: UUID = Field(..., description="Genre ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_deleted: bool = Field(False, description="Whether genre is deleted")

    class Config:
        from_attributes = True


class GenreSimple(BaseModel):
    """Simplified genre schema for content detail"""

    id: UUID = Field(..., description="Genre ID")
    name: str = Field(..., description="Genre name")
    slug: str = Field(..., description="Genre slug")

    class Config:
        from_attributes = True


class PersonSimple(BaseModel):
    """Simplified person schema for content detail"""

    id: UUID = Field(..., description="Person ID")
    name: str = Field(..., description="Person name")
    slug: str = Field(..., description="Person slug")

    class Config:
        from_attributes = True


class CastMember(BaseModel):
    """Cast member schema for content detail"""

    person: PersonSimple = Field(..., description="Person information")
    character_name: Optional[str] = Field(None, description="Character name")
    is_main_cast: bool = Field(False, description="Whether main cast member")
    cast_order: int = Field(0, description="Billing order")
    character_image_url: Optional[str] = Field(None, description="Poster image URL")

    class Config:
        from_attributes = True


class CrewMember(BaseModel):
    """Crew member schema for content detail"""

    person: PersonSimple = Field(..., description="Person information")
    job_title: str = Field(..., description="Job title (Director, Writer, etc.)")
    department: str = Field(..., description="Department (Directing, Writing, etc.)")
    credit_order: int = Field(0, description="Credit order")

    class Config:
        from_attributes = True


class ContentBase(BaseModel):
    """Base content schema"""

    title: str = Field(..., description="Content title")
    slug: str = Field(..., description="Content slug")
    description: Optional[str] = Field(None, description="Content description")
    tagline: Optional[str] = Field(None, description="Content tagline")
    content_type: ContentType = Field(..., description="Type of content")
    status: ContentStatus = Field(..., description="Content status")
    rating: ContentRating = Field(
        ..., alias="content_rating", description="Content rating"
    )
    release_date: Optional[date] = Field(None, description="Release date")
    duration_minutes: Optional[int] = Field(
        None, alias="runtime", description="Duration in minutes"
    )
    imdb_id: Optional[str] = Field(None, description="IMDB ID")
    tmdb_id: Optional[int] = Field(None, description="TMDB ID")
    is_featured: bool = Field(False, description="Whether content is featured")
    is_trending: bool = Field(False, description="Whether content is trending")
    view_count: int = Field(0, alias="total_views", description="Total view count")
    like_count: int = Field(0, alias="likes_count", description="Total like count")
    average_rating: Optional[float] = Field(None, description="Average user rating")
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    backdrop_url: Optional[str] = Field(None, description="Backdrop image URL")
    trailer_url: Optional[str] = Field(None, description="Trailer video URL")


class ContentCreate(ContentBase):
    """Schema for creating content"""

    pass


class ContentUpdate(BaseModel):
    """Schema for updating content"""

    title: Optional[str] = Field(None, description="Content title")
    slug: Optional[str] = Field(None, description="Content slug")
    description: Optional[str] = Field(None, description="Content description")
    tagline: Optional[str] = Field(None, description="Content tagline")
    content_type: Optional[ContentType] = Field(None, description="Type of content")
    status: Optional[ContentStatus] = Field(None, description="Content status")
    rating: Optional[ContentRating] = Field(None, description="Content rating")
    release_date: Optional[date] = Field(None, description="Release date")
    duration_minutes: Optional[int] = Field(
        None, alias="runtime", description="Duration in minutes"
    )
    imdb_id: Optional[str] = Field(None, description="IMDB ID")
    tmdb_id: Optional[int] = Field(None, description="TMDB ID")
    is_featured: Optional[bool] = Field(None, description="Whether content is featured")
    is_trending: Optional[bool] = Field(None, description="Whether content is trending")
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    backdrop_url: Optional[str] = Field(None, description="Backdrop image URL")
    trailer_url: Optional[str] = Field(None, description="Trailer video URL")


class Content(ContentBase):
    """Content response schema"""

    id: UUID = Field(..., description="Content ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_deleted: bool = Field(False, description="Whether content is deleted")
    genres: List[Genre] = Field(default_factory=list, description="Content genres")

    class Config:
        from_attributes = True


class MovieFileSimple(BaseModel):
    """Simplified movie file schema"""

    id: UUID = Field(..., description="Movie file ID")
    quality_level: str = Field(..., description="Quality level (1080p, 720p, etc.)")
    resolution_width: int = Field(..., description="Video width in pixels")
    resolution_height: int = Field(..., description="Video height in pixels")
    file_url: str = Field(..., description="File URL")
    file_size_bytes: Optional[int] = Field(None, description="File size in bytes")
    duration_seconds: float = Field(..., description="Duration in seconds")
    bitrate_kbps: Optional[int] = Field(None, description="Bitrate in kbps")
    video_codec: Optional[str] = Field(None, description="Video codec")
    audio_codec: Optional[str] = Field(None, description="Audio codec")
    container_format: Optional[str] = Field(None, description="Container format")
    is_ready: bool = Field(True, description="Whether file is ready for streaming")

    class Config:
        from_attributes = True


class EpisodeQualitySimple(BaseModel):
    """Simplified episode quality schema"""

    id: UUID = Field(..., description="Episode quality ID")
    quality_level: str = Field(..., description="Quality level (1080p, 720p, etc.)")
    resolution_width: int = Field(..., description="Video width in pixels")
    resolution_height: int = Field(..., description="Video height in pixels")
    file_url: str = Field(..., description="File URL")
    file_size_bytes: Optional[int] = Field(None, description="File size in bytes")
    duration_seconds: Optional[float] = Field(None, description="Duration in seconds")
    bitrate_kbps: Optional[int] = Field(None, description="Bitrate in kbps")
    video_codec: Optional[str] = Field(None, description="Video codec")
    is_ready: bool = Field(True, description="Whether file is ready for streaming")

    class Config:
        from_attributes = True


class EpisodeSimple(BaseModel):
    """Simplified episode schema for TV series"""

    id: UUID = Field(..., description="Episode ID")
    episode_number: int = Field(..., description="Episode number")
    title: str = Field(..., description="Episode title")
    slug: str = Field(..., description="Episode slug")
    description: Optional[str] = Field(None, description="Episode description")
    runtime: Optional[int] = Field(None, description="Runtime in minutes")
    air_date: Optional[date] = Field(None, description="Air date")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    views_count: int = Field(0, description="View count")
    is_available: bool = Field(True, description="Whether episode is available")
    quality_versions: List[EpisodeQualitySimple] = Field(
        default_factory=list, description="Available quality versions"
    )

    class Config:
        from_attributes = True


class SeasonSimple(BaseModel):
    """Simplified season schema for TV series"""

    id: UUID = Field(..., description="Season ID")
    season_number: int = Field(..., description="Season number")
    title: Optional[str] = Field(None, description="Season title")
    description: Optional[str] = Field(None, description="Season description")
    poster_url: Optional[str] = Field(None, description="Season poster URL")
    air_date: Optional[date] = Field(None, description="Air date")
    episode_count: int = Field(0, description="Number of episodes")
    total_duration_minutes: Optional[int] = Field(
        None, description="Total season duration in minutes"
    )
    average_episode_duration: Optional[float] = Field(
        None, description="Average episode duration in minutes"
    )
    is_complete: bool = Field(False, description="Whether season is complete")
    episodes: List[EpisodeSimple] = Field(
        default_factory=list, description="Season episodes"
    )

    class Config:
        from_attributes = True


class SeasonListSimple(BaseModel):
    """Simplified season schema for list views (no episodes)"""

    id: UUID = Field(..., description="Season ID")
    season_number: int = Field(..., description="Season number")
    title: Optional[str] = Field(None, description="Season title")
    description: Optional[str] = Field(None, description="Season description")
    poster_url: Optional[str] = Field(None, description="Season poster URL")
    air_date: Optional[date] = Field(None, description="Air date")
    episode_count: int = Field(0, description="Number of episodes")
    total_duration_minutes: Optional[int] = Field(
        None, description="Total season duration in minutes"
    )
    average_episode_duration: Optional[float] = Field(
        None, description="Average episode duration in minutes"
    )
    is_complete: bool = Field(False, description="Whether season is complete")

    class Config:
        from_attributes = True


class CastCrewResponse(BaseModel):
    """Response schema for cast and crew APIs"""

    cast: List[CastMember] = Field(default_factory=list, description="Cast members")
    crew: List[CrewMember] = Field(default_factory=list, description="Crew members")
    total_cast: int = Field(0, description="Total number of cast members")
    total_crew: int = Field(0, description="Total number of crew members")

    class Config:
        from_attributes = True


class ContentDetail(BaseModel):
    """Simplified content detail schema - no cast/crew"""

    # Basic Information
    id: UUID = Field(..., description="Content ID")
    title: str = Field(..., description="Content title")
    slug: str = Field(..., description="Content slug")
    description: Optional[str] = Field(None, description="Content description")
    tagline: Optional[str] = Field(None, description="Content tagline")

    # Content Classification
    content_type: ContentType = Field(..., description="Type of content")
    status: ContentStatus = Field(..., description="Content status")
    content_rating: Optional[ContentRating] = Field(None, description="Content rating")

    # Visual Assets
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    backdrop_url: Optional[str] = Field(None, description="Backdrop image URL")
    trailer_url: Optional[str] = Field(None, description="Trailer video URL")

    # Release Information
    release_date: Optional[date] = Field(None, description="Release date")
    duration_minutes: Optional[int] = Field(
        None, alias="runtime", description="Duration in minutes"
    )

    # Statistics
    view_count: int = Field(0, alias="total_views", description="Total view count")
    like_count: int = Field(0, alias="likes_count", description="Total like count")
    average_rating: Optional[float] = Field(None, description="Average user rating")

    # Flags
    is_featured: bool = Field(False, description="Whether content is featured")
    is_trending: bool = Field(False, description="Whether content is trending")

    # Relationships
    genres: List[GenreSimple] = Field(
        default_factory=list, description="Content genres"
    )
    # Content type specific data
    movie_files: List[MovieFileSimple] = Field(
        default_factory=list, description="Movie files (for movies)"
    )
    seasons: List[SeasonSimple] = Field(
        default_factory=list, description="Seasons (for TV series)"
    )

    # Metadata
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class ContentList(BaseModel):
    """Content list response schema"""

    id: UUID = Field(..., description="Content ID")
    title: str = Field(..., description="Content title")
    slug: str = Field(..., description="Content slug")
    content_type: ContentType = Field(..., description="Type of content")
    status: ContentStatus = Field(..., description="Content status")
    content_rating: ContentRating = Field(..., description="Content rating")
    release_date: Optional[date] = Field(None, description="Release date")
    duration_minutes: Optional[int] = Field(
        None, alias="runtime", description="Duration in minutes"
    )
    is_featured: bool = Field(False, description="Whether content is featured")
    is_trending: bool = Field(False, description="Whether content is trending")
    view_count: int = Field(0, alias="total_views", description="Total view count")
    like_count: int = Field(0, alias="likes_count", description="Total like count")
    average_rating: Optional[float] = Field(None, description="Average user rating")
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    backdrop_url: Optional[str] = Field(None, description="Backdrop image URL")
    trailer_url: Optional[str] = Field(None, description="Trailer URL")
    genres: List[Genre] = Field(default_factory=list, description="Content genres")

    # Content type specific data for list view
    movie_files: List[MovieFileSimple] = Field(
        default_factory=list, description="Movie files (for movies)"
    )
    seasons: List[SeasonListSimple] = Field(
        default_factory=list, description="Seasons (for TV series)"
    )

    class Config:
        from_attributes = True


class PaginationParams(BaseModel):
    """Pagination parameters"""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
    sort_by: Optional[str] = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")


class PaginatedResponse(BaseModel):
    """Paginated response schema"""

    items: List[dict] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class ContentListResponse(BaseModel):
    """Response schema for content list endpoints"""

    items: List[ContentList] = Field(..., description="List of content items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class GenreListResponse(BaseModel):
    """Response schema for genre list endpoints"""

    items: List[Genre] = Field(..., description="List of genre items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class ContentFilters(BaseModel):
    """Content filtering parameters"""

    content_type: Optional[ContentType] = Field(
        None, description="Filter by content type"
    )
    status: Optional[ContentStatus] = Field(None, description="Filter by status")
    rating: Optional[ContentRating] = Field(None, description="Filter by rating")
    genre_ids: Optional[List[UUID]] = Field(None, description="Filter by genre IDs")
    is_featured: Optional[bool] = Field(None, description="Filter featured content")
    is_trending: Optional[bool] = Field(None, description="Filter trending content")
    is_new_release: Optional[bool] = Field(
        None, description="Filter new releases (last 30 days)"
    )
    year: Optional[int] = Field(None, description="Filter by release year")
    search: Optional[str] = Field(None, description="Search in title and description")


class ContentQueryParams(BaseModel):
    """Query parameters for content list endpoint"""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")
    content_type: Optional[ContentType] = Field(
        None, description="Filter by content type"
    )
    status: Optional[ContentStatus] = Field(None, description="Filter by status")
    rating: Optional[ContentRating] = Field(None, description="Filter by rating")
    genre_ids: Optional[str] = Field(None, description="Comma-separated genre IDs")
    is_featured: Optional[bool] = Field(None, description="Filter featured content")
    is_trending: Optional[bool] = Field(None, description="Filter trending content")
    is_new_release: Optional[bool] = Field(
        None, description="Filter new releases (last 30 days)"
    )
    year: Optional[int] = Field(None, description="Filter by release year")
    search: Optional[str] = Field(None, description="Search in title and description")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    def to_filters(self) -> ContentFilters:
        """Convert to ContentFilters, handling genre_ids parsing"""
        genre_id_list = None
        if self.genre_ids:
            try:
                genre_id_list = [UUID(gid.strip()) for gid in self.genre_ids.split(",")]
            except ValueError:
                raise ValueError("Invalid genre IDs format")

        return ContentFilters(
            content_type=self.content_type,
            status=self.status,
            rating=self.rating,
            genre_ids=genre_id_list,
            is_featured=self.is_featured,
            is_trending=self.is_trending,
            is_new_release=self.is_new_release,
            year=self.year,
            search=self.search,
        )

    def to_pagination(self) -> PaginationParams:
        """Convert to PaginationParams"""
        return PaginationParams(
            page=self.page,
            size=self.size,
            sort_by=self.sort_by,
            sort_order=self.sort_order,
        )


class FeaturedContentQueryParams(BaseModel):
    """Query parameters for featured content endpoint"""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")
    content_type: Optional[ContentType] = Field(
        None, description="Filter by content type"
    )
    rating: Optional[ContentRating] = Field(None, description="Filter by rating")
    genre_ids: Optional[str] = Field(None, description="Comma-separated genre IDs")
    is_new_release: Optional[bool] = Field(
        None, description="Filter new releases (last 30 days)"
    )
    year: Optional[int] = Field(None, description="Filter by release year")
    search: Optional[str] = Field(None, description="Search in title and description")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    def to_filters(self) -> ContentFilters:
        """Convert to ContentFilters, handling genre_ids parsing"""
        genre_id_list = None
        if self.genre_ids:
            try:
                genre_id_list = [UUID(gid.strip()) for gid in self.genre_ids.split(",")]
            except ValueError:
                raise ValueError("Invalid genre IDs format")

        return ContentFilters(
            content_type=self.content_type,
            rating=self.rating,
            genre_ids=genre_id_list,
            is_new_release=self.is_new_release,
            year=self.year,
            search=self.search,
            is_featured=True,  # Always true for featured content
        )

    def to_pagination(self) -> PaginationParams:
        """Convert to PaginationParams"""
        return PaginationParams(
            page=self.page,
            size=self.size,
            sort_by=self.sort_by,
            sort_order=self.sort_order,
        )


class TrendingContentQueryParams(BaseModel):
    """Query parameters for trending content endpoint"""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")
    content_type: Optional[ContentType] = Field(
        None, description="Filter by content type"
    )
    rating: Optional[ContentRating] = Field(None, description="Filter by rating")
    genre_ids: Optional[str] = Field(None, description="Comma-separated genre IDs")
    is_new_release: Optional[bool] = Field(
        None, description="Filter new releases (last 30 days)"
    )
    year: Optional[int] = Field(None, description="Filter by release year")
    search: Optional[str] = Field(None, description="Search in title and description")
    sort_by: str = Field("view_count", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    def to_filters(self) -> ContentFilters:
        """Convert to ContentFilters, handling genre_ids parsing"""
        genre_id_list = None
        if self.genre_ids:
            try:
                genre_id_list = [UUID(gid.strip()) for gid in self.genre_ids.split(",")]
            except ValueError:
                raise ValueError("Invalid genre IDs format")

        return ContentFilters(
            content_type=self.content_type,
            rating=self.rating,
            genre_ids=genre_id_list,
            is_new_release=self.is_new_release,
            year=self.year,
            search=self.search,
            is_trending=True,  # Always true for trending content
        )

    def to_pagination(self) -> PaginationParams:
        """Convert to PaginationParams"""
        return PaginationParams(
            page=self.page,
            size=self.size,
            sort_by=self.sort_by,
            sort_order=self.sort_order,
        )


class MostReviewedLastMonthQueryParams(BaseModel):
    """Query parameters for most reviewed last month endpoint"""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")
    content_type: Optional[ContentType] = Field(
        None, description="Filter by content type"
    )
    rating: Optional[ContentRating] = Field(None, description="Filter by rating")
    genre_ids: Optional[str] = Field(None, description="Comma-separated genre IDs")
    min_rating: Optional[float] = Field(
        3.0, ge=0.0, le=5.0, description="Minimum average rating"
    )
    min_reviews: Optional[int] = Field(5, ge=0, description="Minimum reviews count")
    year: Optional[int] = Field(None, description="Filter by release year")
    search: Optional[str] = Field(None, description="Search in title and description")
    sort_by: str = Field("reviews_count", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    def to_filters(self) -> ContentFilters:
        """Convert to ContentFilters, handling genre_ids parsing"""
        genre_id_list = None
        if self.genre_ids:
            try:
                genre_id_list = [UUID(gid.strip()) for gid in self.genre_ids.split(",")]
            except ValueError:
                raise ValueError("Invalid genre IDs format")

        return ContentFilters(
            content_type=self.content_type,
            rating=self.rating,
            genre_ids=genre_id_list,
            year=self.year,
            search=self.search,
        )

    def to_pagination(self) -> PaginationParams:
        """Convert to PaginationParams"""
        return PaginationParams(
            page=self.page,
            size=self.size,
            sort_by=self.sort_by,
            sort_order=self.sort_order,
        )


class GenreFilters(BaseModel):
    """Genre filtering parameters"""

    is_active: Optional[bool] = Field(None, description="Filter by active status")
    search: Optional[str] = Field(None, description="Search in name and description")


class CastListResponse(BaseModel):
    """Response schema for cast list with pagination"""

    items: List[CastMember] = Field(..., description="List of cast members")
    total: int = Field(..., description="Total number of cast members")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class CrewListResponse(BaseModel):
    """Response schema for crew list with pagination"""

    items: List[CrewMember] = Field(..., description="List of crew members")
    total: int = Field(..., description="Total number of crew members")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class CastFilters(BaseModel):
    """Filters for cast queries"""

    is_main_cast: Optional[bool] = Field(None, description="Filter by main cast status")
    search: Optional[str] = Field(
        None, description="Search in character name or person name"
    )
    department: Optional[str] = Field(None, description="Filter by department")


class CrewFilters(BaseModel):
    """Filters for crew queries"""

    department: Optional[str] = Field(None, description="Filter by department")
    job_title: Optional[str] = Field(None, description="Filter by job title")
    search: Optional[str] = Field(
        None, description="Search in job title or person name"
    )


class ReviewUser(BaseModel):
    """Simplified user schema for reviews"""

    id: UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    avatar_url: Optional[str] = Field(None, description="Profile image URL")
    is_verified: bool = Field(False, description="Whether user is verified")

    class Config:
        from_attributes = True


class ReviewBase(BaseModel):
    """Base review schema"""

    rating: float = Field(..., ge=1.0, le=5.0, description="Rating (1.0-5.0)")
    title: Optional[str] = Field(None, description="Review title")
    review_text: Optional[str] = Field(None, description="Review text")
    language: str = Field("en", description="Review language")
    is_featured: bool = Field(False, description="Whether review is featured")
    helpful_votes: int = Field(0, description="Number of helpful votes")
    total_votes: int = Field(0, description="Total number of votes")
    is_edited: bool = Field(False, description="Whether review was edited")
    last_edited_at: Optional[datetime] = Field(None, description="Last edit timestamp")


class ReviewCreate(BaseModel):
    """Schema for creating a review - user-facing only"""

    rating: float = Field(..., ge=1.0, le=5.0, description="Rating (1.0-5.0)")
    title: Optional[str] = Field(None, description="Review title")
    review_text: Optional[str] = Field(None, description="Review text")
    language: str = Field("en", description="Review language")


class ReviewUpdate(BaseModel):
    """Schema for updating a review - user-facing only"""

    rating: Optional[float] = Field(
        None, ge=1.0, le=5.0, description="Rating (1.0-5.0)"
    )
    title: Optional[str] = Field(None, description="Review title")
    review_text: Optional[str] = Field(None, description="Review text")
    language: Optional[str] = Field(None, description="Review language")


class Review(ReviewBase):
    """Review response schema"""

    id: UUID = Field(..., description="Review ID")
    content_id: UUID = Field(..., description="Content ID")
    user_id: UUID = Field(..., description="User ID")
    status: str = Field(..., description="Review status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    user: ReviewUser = Field(..., description="Review author")

    class Config:
        from_attributes = True


class ReviewSimple(BaseModel):
    """Simplified review schema for lists"""

    id: UUID = Field(..., description="Review ID")
    rating: float = Field(..., description="Rating (1.0-5.0)")
    title: Optional[str] = Field(None, description="Review title")
    review_text: Optional[str] = Field(None, description="Review text")
    language: str = Field(..., description="Review language")
    is_featured: bool = Field(False, description="Whether review is featured")
    helpful_votes: int = Field(0, description="Number of helpful votes")
    total_votes: int = Field(0, description="Total number of votes")
    is_edited: bool = Field(False, description="Whether review was edited")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_edited_at: Optional[datetime] = Field(None, description="Last edit timestamp")
    user: ReviewUser = Field(..., description="Review author")

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """Response schema for review list with pagination"""

    items: List[ReviewSimple] = Field(..., description="List of reviews")
    total: int = Field(..., description="Total number of reviews")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class ReviewFilters(BaseModel):
    """Filters for review queries"""

    rating_min: Optional[float] = Field(
        None, ge=1.0, le=5.0, description="Minimum rating"
    )
    rating_max: Optional[float] = Field(
        None, ge=1.0, le=5.0, description="Maximum rating"
    )
    is_featured: Optional[bool] = Field(None, description="Filter by featured status")
    language: Optional[str] = Field(None, description="Filter by language")
    search: Optional[str] = Field(None, description="Search in title or review text")
    user_id: Optional[UUID] = Field(None, description="Filter by specific user")


class ReviewStats(BaseModel):
    """Review statistics for content"""

    total_reviews: int = Field(0, description="Total number of reviews")
    average_rating: Optional[float] = Field(None, description="Average rating")
    rating_distribution: dict = Field(
        default_factory=dict, description="Rating distribution"
    )
    featured_reviews_count: int = Field(0, description="Number of featured reviews")
    recent_reviews_count: int = Field(
        0, description="Number of recent reviews (last 30 days)"
    )


class ContentReviewsResponse(BaseModel):
    """Response schema for content reviews with statistics"""

    content_id: UUID = Field(..., description="Content ID")
    reviews: List[ReviewSimple] = Field(..., description="List of reviews")
    stats: ReviewStats = Field(..., description="Review statistics")
    pagination: dict = Field(..., description="Pagination information")


class ReviewVoteRequest(BaseModel):
    """Schema for voting on a review"""

    is_helpful: bool = Field(..., description="Whether the review is helpful")


class ReviewVoteResponse(BaseModel):
    """Response schema for review vote"""

    message: str = Field(..., description="Success message")
    review_id: UUID = Field(..., description="Review ID")
    helpful_votes: int = Field(..., description="Number of helpful votes")
    total_votes: int = Field(..., description="Total number of votes")


class ReviewCreateResponse(BaseModel):
    """Response schema for review creation"""

    message: str = Field(..., description="Success message")
    review: Review = Field(..., description="Created review")


class ReviewUpdateResponse(BaseModel):
    """Response schema for review update"""

    message: str = Field(..., description="Success message")
    review: Review = Field(..., description="Updated review")


class ReviewDeleteResponse(BaseModel):
    """Response schema for review deletion"""

    message: str = Field(..., description="Success message")
    review_id: UUID = Field(..., description="Deleted review ID")


# Content Discovery Schemas - Optimized for Frontend Performance
class GenreMinimal(BaseModel):
    """Minimal genre data for content discovery"""

    id: UUID = Field(..., description="Genre ID")
    name: str = Field(..., description="Genre name")
    slug: str = Field(..., description="Genre slug")
    cover_image_url: Optional[str] = Field(None, description="Genre icon URL")

    class Config:
        from_attributes = True


class MovieFileMinimal(BaseModel):
    """Minimal movie file data for discovery API"""

    id: UUID = Field(..., description="Movie file ID")
    quality_level: str = Field(..., description="Quality level (1080p, 720p, etc.)")
    file_url: str = Field(..., description="File URL")
    duration_seconds: float = Field(..., description="Duration in seconds")
    is_ready: bool = Field(True, description="Whether file is ready for streaming")

    class Config:
        from_attributes = True


class EpisodeMinimal(BaseModel):
    """Minimal episode data for TV series discovery API"""

    id: UUID = Field(..., description="Episode ID")
    episode_number: int = Field(..., description="Episode number")
    title: str = Field(..., description="Episode title")
    slug: str = Field(..., description="Episode slug")
    description: Optional[str] = Field(None, description="Episode description")
    runtime: Optional[int] = Field(None, description="Runtime in minutes")
    air_date: Optional[date] = Field(None, description="Air date")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    views_count: int = Field(0, description="View count")
    is_available: bool = Field(True, description="Whether episode is available")

    class Config:
        from_attributes = True


class ContentMinimal(BaseModel):
    """Minimal content data for fast loading"""

    id: UUID = Field(..., description="Content ID")
    title: str = Field(..., description="Content title")
    slug: str = Field(..., description="Content slug")
    description: Optional[str] = Field(None, description="Short description")
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    backdrop_url: Optional[str] = Field(None, description="Backdrop image URL")
    release_date: Optional[datetime] = Field(None, description="Release date")
    content_type: str = Field(..., description="Content type (movie, tv_series, etc.)")
    content_rating: Optional[str] = Field(
        None, description="Content rating (PG, R, etc.)"
    )
    runtime: Optional[int] = Field(None, description="Runtime in minutes")
    average_rating: Optional[float] = Field(None, description="Average user rating")
    total_reviews: int = Field(0, description="Total number of reviews")
    total_views: int = Field(0, description="Total view count")
    is_featured: bool = Field(False, description="Is featured content")
    is_trending: bool = Field(False, description="Is trending content")
    # For movies: movie files
    movie_files: List[MovieFileMinimal] = Field(
        default_factory=list, description="Available movie files"
    )
    # For TV series: first episode of each season
    episode_files: List[EpisodeMinimal] = Field(
        default_factory=list, description="First episodes of each season"
    )

    class Config:
        from_attributes = True


class ContentSection(BaseModel):
    """Content section with pagination"""

    section_name: str = Field(
        ..., description="Section name (featured, trending, etc.)"
    )
    items: List[ContentMinimal] = Field(
        default_factory=list, description="Content items"
    )
    total_items: int = Field(0, description="Total items in section")
    has_more: bool = Field(False, description="Whether there are more items")
    next_page: Optional[int] = Field(
        None, description="Next page number if has_more is true"
    )

    class Config:
        from_attributes = True


class ContentDiscoveryResponse(BaseModel):
    """Main response for content discovery API"""

    sections: List[ContentSection] = Field(..., description="Content sections")
    genres: List[GenreMinimal] = Field(
        default_factory=list, description="All available genres"
    )
    total_sections: int = Field(..., description="Total number of sections")
    page: int = Field(1, description="Current page")
    size: int = Field(10, description="Items per section")
    generated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Response generation time"
    )

    class Config:
        from_attributes = True


class ContentDiscoveryQueryParams(BaseModel):
    """Query parameters for content discovery API"""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=50, description="Items per section")
    content_type: Optional[ContentType] = Field(
        None, description="Filter by content type"
    )
    genre_id: Optional[UUID] = Field(None, description="Filter by genre ID")
    include_featured: bool = Field(True, description="Include featured section")
    include_trending: bool = Field(True, description="Include trending section")
    include_most_reviewed: bool = Field(
        True, description="Include most reviewed section"
    )
    include_new_releases: bool = Field(True, description="Include new releases section")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 10,
                "content_type": "movie",
                "include_featured": True,
                "include_trending": True,
                "include_most_reviewed": True,
                "include_new_releases": True,
            }
        }
