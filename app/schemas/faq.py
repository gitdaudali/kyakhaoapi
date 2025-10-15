from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FAQResponse(BaseModel):
    """User response schema for FAQ"""

    id: UUID = Field(..., description="FAQ ID")
    question: str = Field(..., description="FAQ question")
    answer: str = Field(..., description="FAQ answer")
    category: Optional[str] = Field(None, description="FAQ category")
    is_featured: bool = Field(..., description="Whether FAQ is featured")
    sort_order: int = Field(..., description="Sort order")
    view_count: int = Field(..., description="View count")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class FAQListResponse(BaseModel):
    """Response schema for FAQ list"""

    items: List[FAQResponse] = Field(..., description="List of FAQs")
    total: int = Field(..., description="Total number of FAQs")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    class Config:
        from_attributes = True


class FAQQueryParams(BaseModel):
    """Query parameters for FAQ endpoints"""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")
    search: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Search term"
    )
    category: Optional[str] = Field(
        None, max_length=100, description="Filter by category"
    )
    featured_only: Optional[bool] = Field(
        None, description="Show only featured FAQs"
    )
    sort_by: str = Field("sort_order", description="Sort field")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="Sort order")

    class Config:
        from_attributes = True
