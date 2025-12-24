"""
Schemas for dish recommendation API.
"""
from typing import Dict, List, Optional

import uuid
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Request schema for dish recommendations."""
    limit: int = Field(default=20, ge=1, le=100, description="Number of recommendations to return")
    cuisine_id: Optional[uuid.UUID] = Field(default=None, description="Filter by specific cuisine")
    restaurant_id: Optional[uuid.UUID] = Field(default=None, description="Filter by specific restaurant")
    min_score: Optional[float] = Field(default=0.0, ge=0.0, le=100.0, description="Minimum match score threshold")
    include_explanation: bool = Field(default=True, description="Include score breakdown in response")


class ScoreBreakdownResponse(BaseModel):
    """Score breakdown for a dish recommendation."""
    spice_level: float = Field(..., description="Spice level match score")
    cuisine_match: float = Field(..., description="Cuisine match score")
    budget_match: float = Field(..., description="Budget match score")
    dietary_tags: float = Field(..., description="Dietary tags match score")
    past_interactions: float = Field(..., description="Past interactions score")
    dish_rating: float = Field(..., description="Dish rating score")
    total: float = Field(..., description="Total match score")


class RecommendedDish(BaseModel):
    """A dish recommendation with match score."""
    dish_id: uuid.UUID = Field(..., description="Dish ID")
    name: str = Field(..., description="Dish name")
    description: Optional[str] = Field(default=None, description="Dish description")
    price: Optional[float] = Field(default=None, description="Dish price")
    rating: Optional[float] = Field(default=None, description="Dish rating")
    cuisine_id: uuid.UUID = Field(..., description="Cuisine ID")
    cuisine_name: Optional[str] = Field(default=None, description="Cuisine name")
    restaurant_id: uuid.UUID = Field(..., description="Restaurant ID")
    restaurant_name: Optional[str] = Field(default=None, description="Restaurant name")
    match_score: float = Field(..., ge=0.0, le=100.0, description="Match score (0-100)")
    score_breakdown: Optional[ScoreBreakdownResponse] = Field(default=None, description="Score breakdown")
    explanation: Optional[List[str]] = Field(default=None, description="Human-readable explanation")


class RecommendationResponse(BaseModel):
    """Response schema for dish recommendations."""
    recommendations: List[RecommendedDish] = Field(..., description="List of recommended dishes")
    total_count: int = Field(..., description="Total number of recommendations")
    user_id: uuid.UUID = Field(..., description="User ID")
    filters_applied: Dict[str, Optional[str]] = Field(..., description="Filters applied to the request")


class InteractionTrackRequest(BaseModel):
    """Request schema for tracking user interactions."""
    dish_id: uuid.UUID = Field(..., description="Dish ID")
    interaction_type: str = Field(..., description="Type of interaction: click, view, reservation, order, favorite, review")
    metadata: Optional[Dict[str, str]] = Field(default=None, description="Additional metadata about the interaction")


class InteractionTrackResponse(BaseModel):
    """Response schema for interaction tracking."""
    success: bool = Field(..., description="Whether the interaction was tracked successfully")
    interaction_id: uuid.UUID = Field(..., description="Interaction record ID")
    message: str = Field(..., description="Status message")

