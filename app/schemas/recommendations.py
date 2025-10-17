from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    """Individual recommendation item"""
    content_id: UUID
    title: str
    slug: str
    content_type: str
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    release_date: Optional[str] = None
    runtime: Optional[int] = None
    platform_rating: Optional[float] = None
    imdb_rating: Optional[float] = None
    description: Optional[str] = None
    genres: List[str] = []
    recommendation_score: float = Field(..., ge=0.0, le=1.0, description="Recommendation confidence score")
    recommendation_reason: str = Field(..., description="Why this content was recommended")


class RecommendationResponse(BaseModel):
    """Response model for user recommendations"""
    user_id: UUID
    recommendations: List[RecommendationItem]
    total_recommendations: int
    recommendation_type: str = Field(default="hardcoded", description="Type of recommendation algorithm used")
    generated_at: str = Field(..., description="Timestamp when recommendations were generated")
    message: str = Field(default="Recommendations generated successfully")


class RecommendationQueryParams(BaseModel):
    """Query parameters for recommendation requests"""
    limit: int = Field(default=10, ge=1, le=50, description="Number of recommendations to return")
    content_type: Optional[str] = Field(default=None, description="Filter by content type (movie, tv_series, etc.)")
    genre: Optional[str] = Field(default=None, description="Filter by genre")
    min_rating: Optional[float] = Field(default=None, ge=0.0, le=5.0, description="Minimum rating filter")
    max_runtime: Optional[int] = Field(default=None, ge=1, description="Maximum runtime in minutes")
