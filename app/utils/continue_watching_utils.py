from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content import Content, Episode
from app.models.user import User
from app.models.watch_progress import UserWatchProgress


async def get_or_create_watch_progress(
    user_id: UUID,
    content_id: UUID,
    db: AsyncSession,
    episode_id: Optional[UUID] = None
) -> UserWatchProgress:
    """Get existing watch progress or create new one"""
    
    # Try to find existing progress
    query = select(UserWatchProgress).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.content_id == content_id,
            UserWatchProgress.episode_id == episode_id
        )
    )
    
    result = await db.execute(query)
    progress = result.scalar_one_or_none()
    
    if progress:
        return progress
    
    # Create new progress record
    progress = UserWatchProgress(
        user_id=user_id,
        content_id=content_id,
        episode_id=episode_id,
        current_position_seconds=0,
        total_duration_seconds=0,
        watch_percentage=0.0,
        is_completed=False,
        last_watched_at=datetime.utcnow()
    )
    
    db.add(progress)
    await db.commit()
    await db.refresh(progress)
    
    return progress


async def update_watch_progress(
    user_id: UUID,
    content_id: UUID,
    current_position_seconds: int,
    total_duration_seconds: int,
    db: AsyncSession,
    episode_id: Optional[UUID] = None
) -> UserWatchProgress:
    """Update user's watch progress for content"""
    
    # Calculate watch percentage
    watch_percentage = (current_position_seconds / total_duration_seconds) * 100 if total_duration_seconds > 0 else 0
    
    # Auto-complete when user reaches the end (within 5 seconds of total duration)
    is_completed = (total_duration_seconds - current_position_seconds) <= 5
    
    # Get or create progress record
    progress = await get_or_create_watch_progress(user_id, content_id, episode_id, db)
    
    # Update progress
    progress.current_position_seconds = current_position_seconds
    progress.total_duration_seconds = total_duration_seconds
    progress.watch_percentage = watch_percentage
    progress.is_completed = is_completed
    progress.last_watched_at = datetime.utcnow()
    progress.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(progress)
    
    return progress


async def get_continue_watching_list(
    user_id: UUID,
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0
) -> Tuple[List[UserWatchProgress], int]:
    """Get user's continue watching list"""
    
    # Get recent watch progress (not completed, any progress)
    query = select(UserWatchProgress).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == False,  # Only incomplete content
            UserWatchProgress.last_watched_at >= datetime.utcnow() - timedelta(days=30)  # Within last 30 days
        )
    ).options(
        selectinload(UserWatchProgress.content),
        selectinload(UserWatchProgress.episode)
    ).order_by(desc(UserWatchProgress.last_watched_at))
    
    # Get total count
    count_query = select(func.count(UserWatchProgress.id)).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == False,
            UserWatchProgress.last_watched_at >= datetime.utcnow() - timedelta(days=30)
        )
    )
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    result = await db.execute(query.offset(offset).limit(limit))
    progress_list = result.scalars().all()
    
    return progress_list, total


async def get_resume_position(
    user_id: UUID,
    content_id: UUID,
    db: AsyncSession,
    episode_id: Optional[UUID] = None
) -> Optional[UserWatchProgress]:
    """Get resume position for specific content"""
    
    query = select(UserWatchProgress).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.content_id == content_id,
            UserWatchProgress.episode_id == episode_id,
            UserWatchProgress.is_completed == False
        )
    )
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def mark_as_completed(
    user_id: UUID,
    content_id: UUID,
    db: AsyncSession,
    episode_id: Optional[UUID] = None
) -> bool:
    """Mark content as completed"""
    
    query = select(UserWatchProgress).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.content_id == content_id,
            UserWatchProgress.episode_id == episode_id
        )
    )
    
    result = await db.execute(query)
    progress = result.scalar_one_or_none()
    
    if not progress:
        return False
    
    progress.is_completed = True
    progress.watch_percentage = 100.0
    progress.current_position_seconds = progress.total_duration_seconds
    progress.last_watched_at = datetime.utcnow()
    progress.updated_at = datetime.utcnow()
    
    await db.commit()
    return True


async def remove_from_continue_watching(
    user_id: UUID,
    content_id: UUID,
    db: AsyncSession,
    episode_id: Optional[UUID] = None
) -> bool:
    """Remove content from continue watching (delete progress)"""
    
    query = select(UserWatchProgress).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.content_id == content_id,
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


async def get_watch_progress_stats(
    user_id: UUID,
    db: AsyncSession
) -> dict:
    """Get user's watch progress statistics"""
    
    # Total content watched
    total_content_query = select(func.count(UserWatchProgress.id)).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == True
        )
    )
    
    # Total hours watched
    total_hours_query = select(func.sum(UserWatchProgress.total_duration_seconds)).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == True
        )
    )
    
    # Continue watching count
    continue_watching_query = select(func.count(UserWatchProgress.id)).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == False,
            UserWatchProgress.watch_percentage > 5.0
        )
    )
    
    # Recently completed (last 7 days)
    recently_completed_query = select(func.count(UserWatchProgress.id)).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == True,
            UserWatchProgress.last_watched_at >= datetime.utcnow() - timedelta(days=7)
        )
    )
    
    # Last watched at
    last_watched_query = select(func.max(UserWatchProgress.last_watched_at)).where(
        UserWatchProgress.user_id == user_id
    )
    
    # Execute all queries
    total_content_result = await db.execute(total_content_query)
    total_hours_result = await db.execute(total_hours_query)
    continue_watching_result = await db.execute(continue_watching_query)
    recently_completed_result = await db.execute(recently_completed_query)
    last_watched_result = await db.execute(last_watched_query)
    
    total_content = total_content_result.scalar() or 0
    total_seconds = total_hours_result.scalar() or 0
    total_hours = total_seconds / 3600
    continue_watching_count = continue_watching_result.scalar() or 0
    recently_completed_count = recently_completed_result.scalar() or 0
    last_watched_at = last_watched_result.scalar()
    
    # Calculate completion rate
    total_started_query = select(func.count(UserWatchProgress.id)).where(
        UserWatchProgress.user_id == user_id
    )
    total_started_result = await db.execute(total_started_query)
    total_started = total_started_result.scalar() or 0
    
    completion_rate = (total_content / total_started * 100) if total_started > 0 else 0
    
    return {
        "total_content_watched": total_content,
        "total_hours_watched": round(total_hours, 2),
        "completion_rate": round(completion_rate, 2),
        "continue_watching_count": continue_watching_count,
        "recently_completed_count": recently_completed_count,
        "last_watched_at": last_watched_at
    }


async def get_recently_watched(
    user_id: UUID,
    db: AsyncSession,
    limit: int = 10
) -> List[UserWatchProgress]:
    """Get user's recently watched content"""
    
    query = select(UserWatchProgress).where(
        UserWatchProgress.user_id == user_id
    ).options(
        selectinload(UserWatchProgress.content),
        selectinload(UserWatchProgress.episode)
    ).order_by(desc(UserWatchProgress.last_watched_at)).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def cleanup_old_progress(
    db: AsyncSession,
    days_old: int = 30
) -> int:
    """Clean up old watch progress records"""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    
    # Delete old incomplete progress
    query = select(UserWatchProgress).where(
        and_(
            UserWatchProgress.is_completed == False,
            UserWatchProgress.last_watched_at < cutoff_date
        )
    )
    
    result = await db.execute(query)
    old_progress = result.scalars().all()
    
    count = len(old_progress)
    
    for progress in old_progress:
        await db.delete(progress)
    
    await db.commit()
    return count

