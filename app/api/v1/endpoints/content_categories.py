"""
Content Categories API Endpoints

This module contains FastAPI endpoints for content category listings.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.content import Content, ContentGenre, Genre
from app.schemas.content_categories import (
    ContentCategoryResponse,
    ContentCategoryItem
)

router = APIRouter(
    tags=["Content Categories"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)


@router.get("/trending", response_model=ContentCategoryResponse)
async def get_trending_content(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    content_type: Optional[str] = Query(None, description="Filter by content type (movie, tv_series)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get trending content with pagination and sorting"""
    try:
        # Calculate offset
        offset = (page - 1) * limit
        
        # Build base query - simplified without problematic fields
        query = select(Content)
        
        # Filter by content type if provided and valid
        if content_type and content_type not in ["string", "null"] and content_type in ["movie", "tv_series"]:
            query = query.where(Content.content_type == content_type)
        
        # Order by trending (using platform_rating and platform_votes as proxy)
        query = query.order_by(
            desc(Content.platform_rating),
            desc(Content.platform_votes),
            desc(Content.created_at)
        )
        
        # Get total count
        count_query = select(func.count(Content.id))
        if content_type and content_type not in ["string", "null"] and content_type in ["movie", "tv_series"]:
            count_query = count_query.where(Content.content_type == content_type)
        
        # Execute count query
        count_result = await db.execute(count_query)
        total_items = count_result.scalar() or 0
        
        # Execute main query
        result = await db.execute(query.offset(offset).limit(limit))
        contents = result.scalars().all()
        
        # Calculate pagination info
        total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1
        
        # Build response items
        items = []
        for content in contents:
            items.append(ContentCategoryItem(
                id=str(content.id),
                title=content.title,
                slug=content.slug,
                content_type=content.content_type,
                poster_url=content.poster_url,
                backdrop_url=content.backdrop_url,
                release_date=content.release_date.isoformat() if content.release_date else None,
                platform_rating=content.platform_rating,
                platform_votes=content.platform_votes or 0,
                description=content.description
            ))
        
        return ContentCategoryResponse(
            category="trending",
            title="Trending Content",
            items=items,
            total_items=total_items,
            total_pages=total_pages,
            current_page=page,
            page_size=limit,
            has_next=has_next,
            has_previous=has_previous
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching trending content: {str(e)}"
        )


@router.get("/top-rated", response_model=ContentCategoryResponse)
async def get_top_rated_content(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    content_type: Optional[str] = Query(None, description="Filter by content type (movie, tv_series)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get top-rated content with pagination and sorting"""
    try:
        # Calculate offset
        offset = (page - 1) * limit
        
        # Build base query - simplified
        query = select(Content)
        
        # Filter by content type if provided and valid
        if content_type and content_type not in ["string", "null"] and content_type in ["movie", "tv_series"]:
            query = query.where(Content.content_type == content_type)
        
        # Only high-rated content
        query = query.where(Content.platform_rating >= 4.0)
        
        # Order by rating
        query = query.order_by(
            desc(Content.platform_rating),
            desc(Content.platform_votes),
            desc(Content.created_at)
        )
        
        # Get total count
        count_query = select(func.count(Content.id)).where(Content.platform_rating >= 4.0)
        if content_type and content_type not in ["string", "null"] and content_type in ["movie", "tv_series"]:
            count_query = count_query.where(Content.content_type == content_type)
        
        # Execute count query
        count_result = await db.execute(count_query)
        total_items = count_result.scalar() or 0
        
        # Execute main query
        result = await db.execute(query.offset(offset).limit(limit))
        contents = result.scalars().all()
        
        # Calculate pagination info
        total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1
        
        # Build response items
        items = []
        for content in contents:
            items.append(ContentCategoryItem(
                id=str(content.id),
                title=content.title,
                slug=content.slug,
                content_type=content.content_type,
                poster_url=content.poster_url,
                backdrop_url=content.backdrop_url,
                release_date=content.release_date.isoformat() if content.release_date else None,
                platform_rating=content.platform_rating,
                platform_votes=content.platform_votes or 0,
                description=content.description
            ))
        
        return ContentCategoryResponse(
            category="top-rated",
            title="Top Rated Content",
            items=items,
            total_items=total_items,
            total_pages=total_pages,
            current_page=page,
            page_size=limit,
            has_next=has_next,
            has_previous=has_previous
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching top-rated content: {str(e)}"
        )


@router.get("/new-releases", response_model=ContentCategoryResponse)
async def get_new_releases(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    content_type: Optional[str] = Query(None, description="Filter by content type (movie, tv_series)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get new releases (content from last 30 days) with pagination and sorting"""
    try:
        from datetime import datetime, timedelta
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Date 30 days ago
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Build base query - simplified
        query = select(Content)
        
        # Filter by content type if provided and valid
        if content_type and content_type not in ["string", "null"] and content_type in ["movie", "tv_series"]:
            query = query.where(Content.content_type == content_type)
        
        # Only recent content
        query = query.where(Content.release_date >= thirty_days_ago)
        
        # Order by release date (newest first)
        query = query.order_by(
            desc(Content.release_date),
            desc(Content.platform_rating),
            desc(Content.created_at)
        )
        
        # Get total count
        count_query = select(func.count(Content.id)).where(Content.release_date >= thirty_days_ago)
        if content_type and content_type not in ["string", "null"] and content_type in ["movie", "tv_series"]:
            count_query = count_query.where(Content.content_type == content_type)
        
        # Execute count query
        count_result = await db.execute(count_query)
        total_items = count_result.scalar() or 0
        
        # Execute main query
        result = await db.execute(query.offset(offset).limit(limit))
        contents = result.scalars().all()
        
        # Calculate pagination info
        total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1
        
        # Build response items
        items = []
        for content in contents:
            items.append(ContentCategoryItem(
                id=str(content.id),
                title=content.title,
                slug=content.slug,
                content_type=content.content_type,
                poster_url=content.poster_url,
                backdrop_url=content.backdrop_url,
                release_date=content.release_date.isoformat() if content.release_date else None,
                platform_rating=content.platform_rating,
                platform_votes=content.platform_votes or 0,
                description=content.description
            ))
        
        return ContentCategoryResponse(
            category="new-releases",
            title="New Releases",
            items=items,
            total_items=total_items,
            total_pages=total_pages,
            current_page=page,
            page_size=limit,
            has_next=has_next,
            has_previous=has_previous
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching new releases: {str(e)}"
        )


@router.get("/by-genre/{genre_name}", response_model=ContentCategoryResponse)
async def get_content_by_genre(
    genre_name: str,
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    content_type: Optional[str] = Query(None, description="Filter by content type (movie, tv_series)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get content filtered by a specific genre with pagination and sorting"""
    try:
        # Calculate offset
        offset = (page - 1) * limit
        
        # Build base query with genre join - simplified
        query = select(Content).join(ContentGenre).join(Genre).where(
            Genre.name.ilike(f"%{genre_name}%")
        )
        
        # Filter by content type if provided and valid
        if content_type and content_type not in ["string", "null"] and content_type in ["movie", "tv_series"]:
            query = query.where(Content.content_type == content_type)
        
        # Order by rating
        query = query.order_by(
            desc(Content.platform_rating),
            desc(Content.platform_votes),
            desc(Content.created_at)
        )
        
        # Get total count
        count_query = select(func.count(Content.id)).join(ContentGenre).join(Genre).where(
            Genre.name.ilike(f"%{genre_name}%")
        )
        if content_type and content_type not in ["string", "null"] and content_type in ["movie", "tv_series"]:
            count_query = count_query.where(Content.content_type == content_type)
        
        # Execute count query
        count_result = await db.execute(count_query)
        total_items = count_result.scalar() or 0
        
        # Execute main query
        result = await db.execute(query.offset(offset).limit(limit))
        contents = result.scalars().all()
        
        # Calculate pagination info
        total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1
        
        # Build response items
        items = []
        for content in contents:
            items.append(ContentCategoryItem(
                id=str(content.id),
                title=content.title,
                slug=content.slug,
                content_type=content.content_type,
                poster_url=content.poster_url,
                backdrop_url=content.backdrop_url,
                release_date=content.release_date.isoformat() if content.release_date else None,
                platform_rating=content.platform_rating,
                platform_votes=content.platform_votes or 0,
                description=content.description
            ))
        
        return ContentCategoryResponse(
            category=f"genre-{genre_name.lower()}",
            title=f"Content in {genre_name.title()}",
            items=items,
            total_items=total_items,
            total_pages=total_pages,
            current_page=page,
            page_size=limit,
            has_next=has_next,
            has_previous=has_previous
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching content by genre: {str(e)}"
        )