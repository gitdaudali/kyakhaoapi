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


class ContentBase(BaseModel):
    """Base content schema"""

    title: str = Field(..., description="Content title")
    slug: str = Field(..., description="Content slug")
    description: Optional[str] = Field(None, description="Content description")
    tagline: Optional[str] = Field(None, description="Content tagline")
    content_type: ContentType = Field(..., description="Type of content")
    status: ContentStatus = Field(..., description="Content status")
    rating: ContentRating = Field(..., description="Content rating")
    release_date: Optional[date] = Field(None, description="Release date")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    imdb_id: Optional[str] = Field(None, description="IMDB ID")
    tmdb_id: Optional[int] = Field(None, description="TMDB ID")
    is_featured: bool = Field(False, description="Whether content is featured")
    is_trending: bool = Field(False, description="Whether content is trending")
    view_count: int = Field(0, description="Total view count")
    like_count: int = Field(0, description="Total like count")
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
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
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


class ContentList(BaseModel):
    """Content list response schema"""

    id: UUID = Field(..., description="Content ID")
    title: str = Field(..., description="Content title")
    slug: str = Field(..., description="Content slug")
    content_type: ContentType = Field(..., description="Type of content")
    status: ContentStatus = Field(..., description="Content status")
    content_rating: ContentRating = Field(..., description="Content rating")
    release_date: Optional[date] = Field(None, description="Release date")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    is_featured: bool = Field(False, description="Whether content is featured")
    is_trending: bool = Field(False, description="Whether content is trending")
    view_count: int = Field(0, description="Total view count")
    like_count: int = Field(0, description="Total like count")
    average_rating: Optional[float] = Field(None, description="Average user rating")
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    backdrop_url: Optional[str] = Field(None, description="Backdrop image URL")
    genres: List[Genre] = Field(default_factory=list, description="Content genres")

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
    year: Optional[int] = Field(None, description="Filter by release year")
    search: Optional[str] = Field(None, description="Search in title and description")


class GenreFilters(BaseModel):
    """Genre filtering parameters"""

    is_active: Optional[bool] = Field(None, description="Filter by active status")
    search: Optional[str] = Field(None, description="Search in name and description")
