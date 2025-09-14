from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.config import settings
from app.models.content import Content, ContentGenre, Genre
from app.schemas.content import ContentFilters, GenreFilters, PaginationParams


async def get_content_by_id(
    db: AsyncSession, content_id: UUID, include_genres: bool = True
) -> Optional[Content]:
    """Get content by ID with optional genre loading"""
    query = select(Content).where(
        and_(Content.id == content_id, Content.is_deleted == False)
    )

    if include_genres:
        query = query.options(selectinload(Content.genres))

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_genre_by_id(db: AsyncSession, genre_id: UUID) -> Optional[Genre]:
    """Get genre by ID"""
    query = select(Genre).where(and_(Genre.id == genre_id, Genre.is_deleted == False))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_genre_by_slug(db: AsyncSession, slug: str) -> Optional[Genre]:
    """Get genre by slug"""
    query = select(Genre).where(and_(Genre.slug == slug, Genre.is_deleted == False))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_featured_content(
    db: AsyncSession,
    pagination: PaginationParams,
    filters: Optional[ContentFilters] = None,
) -> Tuple[List[Content], int]:
    """Get featured content with pagination and filtering"""
    query = select(Content).where(
        and_(
            Content.is_deleted == False,
            Content.is_featured == True,
            Content.status == "published",
        )
    )

    # Apply filters
    if filters:
        query = _apply_content_filters(query, filters)

    # Apply pagination
    query = _apply_pagination(query, pagination, Content)

    # Load genres
    query = query.options(selectinload(Content.genres))

    # Execute query
    result = await db.execute(query)
    contents = result.scalars().all()

    # Get total count
    count_query = select(func.count(Content.id)).where(
        and_(
            Content.is_deleted == False,
            Content.is_featured == True,
            Content.status == "published",
        )
    )

    if filters:
        count_query = _apply_content_filters(count_query, filters)

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return contents, total


async def get_trending_content(
    db: AsyncSession,
    pagination: PaginationParams,
    filters: Optional[ContentFilters] = None,
) -> Tuple[List[Content], int]:
    """Get trending content with pagination and filtering"""
    query = select(Content).where(
        and_(
            Content.is_deleted == False,
            Content.is_trending == True,
            Content.status == "published",
        )
    )

    # Apply filters
    if filters:
        query = _apply_content_filters(query, filters)

    # Apply pagination
    query = _apply_pagination(query, pagination, Content)

    # Load genres
    query = query.options(selectinload(Content.genres))

    # Execute query
    result = await db.execute(query)
    contents = result.scalars().all()

    # Get total count
    count_query = select(func.count(Content.id)).where(
        and_(
            Content.is_deleted == False,
            Content.is_trending == True,
            Content.status == "published",
        )
    )

    if filters:
        count_query = _apply_content_filters(count_query, filters)

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return contents, total


async def get_content_list(
    db: AsyncSession,
    pagination: PaginationParams,
    filters: Optional[ContentFilters] = None,
) -> Tuple[List[Content], int]:
    """Get content list with pagination and filtering"""
    query = select(Content).where(Content.is_deleted == False)

    # Apply filters
    if filters:
        query = _apply_content_filters(query, filters)

    # Apply pagination
    query = _apply_pagination(query, pagination, Content)

    # Load genres
    query = query.options(selectinload(Content.genres))

    # Execute query
    result = await db.execute(query)
    contents = result.scalars().all()

    # Get total count
    count_query = select(func.count(Content.id)).where(Content.is_deleted == False)

    if filters:
        count_query = _apply_content_filters(count_query, filters)

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return contents, total


async def get_genres_list(
    db: AsyncSession,
    pagination: PaginationParams,
    filters: Optional[GenreFilters] = None,
) -> Tuple[List[Genre], int]:
    """Get genres list with pagination and filtering"""
    query = select(Genre).where(Genre.is_deleted == False)

    # Apply filters
    if filters:
        query = _apply_genre_filters(query, filters)

    # Apply pagination
    query = _apply_pagination(query, pagination, Genre)

    # Execute query
    result = await db.execute(query)
    genres = result.scalars().all()

    # Get total count
    count_query = select(func.count(Genre.id)).where(Genre.is_deleted == False)

    if filters:
        count_query = _apply_genre_filters(count_query, filters)

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return genres, total


def _apply_content_filters(query, filters: ContentFilters):
    """Apply content filters to query"""
    if filters.content_type:
        query = query.where(Content.content_type == filters.content_type)

    if filters.status:
        query = query.where(Content.status == filters.status)

    if filters.rating:
        query = query.where(Content.rating == filters.rating)

    if filters.is_featured is not None:
        query = query.where(Content.is_featured == filters.is_featured)

    if filters.is_trending is not None:
        query = query.where(Content.is_trending == filters.is_trending)

    if filters.year:
        query = query.where(func.extract("year", Content.release_date) == filters.year)

    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.where(
            or_(
                Content.title.ilike(search_term),
                Content.description.ilike(search_term),
                Content.tagline.ilike(search_term),
            )
        )

    if filters.genre_ids:
        # Join with content_genres to filter by genre
        query = query.join(ContentGenre).where(
            ContentGenre.genre_id.in_(filters.genre_ids)
        )

    return query


def _apply_genre_filters(query, filters: GenreFilters):
    """Apply genre filters to query"""
    if filters.is_active is not None:
        query = query.where(Genre.is_active == filters.is_active)

    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.where(
            or_(Genre.name.ilike(search_term), Genre.description.ilike(search_term))
        )

    return query


def _apply_pagination(query, pagination: PaginationParams, model_class=Content):
    """Apply pagination to query"""
    # Apply sorting
    sort_field = getattr(model_class, pagination.sort_by, model_class.created_at)
    if pagination.sort_order == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(sort_field)

    # Apply pagination
    offset = (pagination.page - 1) * pagination.size
    query = query.offset(offset).limit(pagination.size)

    return query


def calculate_pagination_info(page: int, size: int, total: int) -> dict:
    """Calculate pagination information"""
    pages = (total + size - 1) // size  # Ceiling division
    has_next = page < pages
    has_prev = page > 1

    return {
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
        "has_next": has_next,
        "has_prev": has_prev,
    }
