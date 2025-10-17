from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.stats import (
    HoursWatchedResponse, 
    MoviesCompletedResponse, 
    TVEpisodesResponse, 
    FavoritesResponse
)
from app.utils.stats_utils import (
    get_user_hours_watched,
    get_user_movies_completed, 
    get_user_tv_episodes_watched,
    get_user_favorites_count
)

router = APIRouter()

@router.get("/hours-watched", response_model=HoursWatchedResponse)
async def get_hours_watched(
    period: str = "total",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's total hours watched"""
    try:
        hours = await get_user_hours_watched(current_user.id, db, period)
        return HoursWatchedResponse(
            hours=hours,
            period=period,
            message=f"Total hours watched: {hours}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching hours watched: {str(e)}"
        )

@router.get("/movies-completed", response_model=MoviesCompletedResponse)
async def get_movies_completed(
    period: str = "total",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's completed movies count"""
    try:
        count = await get_user_movies_completed(current_user.id, db, period)
        return MoviesCompletedResponse(
            movies_count=count,
            period=period,
            message=f"Movies completed: {count}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching movies completed: {str(e)}"
        )

@router.get("/tv-episodes-watched", response_model=TVEpisodesResponse)
async def get_tv_episodes_watched(
    period: str = "total",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's TV episodes watched count"""
    try:
        count = await get_user_tv_episodes_watched(current_user.id, db, period)
        return TVEpisodesResponse(
            episodes_count=count,
            period=period,
            message=f"TV episodes watched: {count}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching TV episodes: {str(e)}"
        )

@router.get("/favorites", response_model=FavoritesResponse)
async def get_favorites_count(
    period: str = "total",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's favorites count"""
    try:
        count = await get_user_favorites_count(current_user.id, db, period)
        return FavoritesResponse(
            favorites_count=count,
            period=period,
            message=f"Favorites saved: {count}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching favorites: {str(e)}"
        )
