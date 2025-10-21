from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content import Content, Episode
from app.models.user import User
from app.models.watch_progress import UserWatchProgress


async def get_recently_watched_list(
    user_id: UUID,
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    content_type: Optional[str] = None,
    days_back: int = 30
) -> Tuple[List[UserWatchProgress], int]:
    """Get user's recently watched (completed) content"""
    
    # Calculate date filter
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    # Build query conditions
    conditions = [
        UserWatchProgress.user_id == user_id,
        UserWatchProgress.is_completed == True,  # Only completed content
        UserWatchProgress.last_watched_at >= cutoff_date
    ]
    
    # Add content type filter if specified
    if content_type:
        conditions.append(Content.content_type == content_type)
    
    # Get recently watched content
    query = select(UserWatchProgress).where(
        and_(*conditions)
    ).options(
        selectinload(UserWatchProgress.content),
        selectinload(UserWatchProgress.episode)
    ).order_by(desc(UserWatchProgress.last_watched_at))
    
    # Get total count
    count_query = select(func.count(UserWatchProgress.id)).where(
        and_(*conditions)
    )
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    result = await db.execute(query.offset(offset).limit(limit))
    progress_list = result.scalars().all()
    
    return progress_list, total


async def get_recently_watched_by_id(
    user_id: UUID,
    content_id: UUID,
    db: AsyncSession,
    episode_id: Optional[UUID] = None
) -> Optional[UserWatchProgress]:
    """Get specific recently watched content by ID"""
    
    query = select(UserWatchProgress).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.content_id == content_id,
            UserWatchProgress.episode_id == episode_id,
            UserWatchProgress.is_completed == True
        )
    ).options(
        selectinload(UserWatchProgress.content),
        selectinload(UserWatchProgress.episode)
    )
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_recently_watched_stats(
    user_id: UUID,
    db: AsyncSession,
    days_back: int = 30
) -> dict:
    """Get user's recently watched statistics"""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    # Total completed content
    total_completed_query = select(func.count(UserWatchProgress.id)).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == True,
            UserWatchProgress.last_watched_at >= cutoff_date
        )
    )
    
    # Total hours watched
    total_hours_query = select(func.sum(UserWatchProgress.total_duration_seconds)).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == True,
            UserWatchProgress.last_watched_at >= cutoff_date
        )
    )
    
    # Average completion time
    avg_completion_query = select(func.avg(UserWatchProgress.total_duration_seconds)).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == True,
            UserWatchProgress.last_watched_at >= cutoff_date
        )
    )
    
    # Most watched content type
    content_type_query = select(
        Content.content_type,
        func.count(UserWatchProgress.id).label('count')
    ).join(UserWatchProgress).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == True,
            UserWatchProgress.last_watched_at >= cutoff_date
        )
    ).group_by(Content.content_type).order_by(desc('count'))
    
    # Last completed at
    last_completed_query = select(func.max(UserWatchProgress.last_watched_at)).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == True
        )
    )
    
    # Completion streak (consecutive days with completions)
    streak_query = select(func.count(func.distinct(func.date(UserWatchProgress.last_watched_at)))).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == True,
            UserWatchProgress.last_watched_at >= cutoff_date
        )
    )
    
    # Execute all queries
    total_completed_result = await db.execute(total_completed_query)
    total_hours_result = await db.execute(total_hours_query)
    avg_completion_result = await db.execute(avg_completion_query)
    content_type_result = await db.execute(content_type_query)
    last_completed_result = await db.execute(last_completed_query)
    streak_result = await db.execute(streak_query)
    
    total_completed = total_completed_result.scalar() or 0
    total_seconds = total_hours_result.scalar() or 0
    total_hours = total_seconds / 3600
    avg_completion_seconds = avg_completion_result.scalar() or 0
    avg_completion_hours = avg_completion_seconds / 3600
    completion_streak = streak_result.scalar() or 0
    last_completed_at = last_completed_result.scalar()
    
    # Get most watched content type
    content_type_row = content_type_result.first()
    most_watched_type = content_type_row[0] if content_type_row else "movie"
    
    return {
        "total_completed_content": total_completed,
        "total_hours_watched": round(total_hours, 2),
        "average_completion_time": round(avg_completion_hours, 2),
        "most_watched_content_type": most_watched_type,
        "completion_streak_days": completion_streak,
        "last_completed_at": last_completed_at
    }


async def remove_from_recently_watched(
    user_id: UUID,
    content_id: UUID,
    db: AsyncSession,
    episode_id: Optional[UUID] = None
) -> bool:
    """Remove specific content from recently watched history"""
    query = select(UserWatchProgress).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.content_id == content_id,
            UserWatchProgress.is_completed == True,
            UserWatchProgress.episode_id == episode_id
        )
    )
    
    result = await db.execute(query)
    progress = result.scalar_one_or_none()
    
    if not progress:
        return False
    
    await db.delete(progress)
    await db.commit()
    return True


async def clear_all_recently_watched(
    user_id: UUID,
    db: AsyncSession
) -> int:
    """Clear all recently watched history for user"""
    query = select(UserWatchProgress).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == True
        )
    )
    
    result = await db.execute(query)
    progress_list = result.scalars().all()
    
    count = len(progress_list)
    
    for progress in progress_list:
        await db.delete(progress)
    
    await db.commit()
    return count


