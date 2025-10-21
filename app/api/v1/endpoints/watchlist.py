from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.content import UserContentInteraction, Content
from app.schemas.watchlist import WatchlistResponse, WatchlistActionResponse
from app.utils.watchlist_utils import get_user_watchlist_content

router = APIRouter()

@router.get("/", response_model=WatchlistResponse)
async def get_user_watchlist(
    period: str = "total",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's watchlist content details separated by movies and TV shows"""
    try:
        watchlist_data = await get_user_watchlist_content(current_user.id, db, period)
        return WatchlistResponse(
            movies=watchlist_data["movies"],
            tv_shows=watchlist_data["tv_shows"],
            total_movies=watchlist_data["total_movies"],
            total_tv_shows=watchlist_data["total_tv_shows"],
            total_watchlist=watchlist_data["total_watchlist"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching watchlist content: {str(e)}"
        )

@router.post("/{content_id}", response_model=WatchlistActionResponse)
async def add_to_watchlist(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add content to user's watchlist"""
    try:
        # Check if content exists
        content_query = select(Content).where(
            and_(Content.id == content_id, Content.is_deleted == False)
        )
        content_result = await db.execute(content_query)
        content = content_result.scalar_one_or_none()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Check if already in watchlist
        existing_query = select(UserContentInteraction).where(
            and_(
                UserContentInteraction.user_id == current_user.id,
                UserContentInteraction.content_id == content_id,
                UserContentInteraction.interaction_type == "watchlist"
            )
        )
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            return WatchlistActionResponse(
                message="Content already in watchlist", 
                status="already_added"
            )
        
        # Add to watchlist
        watchlist_item = UserContentInteraction(
            user_id=current_user.id,
            content_id=content_id,
            interaction_type="watchlist"
        )
        db.add(watchlist_item)
        await db.commit()
        
        return WatchlistActionResponse(
            message="Content added to watchlist", 
            status="added"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding to watchlist: {str(e)}"
        )

@router.delete("/{content_id}", response_model=WatchlistActionResponse)
async def remove_from_watchlist(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove content from user's watchlist"""
    try:
        # Find the watchlist entry
        query = select(UserContentInteraction).where(
            and_(
                UserContentInteraction.user_id == current_user.id,
                UserContentInteraction.content_id == content_id,
                UserContentInteraction.interaction_type == "watchlist"
            )
        )
        result = await db.execute(query)
        watchlist_entry = result.scalar_one_or_none()
        
        if not watchlist_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found in watchlist"
            )
        
        await db.delete(watchlist_entry)
        await db.commit()
        
        return WatchlistActionResponse(
            message="Content removed from watchlist", 
            status="removed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing from watchlist: {str(e)}"
        )

