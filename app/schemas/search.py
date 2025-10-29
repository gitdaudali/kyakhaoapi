from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.unified_content import UnifiedContentItem, CategoryItem


class SearchQueryParams(BaseModel):
    q: str = Field(..., min_length=2, max_length=100, description="Search query")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=50, description="Items per page")
    content_type: Optional[str] = Field(
        None, description="Filter by content type: movie, tv_series, episode"
    )


class SimpleContentItem(BaseModel):
    id: str
    title: str
    content_type: str
    poster_url: Optional[str] = None
    platform_rating: Optional[float] = None
    is_featured: bool = False
    is_trending: bool = False


class SearchGroupedResults(BaseModel):
    movies: List[SimpleContentItem] = Field(default_factory=list)
    tv_series: List[SimpleContentItem] = Field(default_factory=list)
    episodes: List[SimpleContentItem] = Field(default_factory=list)


class SearchSections(BaseModel):
    top_rated: List[SimpleContentItem] = Field(default_factory=list)
    trending: List[SimpleContentItem] = Field(default_factory=list)
    new_releases: List[SimpleContentItem] = Field(default_factory=list)
    categories: List[CategoryItem] = Field(default_factory=list)


class MainSearchResponse(BaseModel):
    query: str
    total_results: int
    page: int
    size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    results: SearchGroupedResults
    sections: SearchSections


