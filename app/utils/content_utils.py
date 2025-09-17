from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.config import settings
from app.models.content import (
    Content,
    ContentCast,
    ContentCrew,
    ContentGenre,
    Genre,
    Person,
)
from app.schemas.content import (
    CastFilters,
    ContentFilters,
    CrewFilters,
    GenreFilters,
    PaginationParams,
)


async def get_content_by_id(
    db: AsyncSession, content_id: UUID, include_relationships: bool = True
) -> Optional[Content]:
    """Get content by ID with optional relationship loading"""
    query = select(Content).where(
        and_(Content.id == content_id, Content.is_deleted == False)
    )

    if include_relationships:
        query = query.options(
            selectinload(Content.genres),
            selectinload(Content.cast).selectinload(ContentCast.person),
            selectinload(Content.crew).selectinload(ContentCrew.person),
        )

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_content_detail_optimized(
    db: AsyncSession, content_id: UUID
) -> Optional[Content]:
    """Get content by ID optimized for detail view - loads appropriate relationships based on content type"""
    query = select(Content).where(
        and_(Content.id == content_id, Content.is_deleted == False)
    )

    # Always load genres
    query = query.options(selectinload(Content.genres))

    # Load content-type specific relationships
    from app.models.content import Episode, Season

    query = query.options(
        selectinload(Content.movie_files),  # For movies
        selectinload(Content.seasons).selectinload(Season.episodes),  # For TV series
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_content_crew_cast(
    db: AsyncSession, content_id: UUID
) -> Optional[Content]:
    """Get content with only cast and crew relationships for performance"""
    from app.models.content import ContentCast, ContentCrew, Person

    # First get the content
    content_query = select(Content).where(
        and_(Content.id == content_id, Content.is_deleted == False)
    )
    content_result = await db.execute(content_query)
    content = content_result.scalar_one_or_none()

    if not content:
        return None

    # Manually load cast and crew to avoid recursion
    cast_query = select(ContentCast).where(ContentCast.content_id == content_id)
    cast_result = await db.execute(cast_query)
    cast_items = cast_result.scalars().all()

    crew_query = select(ContentCrew).where(ContentCrew.content_id == content_id)
    crew_result = await db.execute(crew_query)
    crew_items = crew_result.scalars().all()

    # Load people for cast
    if cast_items:
        person_ids = [item.person_id for item in cast_items]
        people_query = select(Person).where(Person.id.in_(person_ids))
        people_result = await db.execute(people_query)
        people = {p.id: p for p in people_result.scalars().all()}

        # Attach people to cast items
        for cast_item in cast_items:
            cast_item.person = people.get(cast_item.person_id)

    # Load people for crew
    if crew_items:
        person_ids = [item.person_id for item in crew_items]
        people_query = select(Person).where(Person.id.in_(person_ids))
        people_result = await db.execute(people_query)
        people = {p.id: p for p in people_result.scalars().all()}

        # Attach people to crew items
        for crew_item in crew_items:
            crew_item.person = people.get(crew_item.person_id)

    # Manually set the relationships
    content.cast = cast_items
    content.crew = crew_items

    return content


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
    """Get content list with pagination and filtering - optimized for different content types"""
    from app.models.content import Episode, Season

    query = select(Content).where(Content.is_deleted == False)

    # Apply filters
    if filters:
        query = _apply_content_filters(query, filters)

    # Apply pagination
    query = _apply_pagination(query, pagination, Content)

    # Load genres for all content
    query = query.options(selectinload(Content.genres))

    # Load content-type specific relationships for list view
    # For movies: load movie_files (basic info only)
    # For TV series: load seasons (basic info only, no episodes)
    query = query.options(
        selectinload(Content.movie_files),  # For movies
        selectinload(
            Content.seasons
        ),  # For TV series (without episodes for performance)
    )

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


async def get_content_cast(
    db: AsyncSession,
    content_id: UUID,
    pagination: PaginationParams,
    filters: CastFilters,
) -> Tuple[List[ContentCast], int]:
    """Get cast for a specific content with pagination and filtering"""
    # Base query
    query = (
        select(ContentCast)
        .join(Person, ContentCast.person_id == Person.id)
        .where(
            and_(
                ContentCast.content_id == content_id,
                Person.is_deleted == False,
            )
        )
    )

    # Apply filters
    if filters.is_main_cast is not None:
        query = query.where(ContentCast.is_main_cast == filters.is_main_cast)

    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.where(
            or_(
                ContentCast.character_name.ilike(search_term),
                Person.name.ilike(search_term),
            )
        )

    if filters.department:
        # For cast, department is typically "Acting" or similar
        query = query.where(
            Person.known_for_department.ilike(f"%{filters.department}%")
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination and sorting
    if pagination.sort_by == "character_name":
        sort_field = ContentCast.character_name
    elif pagination.sort_by == "person_name":
        sort_field = Person.name
    elif pagination.sort_by == "cast_order":
        sort_field = ContentCast.cast_order
    else:
        sort_field = ContentCast.cast_order

    if pagination.sort_order == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(sort_field)

    # Apply pagination
    offset = (pagination.page - 1) * pagination.size
    query = query.offset(offset).limit(pagination.size)

    # Execute query with person relationship
    query = query.options(selectinload(ContentCast.person))
    result = await db.execute(query)
    cast_members = result.scalars().all()

    return cast_members, total


async def get_content_crew(
    db: AsyncSession,
    content_id: UUID,
    pagination: PaginationParams,
    filters: CrewFilters,
) -> Tuple[List[ContentCrew], int]:
    """Get crew for a specific content with pagination and filtering"""
    # Base query
    query = (
        select(ContentCrew)
        .join(Person, ContentCrew.person_id == Person.id)
        .where(
            and_(
                ContentCrew.content_id == content_id,
                Person.is_deleted == False,
            )
        )
    )

    # Apply filters
    if filters.department:
        query = query.where(ContentCrew.department.ilike(f"%{filters.department}%"))

    if filters.job_title:
        query = query.where(ContentCrew.job_title.ilike(f"%{filters.job_title}%"))

    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.where(
            or_(
                ContentCrew.job_title.ilike(search_term),
                ContentCrew.department.ilike(search_term),
                Person.name.ilike(search_term),
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination and sorting
    if pagination.sort_by == "job_title":
        sort_field = ContentCrew.job_title
    elif pagination.sort_by == "department":
        sort_field = ContentCrew.department
    elif pagination.sort_by == "person_name":
        sort_field = Person.name
    elif pagination.sort_by == "credit_order":
        sort_field = ContentCrew.credit_order
    else:
        sort_field = ContentCrew.credit_order

    if pagination.sort_order == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(sort_field)

    # Apply pagination
    offset = (pagination.page - 1) * pagination.size
    query = query.offset(offset).limit(pagination.size)

    # Execute query with person relationship
    query = query.options(selectinload(ContentCrew.person))
    result = await db.execute(query)
    crew_members = result.scalars().all()

    return crew_members, total


async def get_content_cast_crew(
    db: AsyncSession, content_id: UUID
) -> Tuple[List[ContentCast], List[ContentCrew]]:
    """Get both cast and crew for a specific content"""
    # Get cast
    cast_query = (
        select(ContentCast)
        .join(Person, ContentCast.person_id == Person.id)
        .where(
            and_(
                ContentCast.content_id == content_id,
                Person.is_deleted == False,
            )
        )
        .options(selectinload(ContentCast.person))
        .order_by(ContentCast.cast_order)
    )

    # Get crew
    crew_query = (
        select(ContentCrew)
        .join(Person, ContentCrew.person_id == Person.id)
        .where(
            and_(
                ContentCrew.content_id == content_id,
                Person.is_deleted == False,
            )
        )
        .options(selectinload(ContentCrew.person))
        .order_by(ContentCrew.credit_order)
    )

    # Execute both queries
    cast_result = await db.execute(cast_query)
    crew_result = await db.execute(crew_query)

    cast_members = cast_result.scalars().all()
    crew_members = crew_result.scalars().all()

    return cast_members, crew_members
