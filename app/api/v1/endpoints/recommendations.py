from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.recommendations import (
    RecommendationResponse,
    RecommendationQueryParams
)
from app.utils.recommendation_utils import (
    get_hardcoded_recommendations,
    get_trending_recommendations,
    get_similar_content_recommendations
)

router = APIRouter()


@router.get("/", response_model=RecommendationResponse)
async def get_user_recommendations(
    query_params: RecommendationQueryParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get personalized recommendations for the current user.
    Currently returns hardcoded recommendations, will be replaced with AI/ML models.
    """
    try:
        recommendations = get_hardcoded_recommendations(
            user_id=str(current_user.id),
            query_params=query_params
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get("/trending", response_model=RecommendationResponse)
async def get_trending_recommendations_endpoint(
    limit: int = Query(default=10, ge=1, le=50, description="Number of trending recommendations to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get trending content recommendations.
    Currently returns hardcoded trending content, will be replaced with AI/ML models.
    """
    try:
        recommendations = get_trending_recommendations(
            user_id=str(current_user.id),
            limit=limit
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating trending recommendations: {str(e)}"
        )


@router.get("/similar/{content_id}", response_model=RecommendationResponse)
async def get_similar_content_recommendations(
    content_id: UUID,
    limit: int = Query(default=5, ge=1, le=20, description="Number of similar content recommendations to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get recommendations for content similar to the specified content.
    Currently returns hardcoded similar content, will be replaced with AI/ML models.
    """
    try:
        recommendations = get_similar_content_recommendations(
            content_id=str(content_id),
            user_id=str(current_user.id),
            limit=limit
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating similar content recommendations: {str(e)}"
        )


@router.get("/genre/{genre_name}", response_model=RecommendationResponse)
async def get_genre_recommendations(
    genre_name: str,
    limit: int = Query(default=10, ge=1, le=50, description="Number of genre recommendations to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get recommendations for a specific genre.
    Currently returns hardcoded genre-based recommendations, will be replaced with AI/ML models.
    """
    try:
        query_params = RecommendationQueryParams(
            limit=limit,
            genre=genre_name
        )
        recommendations = get_hardcoded_recommendations(
            user_id=str(current_user.id),
            query_params=query_params
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating genre recommendations: {str(e)}"
        )


@router.get("/new-releases", response_model=RecommendationResponse)
async def get_new_releases_recommendations(
    limit: int = Query(default=10, ge=1, le=50, description="Number of new release recommendations to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get new release recommendations.
    Currently returns hardcoded new releases, will be replaced with AI/ML models.
    """
    try:
        # For now, return trending content as "new releases"
        recommendations = get_trending_recommendations(
            user_id=str(current_user.id),
            limit=limit
        )
        # Update the recommendation type
        recommendations.recommendation_type = "new_releases"
        recommendations.message = "New release recommendations generated successfully"
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating new release recommendations: {str(e)}"
        )
