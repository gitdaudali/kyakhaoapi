"""
Content Categories Schemas

This module contains Pydantic schemas for content category API endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ContentCategoryItem(BaseModel):
    """Schema for individual content item in category listings"""
    
    id: str = Field(..., description="Content ID")
    title: str = Field(..., description="Content title")
    slug: str = Field(..., description="Content slug")
    content_type: str = Field(..., description="Content type (movie, tv_series)")
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    backdrop_url: Optional[str] = Field(None, description="Backdrop image URL")
    release_date: Optional[str] = Field(None, description="Release date")
    platform_rating: Optional[float] = Field(None, description="Platform rating")
    platform_votes: int = Field(0, description="Number of platform votes")
    description: Optional[str] = Field(None, description="Content description")
    
    class Config:
        from_attributes = True


class ContentCategoryResponse(BaseModel):
    """Schema for content category response with pagination"""
    
    category: str = Field(..., description="Category identifier")
    title: str = Field(..., description="Category display title")
    items: List[ContentCategoryItem] = Field(..., description="List of content items")
    total_items: int = Field(..., description="Total number of items across all pages")
    total_pages: int = Field(..., description="Total number of pages")
    current_page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    
    class Config:
        from_attributes = True
