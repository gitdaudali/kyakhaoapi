from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy import func, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.content import UserWatchHistory, UserContentInteraction, EpisodeView, Content, Episode
from app.models.user import User

async def get_user_hours_watched(user_id: UUID, db: AsyncSession, period: str = "total") -> float:
    """Calculate total hours watched by user"""
    # Get date filter based on period
    date_filter = get_date_filter(period)
    
    # Query to get total seconds watched
    query = select(func.sum(UserWatchHistory.current_position_seconds)).where(
        and_(
            UserWatchHistory.user_id == user_id,
            date_filter
        )
    )
    
    result = await db.execute(query)
    total_seconds = result.scalar() or 0
    
    # Convert seconds to hours
    return round(total_seconds / 3600, 2)

async def get_user_movies_completed(user_id: UUID, db: AsyncSession, period: str = "total") -> int:
    """Count completed movies for user"""
    date_filter = get_date_filter(period)
    
    # Get all completed watch history for user
    completed_history = await db.execute(
        select(UserWatchHistory).where(
            and_(
                UserWatchHistory.user_id == user_id,
                UserWatchHistory.is_completed == True,
                date_filter
            )
        )
    )
    
    # Filter for movies only
    movie_count = 0
    for history in completed_history.scalars():
        content = await db.get(Content, history.content_id)
        if content and content.content_type == "movie":
            movie_count += 1
    
    return movie_count

async def get_user_tv_episodes_watched(user_id: UUID, db: AsyncSession, period: str = "total") -> int:
    """Count TV episodes watched by user"""
    date_filter = get_date_filter(period)
    
    # Count from EpisodeView table
    query = select(func.count(EpisodeView.id)).where(
        and_(
            EpisodeView.viewer_id == user_id,
            date_filter
        )
    )
    
    result = await db.execute(query)
    return result.scalar() or 0

async def get_user_favorites_count(user_id: UUID, db: AsyncSession, period: str = "total") -> int:
    """Count user's favorite content"""
    date_filter = get_date_filter(period)
    
    query = select(func.count(UserContentInteraction.id)).where(
        and_(
            UserContentInteraction.user_id == user_id,
            UserContentInteraction.interaction_type == "favorite",
            date_filter
        )
    )
    
    result = await db.execute(query)
    return result.scalar() or 0

def get_date_filter(period: str):
    """Get date filter based on period"""
    now = datetime.utcnow()
    
    if period == "this_month":
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return UserWatchHistory.created_at >= start_of_month
    elif period == "last_month":
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = (start_of_month - timedelta(days=1)).replace(day=1)
        end_of_last_month = start_of_month - timedelta(days=1)
        return and_(
            UserWatchHistory.created_at >= start_of_last_month,
            UserWatchHistory.created_at <= end_of_last_month
        )
    else:  # total
        return True
