from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.content import UserContentInteraction, Content
from app.schemas.favorites import FavoritesContentResponse
from app.utils.favorites_utils import get_user_favorites_content

router = APIRouter()

@router.get("/", response_model=FavoritesContentResponse)
async def get_user_favorites(
    period: str = "total",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's favorite content details separated by movies and TV shows"""
    try:
        favorites_data = await get_user_favorites_content(current_user.id, db, period)
        return FavoritesContentResponse(
            movies=favorites_data["movies"],
            tv_shows=favorites_data["tv_shows"],
            total_movies=favorites_data["total_movies"],
            total_tv_shows=favorites_data["total_tv_shows"],
            total_favorites=favorites_data["total_favorites"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching favorites content: {str(e)}"
        )

@router.post("/{content_id}")
async def add_to_favorites(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add content to user's favorites"""
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
        
        # Check if already favorited
        existing_query = select(UserContentInteraction).where(
            and_(
                UserContentInteraction.user_id == current_user.id,
                UserContentInteraction.content_id == content_id,
                UserContentInteraction.interaction_type == "favorite"
            )
        )
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            return {"message": "Content already in favorites", "status": "already_favorited"}
        
        # Add to favorites
        favorite = UserContentInteraction(
            user_id=current_user.id,
            content_id=content_id,
            interaction_type="favorite"
        )
        db.add(favorite)
        await db.commit()
        
        return {"message": "Content added to favorites", "status": "added"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding to favorites: {str(e)}"
        )

@router.delete("/{content_id}")
async def remove_from_favorites(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove content from user's favorites"""
    try:
        # Find the favorite interaction
        favorite_query = select(UserContentInteraction).where(
            and_(
                UserContentInteraction.user_id == current_user.id,
                UserContentInteraction.content_id == content_id,
                UserContentInteraction.interaction_type == "favorite"
            )
        )
        favorite_result = await db.execute(favorite_query)
        favorite = favorite_result.scalar_one_or_none()
        
        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found in favorites"
            )
        
        # Remove from favorites
        await db.delete(favorite)
        await db.commit()
        
        return {"message": "Content removed from favorites", "status": "removed"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing from favorites: {str(e)}"
        )
