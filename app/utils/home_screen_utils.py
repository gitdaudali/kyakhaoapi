"""
Home Screen Utility Functions

This module contains utility functions for home screen data processing,
optimized database queries, and data conversion.
"""

from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func, text
from sqlalchemy.orm import selectinload

from app.models.content import Content, Genre, ContentGenre
from app.models.user import User
from app.models.watch_progress import UserWatchProgress
from app.schemas.unified_content import (
    UnifiedContentItem,
    ContentSection,
    CategoryItem,
    QuickNavItem,
    HeroDataResponse,
    ContentSectionsResponse
)


async def convert_content_to_unified_item(
    content: Content,
    include_watch_progress: bool = False,
    user_id: Optional[str] = None,
    db: Optional[AsyncSession] = None
) -> UnifiedContentItem:
    """Convert Content model to UnifiedContentItem with proper defaults."""
    
    # Get watch progress data if needed
    watch_progress = None
    if include_watch_progress and user_id and db:
        progress_query = select(UserWatchProgress).where(
            and_(
                UserWatchProgress.user_id == user_id,
                UserWatchProgress.content_id == content.id,
                UserWatchProgress.is_completed == False
            )
        ).order_by(desc(UserWatchProgress.updated_at)).limit(1)
        
        progress_result = await db.execute(progress_query)
        watch_progress = progress_result.scalar_one_or_none()
    
    return UnifiedContentItem(
        id=str(content.id),
        title=content.title or "",
        slug=content.slug or "",
        content_type=content.content_type.value if content.content_type else "movie",
        poster_url=content.poster_url or "",
        backdrop_url=content.backdrop_url or "",
        thumbnail_url=content.thumbnail_url or content.poster_url or "",
        description=content.description,
        release_date=content.release_date.isoformat() if content.release_date else None,
        platform_rating=float(content.platform_rating) if content.platform_rating else 0.0,
        platform_votes=int(content.platform_votes) if content.platform_votes else 0,
        is_featured=bool(content.is_featured),
        is_trending=bool(content.is_trending),
        current_position_seconds=watch_progress.current_position_seconds if watch_progress else None,
        total_duration_seconds=watch_progress.total_duration_seconds if watch_progress else None,
        progress_percentage=watch_progress.watch_percentage if watch_progress else None,
        last_watched_at=watch_progress.last_watched_at if watch_progress else None,
        episode_title=watch_progress.episode.title if watch_progress and watch_progress.episode else None,
        season_number=watch_progress.episode.season.season_number if watch_progress and watch_progress.episode and watch_progress.episode.season else None,
        episode_number=watch_progress.episode.episode_number if watch_progress and watch_progress.episode else None,
    )


async def get_hero_content_optimized(db: AsyncSession, limit: int = 10) -> List[Content]:
    """Get hero content with optimized single query."""
    query = select(Content).where(
        Content.is_deleted == False
    ).order_by(
        desc(Content.platform_rating),
        desc(Content.created_at)
    ).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_categories_with_counts_optimized(db: AsyncSession) -> List[Tuple[Genre, int]]:
    """Get categories with content counts in a single optimized query."""
    query = select(
        Genre,
        func.count(Content.id).label('content_count')
    ).outerjoin(
        ContentGenre, Genre.id == ContentGenre.genre_id
    ).outerjoin(
        Content, and_(
            ContentGenre.content_id == Content.id,
            Content.is_deleted == False
        )
    ).where(
        Genre.is_deleted == False
    ).group_by(Genre.id).order_by(Genre.name)
    
    result = await db.execute(query)
    return result.all()


async def get_content_section_optimized(
    db: AsyncSession,
    section_type: str,
    limit: int = 10,
    offset: int = 0,
    user_id: Optional[str] = None
) -> Tuple[List[Content], int]:
    """Get content for a specific section with optimized query."""
    
    base_query = select(Content).where(Content.is_deleted == False)
    
    if section_type == "trending":
        query = base_query.order_by(
            desc(Content.platform_rating),
            desc(Content.platform_votes),
            desc(Content.created_at)
        )
    elif section_type == "top_rated":
        query = base_query.where(
            Content.platform_rating >= 4.0
        ).order_by(
            desc(Content.platform_rating),
            desc(Content.platform_votes)
        )
    elif section_type == "new_releases":
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        query = base_query.where(
            Content.release_date >= thirty_days_ago
        ).order_by(
            desc(Content.release_date),
            desc(Content.platform_rating)
        )
    elif section_type == "recently_added":
        query = base_query.order_by(desc(Content.created_at))
    else:
        query = base_query.order_by(desc(Content.created_at))
    
    # Get total count
    count_query = select(func.count(Content.id)).where(Content.is_deleted == False)
    if section_type == "top_rated":
        count_query = count_query.where(Content.platform_rating >= 4.0)
    elif section_type == "new_releases":
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        count_query = count_query.where(Content.release_date >= thirty_days_ago)
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # Get paginated results
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    contents = result.scalars().all()
    
    return contents, total


async def get_continue_watching_optimized(
    db: AsyncSession,
    user_id: str,
    limit: int = 10
) -> List[Content]:
    """Get continue watching content with optimized query."""
    query = select(Content).join(
        UserWatchProgress, Content.id == UserWatchProgress.content_id
    ).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == False,
            Content.is_deleted == False
        )
    ).order_by(
        desc(UserWatchProgress.last_watched_at)
    ).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_recommendations_optimized(
    db: AsyncSession,
    user_id: str,
    limit: int = 10
) -> List[Content]:
    """Get personalized recommendations with optimized query."""
    # For now, return trending content as recommendations
    # This should be replaced with actual recommendation engine
    query = select(Content).where(
        Content.is_deleted == False
    ).order_by(
        desc(Content.platform_rating),
        desc(Content.created_at)
    ).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_genre_sections_optimized(
    db: AsyncSession,
    user_id: Optional[str] = None,
    limit: int = 3,
    items_per_section: int = 10
) -> List[Tuple[Genre, List[Content]]]:
    """Get genre sections with optimized queries."""
    # Get top genres by content count
    genre_query = select(
        Genre,
        func.count(Content.id).label('content_count')
    ).outerjoin(
        ContentGenre, Genre.id == ContentGenre.genre_id
    ).outerjoin(
        Content, and_(
            ContentGenre.content_id == Content.id,
            Content.is_deleted == False
        )
    ).where(
        Genre.is_deleted == False
    ).group_by(Genre.id).order_by(
        desc('content_count'),
        Genre.name
    ).limit(limit)
    
    genre_result = await db.execute(genre_query)
    genres_with_counts = genre_result.all()
    
    genre_sections = []
    for genre, content_count in genres_with_counts:
        if content_count > 0:  # Only include genres with content
            # Get content for this genre
            content_query = select(Content).join(
                ContentGenre, Content.id == ContentGenre.content_id
            ).where(
                and_(
                    ContentGenre.genre_id == genre.id,
                    Content.is_deleted == False
                )
            ).order_by(
                desc(Content.platform_rating),
                desc(Content.created_at)
            ).limit(items_per_section)
            
            content_result = await db.execute(content_query)
            contents = content_result.scalars().all()
            
            genre_sections.append((genre, contents))
    
    return genre_sections


def create_quick_nav_items() -> List[QuickNavItem]:
    """Create quick navigation items."""
    return [
        QuickNavItem(
            id="trending",
            title="Trending",
            icon="trending-up",
            route="/trending"
        ),
        QuickNavItem(
            id="top-rated",
            title="Top Rated",
            icon="star",
            route="/top-rated"
        ),
        QuickNavItem(
            id="new-releases",
            title="New Releases",
            icon="calendar",
            route="/new-releases"
        ),
        QuickNavItem(
            id="my-list",
            title="My List",
            icon="bookmark",
            route="/my-list"
        )
    ]
