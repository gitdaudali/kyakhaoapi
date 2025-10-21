from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.recently_watched import (
    RecentlyWatchedResponse,
    RecentlyWatchedItem,
    RecentlyWatchedStats,
    RecentlyWatchedDetail
)
from app.utils.recently_watched_utils import (
    get_recently_watched_list,
    get_recently_watched_by_id,
    get_recently_watched_stats
)
from app.utils.content_utils import get_content_by_id, get_episode_by_id, calculate_pagination_info

router = APIRouter()


@router.get("/", response_model=RecentlyWatchedResponse)
async def get_recently_watched(
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    content_type: Optional[str] = Query(None, description="Filter by content type (movie, tv_series, etc.)"),
    days_back: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get user's recently watched (completed) content"""
    try:
        progress_list, total = await get_recently_watched_list(
            user_id=current_user.id,
            db=db,
            limit=limit,
            offset=offset,
            content_type=content_type,
            days_back=days_back
        )
        
        # Convert to response format
        items = []
        for progress in progress_list:
            content = await get_content_by_id(db, progress.content_id)
            if not content:
                continue
            
            episode_title = None
            season_number = None
            episode_number = None
            if progress.episode_id:
                episode = await get_episode_by_id(db, progress.episode_id)
                if episode:
                    episode_title = episode.title
                    season_number = episode.season_number
                    episode_number = episode.episode_number
            
            # Calculate watch duration (time spent watching)
            watch_duration = progress.current_position_seconds
            
            items.append(
                RecentlyWatchedItem(
                    content_id=progress.content_id,
                    title=content.title,
                    thumbnail_url=content.poster_url,
                    content_type=content.content_type.value,
                    season_number=season_number,
                    episode_number=episode_number,
                    episode_title=episode_title,
                    completed_at=progress.last_watched_at,
                    watch_duration_seconds=watch_duration,
                    completion_percentage=progress.watch_percentage,
                    watch_duration_formatted="",  # Will be computed by validator
                    days_ago=0  # Will be computed by validator
                )
            )
        
        has_more = (offset + limit) < total
        
        return RecentlyWatchedResponse(
            items=items,
            total=total,
            has_more=has_more
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recently watched list: {str(e)}"
        )


@router.get("/stats", response_model=RecentlyWatchedStats)
async def get_recently_watched_stats(
    days_back: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get user's recently watched statistics"""
    try:
        stats = await get_recently_watched_stats(
            user_id=current_user.id,
            db=db,
            days_back=days_back
        )
        return RecentlyWatchedStats(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recently watched statistics: {str(e)}"
        )


@router.get("/{content_id}", response_model=RecentlyWatchedDetail)
async def get_recently_watched_detail(
    content_id: UUID,
    episode_id: Optional[UUID] = Query(None, description="Episode ID if content is a TV series episode"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get specific recently watched content detail"""
    try:
        progress = await get_recently_watched_by_id(
            user_id=current_user.id,
            content_id=content_id,
            db=db,
            episode_id=episode_id
        )
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recently watched content not found"
            )
        
        content = await get_content_by_id(db, progress.content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        episode_title = None
        season_number = None
        episode_number = None
        if progress.episode_id:
            episode = await get_episode_by_id(db, progress.episode_id)
            if episode:
                episode_title = episode.title
                season_number = episode.season_number
                episode_number = episode.episode_number
        
        return RecentlyWatchedDetail(
            content_id=progress.content_id,
            episode_id=progress.episode_id,
            title=content.title,
            content_type=content.content_type.value,
            season_number=season_number,
            episode_number=episode_number,
            episode_title=episode_title,
            completed_at=progress.last_watched_at,
            watch_duration_seconds=progress.current_position_seconds,
            completion_percentage=progress.watch_percentage,
            total_duration_seconds=progress.total_duration_seconds,
            watch_duration_formatted="",  # Will be computed by validator
            total_duration_formatted="",  # Will be computed by validator
            days_ago=0  # Will be computed by validator
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recently watched detail: {str(e)}"
        )


@router.delete("/{content_id}")
async def remove_from_recently_watched(
    content_id: UUID,
    episode_id: Optional[UUID] = Query(None, description="Episode ID if content is a TV series episode"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Remove specific content from recently watched history"""
    try:
        from app.utils.recently_watched_utils import remove_from_recently_watched
        
        success = await remove_from_recently_watched(
            user_id=current_user.id,
            content_id=content_id,
            db=db,
            episode_id=episode_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found in recently watched history"
            )
        
        return {"message": "Content removed from recently watched history successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing content from recently watched: {str(e)}"
        )


@router.delete("/")
async def clear_recently_watched_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Clear all recently watched history for user"""
    try:
        from app.utils.recently_watched_utils import clear_all_recently_watched
        
        deleted_count = await clear_all_recently_watched(
            user_id=current_user.id,
            db=db
        )
        
        return {
            "message": f"Recently watched history cleared successfully. {deleted_count} items removed.",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing recently watched history: {str(e)}"
        )


