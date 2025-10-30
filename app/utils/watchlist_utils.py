from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy import func, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.content import UserContentInteraction, Content, Genre

async def get_user_watchlist_content(user_id: UUID, db: AsyncSession, period: str = "total") -> dict:
    """Get user's watchlist content with details separated by movies and TV shows"""
    date_filter = get_date_filter(period)
    
    # Get all watchlist content with details
    query = select(Content).join(
        UserContentInteraction, Content.id == UserContentInteraction.content_id
    ).where(
        and_(
            UserContentInteraction.user_id == user_id,
            UserContentInteraction.interaction_type == "watchlist",
            Content.is_deleted == False,
            date_filter
        )
    ).options(
        selectinload(Content.genres)
    )
    
    result = await db.execute(query)
    all_watchlist = result.scalars().all()
    
    # Separate movies and TV shows
    movies = []
    tv_shows = []
    
    for content in all_watchlist:
        # Get the interaction to access added_at timestamp
        interaction_query = select(UserContentInteraction).where(
            and_(
                UserContentInteraction.user_id == user_id,
                UserContentInteraction.content_id == content.id,
                UserContentInteraction.interaction_type == "watchlist"
            )
        )
        interaction_result = await db.execute(interaction_query)
        interaction = interaction_result.scalar_one_or_none()
        
        # Normalize content_type to a plain string (model may store str or Enum)
        _ctype = content.content_type if isinstance(content.content_type, str) else getattr(content.content_type, "value", None)

        content_item = {
            "id": str(content.id),
            "title": content.title,
            "slug": content.slug,
            "description": content.description,
            "poster_url": content.poster_url,
            "backdrop_url": content.backdrop_url,
            "content_type": _ctype,
            "release_date": content.release_date.isoformat() if content.release_date else None,
            "platform_rating": content.platform_rating,
            "platform_votes": content.platform_votes,
            "genres": [{"id": str(genre.id), "name": genre.name} for genre in content.genres],
            "added_at": interaction.created_at.isoformat() if interaction else datetime.utcnow().isoformat()
        }
        
        if _ctype == "movie":
            movies.append(content_item)
        else:
            tv_shows.append(content_item)
    
    return {
        "movies": movies,
        "tv_shows": tv_shows,
        "total_movies": len(movies),
        "total_tv_shows": len(tv_shows),
        "total_watchlist": len(all_watchlist)
    }

def get_date_filter(period: str):
    """Get date filter based on period"""
    now = datetime.utcnow()
    if period == "week":
        return UserContentInteraction.created_at >= now - timedelta(days=7)
    elif period == "month":
        return UserContentInteraction.created_at >= now - timedelta(days=30)
    elif period == "year":
        return UserContentInteraction.created_at >= now - timedelta(days=365)
    else:  # total
        return True
