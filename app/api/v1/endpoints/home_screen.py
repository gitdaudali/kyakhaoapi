"""
Comprehensive Home Screen API

This module provides a single, comprehensive Home Screen API that includes:
1. Hero/Slider data and Categories in the main endpoint
2. All content sections (trending, top-rated, new-releases, etc.)
3. See All API for category-specific data
4. Optimized database queries and Netflix-style responses
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response_handler import success_response, error_response
from app.models.user import User
from app.models.content import Content, Genre, ContentGenre, ContentCast, ContentCrew, Person, UserContentInteraction, InteractionType
from app.models.watch_progress import UserWatchProgress

router = APIRouter(
    tags=["Home Screen"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)


class ContentItem(BaseModel):
    """Unified content item schema for all home screen responses."""
    id: str
    title: str
    slug: str
    content_type: str
    poster_url: str = ""
    backdrop_url: str = ""
    thumbnail_url: str = ""
    description: Optional[str] = None
    release_date: Optional[str] = None
    platform_rating: float = 0.0
    platform_votes: int = 0
    is_featured: bool = False
    is_trending: bool = False
    is_new_release: bool = False
    is_premium: bool = False
    
    # User interaction data
    is_favorite: bool = False
    is_in_watchlist: bool = False
    watch_progress: Optional[float] = None
    last_watched_at: Optional[datetime] = None
    
    # Continue watching specific
    current_position_seconds: Optional[int] = None
    total_duration_seconds: Optional[int] = None
    episode_title: Optional[str] = None
    season_number: Optional[int] = None
    episode_number: Optional[int] = None
    
    # Recommendation data
    recommendation_score: Optional[float] = None
    recommendation_reason: Optional[str] = None
    
    # Metadata
    genres: List[str] = []
    cast: List[Dict[str, Any]] = []
    total_views: int = 0
    likes_count: int = 0
    reviews_count: int = 0
    
    class Config:
        from_attributes = True


class SimpleContentItem(BaseModel):
    """Simplified content item for Home Screen API - Netflix style minimal data."""
    id: str
    title: str
    slug: str
    content_type: str
    poster_url: str = ""
    backdrop_url: str = ""
    thumbnail_url: str = ""
    platform_rating: float = 0.0
    is_featured: bool = False
    is_trending: bool = False
    is_premium: bool = False
    
    class Config:
        from_attributes = True


class ContentSection(BaseModel):
    """Content section with pagination."""
    section_id: str
    title: str
    subtitle: Optional[str] = None
    items: List[ContentItem]
    total_items: int
    has_more: bool
    view_all_route: str
    page: int = 1
    size: int = 20
    
    class Config:
        from_attributes = True


class CategoryItem(BaseModel):
    """Category navigation item."""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    content_count: int = 0
    is_featured: bool = False
    
    class Config:
        from_attributes = True


class QuickNavItem(BaseModel):
    """Quick navigation item."""
    id: str
    title: str
    icon: str
    route: str
    badge_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class HomeScreenResponse(BaseModel):
    """Complete home screen response."""
    # Hero/Slider data
    hero_slider: List[ContentItem]
    categories: List[CategoryItem]
    quick_nav: List[QuickNavItem]
    
    # Content sections
    trending: ContentSection
    top_rated: ContentSection
    new_releases: ContentSection
    recently_added: ContentSection
    continue_watching: List[ContentItem]
    recommendations: List[ContentItem]
    genre_sections: List[ContentSection]
    
    # Metadata
    total_hero_items: int
    total_categories: int
    total_sections: int
    generated_at: datetime
    
    class Config:
        from_attributes = True


async def convert_content_to_simple_item(content: Content) -> SimpleContentItem:
    """Convert Content model to SimpleContentItem for Home Screen API - Netflix style minimal data."""
    return SimpleContentItem(
        id=str(content.id),
        title=content.title or "",
        slug=content.slug or "",
        content_type=content.content_type if content.content_type else "movie",
        poster_url=content.poster_url or "",
        backdrop_url=content.backdrop_url or "",
        thumbnail_url=content.poster_url or "",  # Use poster as thumbnail
        platform_rating=float(content.platform_rating) if content.platform_rating else 0.0,
        is_featured=bool(content.is_featured),
        is_trending=bool(content.is_trending),
        is_premium=bool(content.is_premium)
    )


async def convert_content_to_item(
    content: Content,
    user_id: Optional[str] = None,
    db: Optional[AsyncSession] = None,
    include_watch_progress: bool = False,
    include_user_interactions: bool = False
) -> ContentItem:
    """Convert Content model to ContentItem with user-specific data."""
    
    # Get watch progress if needed
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
    
    # Get user interactions if needed
    is_favorite = False
    is_in_watchlist = False
    if include_user_interactions and user_id and db:
        # Check favorites
        fav_query = select(UserContentInteraction).where(
            and_(
                UserContentInteraction.user_id == user_id,
                UserContentInteraction.content_id == content.id,
                UserContentInteraction.interaction_type == InteractionType.FAVORITE
            )
        )
        fav_result = await db.execute(fav_query)
        is_favorite = fav_result.scalar_one_or_none() is not None
        
        # Check watchlist
        watchlist_query = select(UserContentInteraction).where(
            and_(
                UserContentInteraction.user_id == user_id,
                UserContentInteraction.content_id == content.id,
                UserContentInteraction.interaction_type == InteractionType.WATCHLIST
            )
        )
        watchlist_result = await db.execute(watchlist_query)
        is_in_watchlist = watchlist_result.scalar_one_or_none() is not None
    
    # Get genres
    genres_query = select(Genre).join(ContentGenre).where(
        ContentGenre.content_id == content.id
    )
    genres_result = await db.execute(genres_query) if db else None
    genres = [genre.name for genre in genres_result.scalars().all()] if genres_result else []
    
    # Get cast (first 5 main cast members)
    cast = []
    if db:
        cast_query = select(ContentCast, Person).join(Person).where(
            ContentCast.content_id == content.id
        ).order_by(ContentCast.cast_order).limit(5)
        cast_result = await db.execute(cast_query)
        cast = [
            {
                "name": person.name,
                "character": cast_item.character_name,
                "profile_image": person.profile_image_url
            }
            for cast_item, person in cast_result.all()
        ]
    
    return ContentItem(
        id=str(content.id),
        title=content.title or "",
        slug=content.slug or "",
        content_type=content.content_type if content.content_type else "movie",
        poster_url=content.poster_url or "",
        backdrop_url=content.backdrop_url or "",
        thumbnail_url=content.poster_url or "",  # Use poster as thumbnail
        description=content.description,
        release_date=content.release_date.isoformat() if content.release_date else None,
        platform_rating=float(content.platform_rating) if content.platform_rating else 0.0,
        platform_votes=int(content.platform_votes) if content.platform_votes else 0,
        is_featured=bool(content.is_featured),
        is_trending=bool(content.is_trending),
        is_new_release=bool(content.is_new_release),
        is_premium=bool(content.is_premium),
        is_favorite=is_favorite,
        is_in_watchlist=is_in_watchlist,
        watch_progress=watch_progress.watch_percentage if watch_progress else None,
        last_watched_at=watch_progress.last_watched_at if watch_progress else None,
        current_position_seconds=watch_progress.current_position_seconds if watch_progress else None,
        total_duration_seconds=watch_progress.total_duration_seconds if watch_progress else None,
        episode_title=watch_progress.episode.title if watch_progress and watch_progress.episode else None,
        season_number=watch_progress.episode.season.season_number if watch_progress and watch_progress.episode and watch_progress.episode.season else None,
        episode_number=watch_progress.episode.episode_number if watch_progress and watch_progress.episode else None,
        genres=genres,
        cast=cast,
        total_views=int(content.total_views) if content.total_views else 0,
        likes_count=int(content.likes_count) if content.likes_count else 0,
        reviews_count=int(content.reviews_count) if content.reviews_count else 0
    )


async def get_hero_content(db: AsyncSession, limit: int = 10) -> List[Content]:
    """Get hero content with optimized query."""
    query = select(Content).where(
        and_(
            Content.is_deleted == False,
            Content.status == "published",
            or_(Content.is_featured == True, Content.is_trending == True)
        )
    ).order_by(
        desc(Content.platform_rating),
        desc(Content.created_at)
    ).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_categories_with_counts(db: AsyncSession) -> List[tuple]:
    """Get categories with content counts."""
    query = select(
        Genre,
        func.count(Content.id).label('content_count')
    ).outerjoin(
        ContentGenre, Genre.id == ContentGenre.genre_id
    ).outerjoin(
        Content, and_(
            ContentGenre.content_id == Content.id,
            Content.is_deleted == False,
            Content.status == "published"
        )
    ).where(
        Genre.is_deleted == False
    ).group_by(Genre.id).order_by(Genre.name)
    
    result = await db.execute(query)
    return result.all()


async def get_content_section(
    db: AsyncSession,
    section_type: str,
    limit: int = 20,
    offset: int = 0
) -> tuple[List[Content], int]:
    """Get content for a specific section with optimized query."""
    
    base_query = select(Content).where(
        and_(
            Content.is_deleted == False,
            Content.status == "published"
        )
    )
    
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
    count_query = select(func.count(Content.id)).where(
        and_(
            Content.is_deleted == False,
            Content.status == "published"
        )
    )
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


async def get_continue_watching(db: AsyncSession, user_id: str, limit: int = 10) -> List[Content]:
    """Get continue watching content."""
    query = select(Content).join(
        UserWatchProgress, Content.id == UserWatchProgress.content_id
    ).where(
        and_(
            UserWatchProgress.user_id == user_id,
            UserWatchProgress.is_completed == False,
            Content.is_deleted == False,
            Content.status == "published"
        )
    ).order_by(
        desc(UserWatchProgress.last_watched_at)
    ).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_recommendations(db: AsyncSession, user_id: str, limit: int = 10) -> List[Content]:
    """Get personalized recommendations (simplified for now)."""
    # For now, return trending content as recommendations
    # In production, this should use a proper recommendation engine
    query = select(Content).where(
        and_(
            Content.is_deleted == False,
            Content.status == "published"
        )
        ).order_by(
            desc(Content.platform_rating),
            desc(Content.created_at)
    ).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_genre_sections(db: AsyncSession, limit: int = 3, items_per_section: int = 20) -> List[tuple]:
    """Get genre sections with content."""
    # Get top genres by content count
    genre_query = select(
        Genre,
        func.count(Content.id).label('calculated_content_count')
    ).outerjoin(
        ContentGenre, Genre.id == ContentGenre.genre_id
    ).outerjoin(
        Content, and_(
            ContentGenre.content_id == Content.id,
            Content.is_deleted == False,
            Content.status == "published"
        )
    ).where(
            Genre.is_deleted == False
    ).group_by(Genre.id).order_by(
        desc('calculated_content_count'),
        Genre.name
    ).limit(limit)
    
    genre_result = await db.execute(genre_query)
    genres_with_counts = genre_result.all()
    
    genre_sections = []
    for genre, calculated_count in genres_with_counts:
        if calculated_count > 0:
            # Get content for this genre
            content_query = select(Content).join(
                ContentGenre, Content.id == ContentGenre.content_id
            ).where(
                and_(
                    ContentGenre.genre_id == genre.id,
                    Content.is_deleted == False,
                    Content.status == "published"
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
        

@router.get("/home-screen", response_model=dict)
async def get_home_screen(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Home Screen API - Slider and Categories data only.
    
    The Home Screen API provides all the data required to display content on the main landing page of the app.
    This endpoint provides:
    - Hero slider content
    - Navigation categories
    - Quick navigation items
    """
    try:
        user_id = str(current_user.id)
        
        # Get hero content
        hero_contents = await get_hero_content(db, limit=10)
        hero_items = []
        for content in hero_contents:
            item = await convert_content_to_simple_item(content)
            hero_items.append(item)
        
        # Get categories with counts
        categories_with_counts = await get_categories_with_counts(db)
        categories = []
        for genre, content_count in categories_with_counts:
            categories.append({
                "id": str(genre.id),
                "name": genre.name,
                "slug": genre.slug or genre.name.lower().replace(' ', '-'),
                "icon_url": genre.cover_image_url or "",
                "content_count": content_count
            })
        
        # Create quick navigation
        quick_nav = [
            {
                "id": "trending",
                "title": "Trending",
                "icon": "trending-up",
                "route": "/trending"
            },
            {
                "id": "top-rated",
                "title": "Top Rated",
                "icon": "star",
                "route": "/top-rated"
            },
            {
                "id": "new-releases",
                "title": "New Releases",
                "icon": "calendar",
                "route": "/new-releases"
            },
            {
                "id": "my-list",
                "title": "My List",
                "icon": "bookmark",
                "route": "/my-list"
            }
        ]
        
        response_data = {
            "hero_slider": hero_items,
            "categories": categories,
            "quick_nav": quick_nav
        }
        
        return success_response(
            message="Home Screen API - Slider and Categories data retrieved successfully",
            data=response_data
        )
        
    except Exception as e:
        return error_response(
            message="Error fetching home screen data",
            error_code="HOME_SCREEN_FETCH_ERROR",
            data={"error": str(e)},
            status_code=500
        )


@router.get("/home-sections", response_model=dict)
async def get_home_sections(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number for content sections"),
    size: int = Query(20, ge=1, le=50, description="Items per page for content sections"),
    db: AsyncSession = Depends(get_db)
):
    """
    Home Sections API - All content sections for the home screen.
    
    This endpoint provides all other sections after the main home screen:
    - Trending content
    - Top rated content
    - New releases
    - Recently added content
    - Continue watching
    - Recommendations
    - Genre-specific sections
    """
    try:
        user_id = str(current_user.id)
        offset = (page - 1) * size
        
        # Helper function to build simplified content section
        async def build_simple_content_section(section_id: str, title: str, section_type: str, subtitle: str = None):
            contents, total = await get_content_section(db, section_type, size, offset)
            
            items = []
            for content in contents:
                item = await convert_content_to_simple_item(content)
                items.append(item)
            
            return {
                "section_id": section_id,
                "title": title,
                "subtitle": subtitle,
                "items": items,
                "total_items": total,
                "has_more": (offset + size) < total,
                "view_all_route": f"/{section_id.replace('_', '-')}"
            }
        
        # Build all content sections with simplified data
        trending_section = await build_simple_content_section("trending", "Trending Now", "trending", "What's popular right now")
        top_rated_section = await build_simple_content_section("top_rated", "Top Rated", "top_rated", "Highest rated content")
        new_releases_section = await build_simple_content_section("new_releases", "New Releases", "new_releases", "Recently released content")
        recently_added_section = await build_simple_content_section("recently_added", "Recently Added", "recently_added", "Latest additions to our library")
        
        # Get continue watching - simplified
        continue_watching_contents = await get_continue_watching(db, user_id, size)
        continue_watching_items = []
        for content in continue_watching_contents:
            item = await convert_content_to_simple_item(content)
            continue_watching_items.append(item)
        
        # Get recommendations - simplified
        recommendation_contents = await get_recommendations(db, user_id, size)
        recommendation_items = []
        for content in recommendation_contents:
            item = await convert_content_to_simple_item(content)
            recommendation_items.append(item)
        
        # Get genre sections - simplified
        genre_sections_data = await get_genre_sections(db, limit=3, items_per_section=size)
        genre_sections = []
        for genre, contents in genre_sections_data:
            items = []
            for content in contents:
                item = await convert_content_to_simple_item(content)
                items.append(item)
            
            genre_section = {
                "section_id": f"genre_{genre.name.lower().replace(' ', '_')}",
                "title": f"{genre.name} Content",
                "subtitle": f"Explore {genre.name.lower()} content",
                "items": items,
                "total_items": len(contents),
                "has_more": len(contents) >= size,
                "view_all_route": f"/genre/{genre.slug or genre.name.lower().replace(' ', '-')}"
            }
            genre_sections.append(genre_section)
        
        # Build sections array
        sections = []
        
        # Add main content sections
        sections.append(trending_section)
        sections.append(top_rated_section)
        sections.append(new_releases_section)
        sections.append(recently_added_section)
        
        # Add continue watching section
        if continue_watching_items:
            sections.append({
                "section_id": "continue_watching",
                "title": "Continue Watching",
                "subtitle": "Pick up where you left off",
                "items": continue_watching_items,
                "total_items": len(continue_watching_items),
                "has_more": False,
                "view_all_route": "/continue-watching"
            })
        
        # Add recommendations section
        if recommendation_items:
            sections.append({
                "section_id": "recommendations",
                "title": "Recommended for You",
                "subtitle": "Based on your viewing history",
                "items": recommendation_items,
                "total_items": len(recommendation_items),
                "has_more": False,
                "view_all_route": "/recommendations"
            })
        
        # Add genre sections
        sections.extend(genre_sections)
        
        response_data = {
            "sections": sections,
            "total_sections": len(sections)
        }
        
        return success_response(
            message="Home Sections API - All content sections retrieved successfully",
            data=response_data
        )
        
    except Exception as e:
        return error_response(
            message="Error fetching home sections data",
            error_code="HOME_SECTIONS_FETCH_ERROR",
            data={"error": str(e)},
            status_code=500
        )

