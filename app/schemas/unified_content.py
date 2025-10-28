"""
Unified Content Schemas

This module contains unified schemas for content items across all home screen APIs
to ensure consistency and prevent frontend integration issues.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class UnifiedContentItem(BaseModel):
    """Unified schema for all content items across home screen APIs."""
    id: str = Field(..., description="Content ID")
    title: str = Field(..., description="Content title")
    slug: str = Field(..., description="Content slug for URLs")
    content_type: str = Field(..., description="Type of content (movie, tv_series)")
    poster_url: str = Field(default="", description="Poster image URL")
    backdrop_url: str = Field(default="", description="Backdrop image URL")
    thumbnail_url: str = Field(default="", description="Thumbnail image URL")
    description: Optional[str] = Field(None, description="Content description")
    release_date: Optional[str] = Field(None, description="Release date in ISO format")
    platform_rating: float = Field(default=0.0, description="Platform rating (0.0-10.0)")
    platform_votes: int = Field(default=0, description="Number of platform votes")
    is_featured: bool = Field(default=False, description="Whether content is featured")
    is_trending: bool = Field(default=False, description="Whether content is trending")
    
    # Additional fields for different contexts
    current_position_seconds: Optional[int] = Field(None, description="Current watch position (for continue watching)")
    total_duration_seconds: Optional[int] = Field(None, description="Total duration (for continue watching)")
    progress_percentage: Optional[float] = Field(None, description="Watch progress percentage")
    last_watched_at: Optional[datetime] = Field(None, description="Last watched timestamp")
    episode_title: Optional[str] = Field(None, description="Episode title (for TV shows)")
    season_number: Optional[int] = Field(None, description="Season number (for TV shows)")
    episode_number: Optional[int] = Field(None, description="Episode number (for TV shows)")
    recommendation_score: Optional[float] = Field(None, description="Recommendation score (0.0-1.0)")
    recommendation_reason: Optional[str] = Field(None, description="Why this content is recommended")
    
    class Config:
        from_attributes = True


class ContentSection(BaseModel):
    """Unified schema for content sections."""
    section_id: str = Field(..., description="Unique section identifier")
    title: str = Field(..., description="Section title")
    items: List[UnifiedContentItem] = Field(..., description="Content items in section")
    total_items: int = Field(..., description="Total items available")
    has_more: bool = Field(..., description="Whether more items are available")
    view_all_route: str = Field(..., description="Route to view all items")
    page: int = Field(default=1, description="Current page number")
    size: int = Field(default=10, description="Items per page")
    
    class Config:
        from_attributes = True


class CategoryItem(BaseModel):
    """Schema for category navigation items."""
    id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="Category slug")
    description: Optional[str] = Field(None, description="Category description")
    icon_url: Optional[str] = Field(None, description="Category icon URL")
    content_count: int = Field(default=0, description="Number of items in category")
    
    class Config:
        from_attributes = True


class QuickNavItem(BaseModel):
    """Schema for quick navigation items."""
    id: str = Field(..., description="Navigation item ID")
    title: str = Field(..., description="Navigation title")
    icon: str = Field(..., description="Icon name")
    route: str = Field(..., description="Navigation route")
    badge_count: Optional[int] = Field(None, description="Badge count for notifications")
    
    class Config:
        from_attributes = True


class HeroDataResponse(BaseModel):
    """Unified response for hero data."""
    hero_slider: List[UnifiedContentItem] = Field(..., description="Featured content for hero slider")
    categories: List[CategoryItem] = Field(..., description="Available content categories")
    quick_nav: List[QuickNavItem] = Field(..., description="Quick navigation items")
    total_hero_items: int = Field(..., description="Total hero slider items")
    total_categories: int = Field(..., description="Total categories")
    
    class Config:
        from_attributes = True


class ContentSectionsResponse(BaseModel):
    """Unified response for content sections."""
    trending: ContentSection = Field(..., description="Trending content section")
    top_rated: ContentSection = Field(..., description="Top rated content section")
    new_releases: ContentSection = Field(..., description="New releases section")
    continue_watching: List[UnifiedContentItem] = Field(..., description="Continue watching items")
    recommendations: List[UnifiedContentItem] = Field(..., description="Personalized recommendations")
    recently_added: ContentSection = Field(..., description="Recently added content section")
    genre_sections: List[ContentSection] = Field(..., description="Genre-specific sections")
    total_sections: int = Field(..., description="Total number of sections")
    
    class Config:
        from_attributes = True


class HomeScreenResponse(BaseModel):
    """Complete home screen response combining hero data and content sections."""
    hero_data: HeroDataResponse = Field(..., description="Hero data (slider, categories, nav)")
    content_sections: ContentSectionsResponse = Field(..., description="Content sections")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation timestamp")
    
    class Config:
        from_attributes = True
