"""
Home Screen API Endpoints

This module contains FastAPI endpoints for the Home Screen API.
Provides hero data (slider and categories) and content sections.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.content import Content, Genre, ContentGenre
from app.schemas.home_screen import (
    HeroDataResponse,
    ContentSectionsResponse,
    HeroSliderItem,
    CategoryItem,
    QuickNavItem,
    ContentSection,
    ContentSectionItem,
    ContinueWatchingItem,
    RecommendationItem
)

router = APIRouter(
    tags=["Home Screen"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)


@router.get("/hero-data", response_model=HeroDataResponse)
async def get_home_hero_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get hero data for home screen (slider and categories)"""
    try:
        # Get featured content for hero slider (top rated and recent)
        hero_query = select(Content).where(
            Content.is_deleted == False
        ).order_by(
            desc(Content.platform_rating),
            desc(Content.created_at)
        ).limit(10)
        
        hero_result = await db.execute(hero_query)
        hero_contents = hero_result.scalars().all()
        
        # Build hero slider items
        hero_slider = []
        for content in hero_contents:
            hero_slider.append(HeroSliderItem(
                id=str(content.id),
                title=content.title,
                slug=content.slug,
                content_type=content.content_type,
                poster_url=content.poster_url,
                backdrop_url=content.backdrop_url,
                description=content.description,
                release_date=content.release_date.isoformat() if content.release_date else None,
                platform_rating=content.platform_rating,
                is_featured=content.is_featured
            ))
        
        # Get categories
        categories_query = select(Genre).where(
            Genre.is_deleted == False
        ).order_by(Genre.name)
        
        categories_result = await db.execute(categories_query)
        genres = categories_result.scalars().all()
        
        # Build category items
        categories = []
        for genre in genres:
            # Get content count for this genre
            count_query = select(func.count(Content.id)).join(ContentGenre).where(
                and_(
                    ContentGenre.genre_id == genre.id,
                    Content.is_deleted == False
                )
            )
            count_result = await db.execute(count_query)
            content_count = count_result.scalar() or 0
            
            categories.append(CategoryItem(
                id=str(genre.id),
                name=genre.name,
                slug=genre.name.lower().replace(' ', '-'),
                description=genre.description,
                content_count=content_count
            ))
        
        # Build quick navigation items
        quick_nav = [
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
        
        return HeroDataResponse(
            hero_slider=hero_slider,
            categories=categories,
            quick_nav=quick_nav,
            total_hero_items=len(hero_slider),
            total_categories=len(categories)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching hero data: {str(e)}"
        )


@router.get("/content-sections", response_model=ContentSectionsResponse)
async def get_home_content_sections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get content sections for home screen (trending, top rated, etc.)"""
    try:
        # Helper function to build content section
        async def build_content_section(section_id: str, title: str, query, limit: int = 10):
            result = await db.execute(query.limit(limit))
            contents = result.scalars().all()
            
            items = []
            for content in contents:
                items.append(ContentSectionItem(
                    id=str(content.id),
                    title=content.title,
                    slug=content.slug,
                    content_type=content.content_type,
                    poster_url=content.poster_url,
                    backdrop_url=content.backdrop_url,
                    release_date=content.release_date.isoformat() if content.release_date else None,
                    platform_rating=content.platform_rating,
                    platform_votes=content.platform_votes or 0,
                    description=content.description,
                    is_featured=content.is_featured
                ))
            
            # Get total count for has_more
            count_query = select(func.count(Content.id)).where(
                Content.is_deleted == False
            )
            if section_id == "trending":
                # Trending uses platform rating and votes
                pass
            elif section_id == "top-rated":
                count_query = count_query.where(Content.platform_rating >= 4.0)
            elif section_id == "new-releases":
                from datetime import datetime, timedelta
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                count_query = count_query.where(Content.release_date >= thirty_days_ago)
            
            count_result = await db.execute(count_query)
            total_count = count_result.scalar() or 0
            
            return ContentSection(
                section_id=section_id,
                title=title,
                items=items,
                total_items=total_count,
                has_more=total_count > limit,
                view_all_route=f"/{section_id.replace('_', '-')}"
            )
        
        # Build trending section
        trending_query = select(Content).where(
            Content.is_deleted == False
        ).order_by(
            desc(Content.platform_rating),
            desc(Content.platform_votes),
            desc(Content.created_at)
        )
        trending_section = await build_content_section("trending", "Trending Now", trending_query)
        
        # Build top rated section
        top_rated_query = select(Content).where(
            and_(
                Content.is_deleted == False,
                Content.platform_rating >= 4.0
            )
        ).order_by(
            desc(Content.platform_rating),
            desc(Content.platform_votes)
        )
        top_rated_section = await build_content_section("top_rated", "Top Rated", top_rated_query)
        
        # Build new releases section
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_releases_query = select(Content).where(
            and_(
                Content.is_deleted == False,
                Content.release_date >= thirty_days_ago
            )
        ).order_by(
            desc(Content.release_date),
            desc(Content.platform_rating)
        )
        new_releases_section = await build_content_section("new_releases", "New Releases", new_releases_query)
        
        # Build recently added section
        recently_added_query = select(Content).where(
            Content.is_deleted == False
        ).order_by(desc(Content.created_at))
        recently_added_section = await build_content_section("recently_added", "Recently Added", recently_added_query)
        
        # Build continue watching (placeholder - would need watch progress data)
        continue_watching = []
        
        # Build recommendations (placeholder - would need recommendation engine)
        recommendations = []
        
        # Build genre sections (top 3 genres)
        genre_sections = []
        genres_query = select(Genre).where(
            Genre.is_deleted == False
        ).order_by(Genre.name).limit(3)
        
        genres_result = await db.execute(genres_query)
        genres = genres_result.scalars().all()
        
        for genre in genres:
            genre_query = select(Content).join(ContentGenre).where(
                and_(
                    ContentGenre.genre_id == genre.id,
                    Content.is_deleted == False
                )
            ).order_by(
                desc(Content.platform_rating),
                desc(Content.created_at)
            )
            genre_section = await build_content_section(
                f"genre_{genre.name.lower().replace(' ', '_')}",
                f"{genre.name} Content",
                genre_query
            )
            genre_sections.append(genre_section)
        
        return ContentSectionsResponse(
            trending=trending_section,
            top_rated=top_rated_section,
            new_releases=new_releases_section,
            continue_watching=continue_watching,
            recommendations=recommendations,
            recently_added=recently_added_section,
            genre_sections=genre_sections,
            total_sections=4 + len(genre_sections)  # 4 main sections + genre sections
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching content sections: {str(e)}"
        )
