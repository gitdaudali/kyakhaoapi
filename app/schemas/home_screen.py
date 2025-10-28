"""
Home Screen API Schemas

This module contains Pydantic schemas for the Home Screen API responses.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class HeroSliderItem(BaseModel):
    """Schema for hero slider/banner items."""
    id: str
    title: str
    slug: str
    content_type: str
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[str] = None
    platform_rating: Optional[float] = None
    is_featured: bool = False

    class Config:
        from_attributes = True


class CategoryItem(BaseModel):
    """Schema for category navigation items."""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    content_count: int = 0

    class Config:
        from_attributes = True


class QuickNavItem(BaseModel):
    """Schema for quick navigation items."""
    id: str
    title: str
    icon: str
    route: str
    badge_count: Optional[int] = None

    class Config:
        from_attributes = True


class HeroDataResponse(BaseModel):
    """Schema for hero data API response."""
    hero_slider: List[HeroSliderItem] = Field(..., description="Featured content for hero slider")
    categories: List[CategoryItem] = Field(..., description="Available content categories")
    quick_nav: List[QuickNavItem] = Field(..., description="Quick navigation items")
    total_hero_items: int = Field(..., description="Total number of hero slider items")
    total_categories: int = Field(..., description="Total number of categories")


class ContentSectionItem(BaseModel):
    """Schema for individual content items in sections."""
    id: str
    title: str
    slug: str
    content_type: str
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    release_date: Optional[str] = None
    platform_rating: Optional[float] = None
    platform_votes: int = 0
    description: Optional[str] = None
    is_featured: bool = False

    class Config:
        from_attributes = True


class ContentSection(BaseModel):
    """Schema for a content section (e.g., Trending, Top Rated)."""
    section_id: str = Field(..., description="Unique identifier for the section")
    title: str = Field(..., description="Section title")
    items: List[ContentSectionItem] = Field(..., description="Content items in this section")
    total_items: int = Field(..., description="Total items available in this section")
    has_more: bool = Field(..., description="Whether there are more items available")
    view_all_route: Optional[str] = Field(None, description="Route to view all items in this section")

    class Config:
        from_attributes = True


class ContinueWatchingItem(BaseModel):
    """Schema for continue watching items."""
    id: str
    title: str
    slug: str
    content_type: str
    poster_url: Optional[str] = None
    current_position_seconds: int = Field(..., description="Current watch position in seconds")
    total_duration_seconds: int = Field(..., description="Total content duration in seconds")
    progress_percentage: float = Field(..., description="Watch progress as percentage")
    last_watched_at: datetime
    episode_title: Optional[str] = None
    season_number: Optional[int] = None
    episode_number: Optional[int] = None

    class Config:
        from_attributes = True


class RecommendationItem(BaseModel):
    """Schema for personalized recommendation items."""
    id: str
    title: str
    slug: str
    content_type: str
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    release_date: Optional[str] = None
    platform_rating: Optional[float] = None
    recommendation_score: float = Field(..., description="AI recommendation score (0.0-1.0)")
    recommendation_reason: str = Field(..., description="Why this content is recommended")
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ContentSectionsResponse(BaseModel):
    """Schema for content sections API response."""
    trending: ContentSection = Field(..., description="Trending content section")
    top_rated: ContentSection = Field(..., description="Top rated content section")
    new_releases: ContentSection = Field(..., description="New releases section")
    continue_watching: List[ContinueWatchingItem] = Field(..., description="Continue watching items")
    recommendations: List[RecommendationItem] = Field(..., description="Personalized recommendations")
    recently_added: ContentSection = Field(..., description="Recently added content section")
    genre_sections: List[ContentSection] = Field(..., description="Genre-specific content sections")
    total_sections: int = Field(..., description="Total number of content sections")

    class Config:
        from_attributes = True
