from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy import func, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.content import UserContentInteraction, Content, Genre

async def get_user_favorites_content(user_id: UUID, db: AsyncSession, period: str = "total") -> dict:
    """Get user's favorite content with details separated by movies and TV shows"""
    date_filter = get_date_filter(period)
    
    # Get all favorite content with details
    query = select(Content).join(
        UserContentInteraction, Content.id == UserContentInteraction.content_id
    ).where(
        and_(
            UserContentInteraction.user_id == user_id,
            UserContentInteraction.interaction_type == "favorite",
            Content.is_deleted == False,
            date_filter
        )
    ).options(
        selectinload(Content.genres)
    )
    
    result = await db.execute(query)
    all_favorites = result.scalars().all()
    
    # Separate movies and TV shows
    movies = []
    tv_shows = []
    
    for content in all_favorites:
        content_data = {
            "id": str(content.id),
            "title": content.title,
            "slug": content.slug,
            "description": content.description,
            "poster_url": content.poster_url,
            "backdrop_url": content.backdrop_url,
            "content_type": content.content_type,
            "release_date": content.release_date.isoformat() if content.release_date else None,
            "platform_rating": content.platform_rating,
            "platform_votes": content.platform_votes,
            "genres": [{"id": str(genre.id), "name": genre.name} for genre in content.genres],
            "favorited_at": content.created_at.isoformat()
        }
        
        # Separate by content type
        if content.content_type in ["movie", "anime", "short_film"]:
            movies.append(content_data)
        elif content.content_type in ["tv_series", "mini_series", "documentary"]:
            tv_shows.append(content_data)
    
    return {
        "movies": movies,
        "tv_shows": tv_shows,
        "total_movies": len(movies),
        "total_tv_shows": len(tv_shows),
        "total_favorites": len(movies) + len(tv_shows)
    }

def get_date_filter(period: str):
    """Get date filter based on period"""
    now = datetime.utcnow()
    
    if period == "this_month":
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return UserContentInteraction.created_at >= start_of_month
    elif period == "last_month":
        start_of_last_month = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        end_of_last_month = now.replace(day=1) - timedelta(days=1)
        return and_(
            UserContentInteraction.created_at >= start_of_last_month,
            UserContentInteraction.created_at <= end_of_last_month
        )
    elif period == "this_year":
        start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return UserContentInteraction.created_at >= start_of_year
    else:  # "total" or any other value
        return True
