from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.continue_watching import (
    ContinueWatchingItem,
    ContinueWatchingResponse,
    MarkAsCompletedRequest,
    RemoveFromContinueWatchingRequest,
    ResumePositionResponse,
    WatchProgressResponse,
    WatchProgressStats,
    WatchProgressUpdate,
)
from app.utils.continue_watching_utils import (
    get_continue_watching_list,
    get_resume_position,
    get_watch_progress_stats,
    mark_as_completed,
    remove_from_continue_watching,
    update_watch_progress,
)

router = APIRouter()


@router.get("/", response_model=ContinueWatchingResponse)
async def get_continue_watching(
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=50, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get user's continue watching list"""
    try:
        progress_list, total = await get_continue_watching_list(
            user_id=current_user.id,
            db=db,
            limit=limit,
            offset=offset
        )
        
        # Convert to response format
        items = []
        for progress in progress_list:
            # Get content details
            content = progress.content
            episode = progress.episode
            
            item = ContinueWatchingItem(
                content_id=progress.content_id,
                title=content.title,
                thumbnail_url=content.thumbnail_url,
                content_type=content.content_type.value,
                season_number=episode.season.season_number if episode and episode.season else None,
                episode_number=episode.episode_number if episode else None,
                episode_title=episode.title if episode else None,
                resume_position_seconds=progress.current_position_seconds,
                total_duration_seconds=progress.total_duration_seconds,
                watch_percentage=progress.watch_percentage,
                last_watched_at=progress.last_watched_at,
                resume_position_formatted=progress.resume_position_formatted,
                total_duration_formatted=progress.total_duration_formatted,
                time_remaining_seconds=progress.total_duration_seconds - progress.current_position_seconds
            )
            items.append(item)
        
        has_more = (offset + limit) < total
        
        return ContinueWatchingResponse(
            items=items,
            total=total,
            has_more=has_more
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching continue watching list: {str(e)}"
        )


@router.get("/stats", response_model=WatchProgressStats)
async def get_watch_progress_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get user's watch progress statistics"""
    try:
        stats = await get_watch_progress_stats(
            user_id=current_user.id,
            db=db
        )
        
        return WatchProgressStats(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching watch progress stats: {str(e)}"
        )


@router.get("/{content_id}/resume", response_model=ResumePositionResponse)
async def get_resume_position(
    content_id: UUID,
    episode_id: UUID = Query(None, description="Episode ID for TV shows"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get resume position for specific content"""
    try:
        progress = await get_resume_position(
            user_id=current_user.id,
            content_id=content_id,
            db=db,
            episode_id=episode_id
        )
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume position found for this content"
            )
        
        return ResumePositionResponse(
            content_id=progress.content_id,
            episode_id=progress.episode_id,
            resume_position_seconds=progress.current_position_seconds,
            total_duration_seconds=progress.total_duration_seconds,
            watch_percentage=progress.watch_percentage,
            is_completed=progress.is_completed,
            last_watched_at=progress.last_watched_at,
            resume_position_formatted=progress.resume_position_formatted,
            total_duration_formatted=progress.total_duration_formatted,
            time_remaining_seconds=progress.total_duration_seconds - progress.current_position_seconds
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching resume position: {str(e)}"
        )


@router.post("/{content_id}/progress", response_model=WatchProgressResponse)
async def update_watch_progress(
    content_id: UUID,
    progress_data: WatchProgressUpdate,
    episode_id: UUID = Query(None, description="Episode ID for TV shows"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update watch progress for content"""
    try:
        progress = await update_watch_progress(
            user_id=current_user.id,
            content_id=content_id,
            current_position_seconds=progress_data.current_position_seconds,
            total_duration_seconds=progress_data.total_duration_seconds,
            db=db,
            episode_id=episode_id
        )
        
        return WatchProgressResponse(
            id=progress.id,
            user_id=progress.user_id,
            content_id=progress.content_id,
            episode_id=progress.episode_id,
            current_position_seconds=progress.current_position_seconds,
            total_duration_seconds=progress.total_duration_seconds,
            watch_percentage=progress.watch_percentage,
            is_completed=progress.is_completed,
            last_watched_at=progress.last_watched_at,
            created_at=progress.created_at,
            updated_at=progress.updated_at,
            resume_position_formatted=progress.resume_position_formatted,
            total_duration_formatted=progress.total_duration_formatted
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating watch progress: {str(e)}"
        )


# Manual completion endpoint removed - content auto-completes when user reaches the end


@router.delete("/{content_id}")
async def remove_from_continue_watching(
    content_id: UUID,
    request: RemoveFromContinueWatchingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Remove content from continue watching list"""
    try:
        success = await remove_from_continue_watching(
            user_id=current_user.id,
            content_id=content_id,
            db=db,
            episode_id=request.episode_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watch progress not found for this content"
            )
        
        return {"message": "Content removed from continue watching successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing content from continue watching: {str(e)}"
        )


@router.delete("/")
async def clear_continue_watching_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Clear all continue watching history for user"""
    try:
        from app.utils.continue_watching_utils import clear_all_continue_watching
        
        deleted_count = await clear_all_continue_watching(
            user_id=current_user.id,
            db=db
        )
        
        return {
            "message": f"Continue watching history cleared successfully. {deleted_count} items removed.",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing continue watching history: {str(e)}"
        )
