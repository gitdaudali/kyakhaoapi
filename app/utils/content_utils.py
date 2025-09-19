from datetime import date, datetime, timedelta
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
    ContentReview,
    Episode,
    Genre,
    Person,
    Season,
)
from app.models.user import User
from app.schemas.content import (
    CastFilters,
    ContentFilters,
    CrewFilters,
    GenreFilters,
    PaginationParams,
    ReviewFilters,
)


async def get_content_by_id(
    db: AsyncSession, content_id: UUID, include_relationships: bool = True
) -> Optional[Content]:
    """Get content by ID with optional relationship loading"""
    try:
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
    except Exception as e:
        raise Exception(f"Error retrieving content by ID: {str(e)}")


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


async def get_most_reviewed_last_month(
    db: AsyncSession,
    pagination: PaginationParams,
    filters: Optional[ContentFilters] = None,
    min_rating: float = 3.0,
    min_reviews: int = 5,
) -> Tuple[List[Content], int]:
    """Get most reviewed content in the last month with pagination and filtering"""
    try:
        # Calculate date 30 days ago
        thirty_days_ago = datetime.now() - timedelta(days=30)

        # Base query for content with reviews in the last month
        query = (
            select(Content)
            .join(ContentReview, Content.id == ContentReview.content_id)
            .where(
                and_(
                    Content.is_deleted == False,
                    Content.status == "published",
                    ContentReview.created_at >= thirty_days_ago,
                    ContentReview.status == "published",
                )
            )
            .group_by(Content.id)
            .having(
                and_(
                    func.count(ContentReview.id) >= min_reviews,
                    func.avg(ContentReview.rating) >= min_rating,
                )
            )
        )

        # Apply additional filters
        if filters:
            query = _apply_content_filters(query, filters)

        # Order by review count (most reviewed first)
        if pagination.sort_by == "reviews_count":
            query = query.order_by(desc(func.count(ContentReview.id)))
        elif pagination.sort_by == "average_rating":
            query = query.order_by(desc(func.avg(ContentReview.rating)))
        elif pagination.sort_by == "total_views":
            query = query.order_by(desc(Content.total_views))
        else:
            query = query.order_by(desc(func.count(ContentReview.id)))

        # Apply pagination
        query = query.offset((pagination.page - 1) * pagination.size).limit(
            pagination.size
        )

        # Load relationships
        query = query.options(
            selectinload(Content.genres),
            selectinload(Content.movie_files),
            selectinload(Content.seasons),
        )

        # Execute query
        result = await db.execute(query)
        contents = result.scalars().all()

        # Get total count
        count_query = (
            select(func.count(func.distinct(Content.id)))
            .select_from(Content)
            .join(ContentReview, Content.id == ContentReview.content_id)
            .where(
                and_(
                    Content.is_deleted == False,
                    Content.status == "published",
                    ContentReview.created_at >= thirty_days_ago,
                    ContentReview.status == "published",
                )
            )
            .group_by(Content.id)
            .having(
                and_(
                    func.count(ContentReview.id) >= min_reviews,
                    func.avg(ContentReview.rating) >= min_rating,
                )
            )
        )

        if filters:
            count_query = _apply_content_filters(count_query, filters)

        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        return contents, total
    except Exception as e:
        raise Exception(f"Error retrieving most reviewed content: {str(e)}")


async def get_content_list(
    db: AsyncSession,
    pagination: PaginationParams,
    filters: Optional[ContentFilters] = None,
) -> Tuple[List[Content], int]:
    """Get content list with pagination and filtering - optimized for different content types"""
    try:
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
    except Exception as e:
        raise Exception(f"Error retrieving content list: {str(e)}")


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

    if filters.is_new_release is not None:
        if filters.is_new_release:
            # Filter for content released in the last 30 days
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            query = query.where(Content.release_date >= thirty_days_ago)
        else:
            # Filter for content released more than 30 days ago
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            query = query.where(Content.release_date < thirty_days_ago)

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


async def get_content_reviews(
    db: AsyncSession,
    content_id: UUID,
    pagination: PaginationParams,
    filters: ReviewFilters,
) -> Tuple[List[ContentReview], int]:
    """Get reviews for a specific content with pagination and filtering"""
    # Base query
    query = (
        select(ContentReview)
        .join(User, ContentReview.user_id == User.id)
        .where(
            and_(
                ContentReview.content_id == content_id,
                User.is_deleted == False,
                ContentReview.status == "published",
            )
        )
    )

    # Apply filters
    if filters.rating_min is not None:
        query = query.where(ContentReview.rating >= filters.rating_min)

    if filters.rating_max is not None:
        query = query.where(ContentReview.rating <= filters.rating_max)

    if filters.is_featured is not None:
        query = query.where(ContentReview.is_featured == filters.is_featured)

    if filters.language:
        query = query.where(ContentReview.language == filters.language)

    if filters.user_id:
        query = query.where(ContentReview.user_id == filters.user_id)

    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.where(
            or_(
                ContentReview.title.ilike(search_term),
                ContentReview.review_text.ilike(search_term),
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination and sorting
    if pagination.sort_by == "rating":
        sort_field = ContentReview.rating
    elif pagination.sort_by == "helpful_votes":
        sort_field = ContentReview.helpful_votes
    elif pagination.sort_by == "created_at":
        sort_field = ContentReview.created_at
    elif pagination.sort_by == "title":
        sort_field = ContentReview.title
    else:
        sort_field = ContentReview.created_at

    if pagination.sort_order == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(sort_field)

    # Apply pagination
    offset = (pagination.page - 1) * pagination.size
    query = query.offset(offset).limit(pagination.size)

    # Execute query with user relationship
    query = query.options(selectinload(ContentReview.user))
    result = await db.execute(query)
    reviews = result.scalars().all()

    return reviews, total


async def get_review_stats(db: AsyncSession, content_id: UUID) -> dict:
    """Get review statistics for a content"""
    # Total reviews count
    total_reviews_query = select(func.count()).where(
        and_(
            ContentReview.content_id == content_id,
            ContentReview.status == "published",
        )
    )
    total_reviews_result = await db.execute(total_reviews_query)
    total_reviews = total_reviews_result.scalar()

    if total_reviews == 0:
        return {
            "total_reviews": 0,
            "average_rating": None,
            "rating_distribution": {},
            "featured_reviews_count": 0,
            "recent_reviews_count": 0,
        }

    # Average rating
    avg_rating_query = select(func.avg(ContentReview.rating)).where(
        and_(
            ContentReview.content_id == content_id,
            ContentReview.status == "published",
        )
    )
    avg_rating_result = await db.execute(avg_rating_query)
    average_rating = avg_rating_result.scalar()

    # Rating distribution
    rating_dist_query = (
        select(
            ContentReview.rating,
            func.count().label("count"),
        )
        .where(
            and_(
                ContentReview.content_id == content_id,
                ContentReview.status == "published",
            )
        )
        .group_by(ContentReview.rating)
        .order_by(ContentReview.rating)
    )
    rating_dist_result = await db.execute(rating_dist_query)
    rating_distribution = {
        str(row.rating): row.count for row in rating_dist_result.fetchall()
    }

    # Featured reviews count
    featured_query = select(func.count()).where(
        and_(
            ContentReview.content_id == content_id,
            ContentReview.status == "published",
            ContentReview.is_featured == True,
        )
    )
    featured_result = await db.execute(featured_query)
    featured_reviews_count = featured_result.scalar()

    # Recent reviews count (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_query = select(func.count()).where(
        and_(
            ContentReview.content_id == content_id,
            ContentReview.status == "published",
            ContentReview.created_at >= thirty_days_ago,
        )
    )
    recent_result = await db.execute(recent_query)
    recent_reviews_count = recent_result.scalar()

    return {
        "total_reviews": total_reviews,
        "average_rating": round(average_rating, 2) if average_rating else None,
        "rating_distribution": rating_distribution,
        "featured_reviews_count": featured_reviews_count,
        "recent_reviews_count": recent_reviews_count,
    }


async def get_content_review_by_id(
    db: AsyncSession, review_id: UUID
) -> Optional[ContentReview]:
    """Get a specific review by ID"""
    query = (
        select(ContentReview)
        .join(User, ContentReview.user_id == User.id)
        .where(
            and_(
                ContentReview.id == review_id,
                User.is_deleted == False,
                ContentReview.status == "published",
            )
        )
        .options(selectinload(ContentReview.user))
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_review_for_content(
    db: AsyncSession, content_id: UUID, user_id: UUID
) -> Optional[ContentReview]:
    """Get a user's review for specific content"""
    query = (
        select(ContentReview)
        .join(User, ContentReview.user_id == User.id)
        .where(
            and_(
                ContentReview.content_id == content_id,
                ContentReview.user_id == user_id,
                User.is_deleted == False,
            )
        )
        .options(selectinload(ContentReview.user))
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_content_review(
    db: AsyncSession, content_id: UUID, user_id: UUID, review_data: dict
) -> ContentReview:
    """Create a new review for content - user-facing only"""
    # Check if user already has a review for this content
    existing_review = await get_user_review_for_content(db, content_id, user_id)
    if existing_review:
        raise ValueError("User already has a review for this content")

    # Create new review with only user-facing fields
    review = ContentReview(
        content_id=content_id,
        user_id=user_id,
        rating=review_data["rating"],
        title=review_data.get("title"),
        review_text=review_data.get("review_text"),
        language=review_data.get("language", "en"),
        status="published",
        # Admin fields are set to defaults
        is_featured=False,
        helpful_votes=0,
        total_votes=0,
        is_edited=False,
        last_edited_at=None,
    )

    db.add(review)
    await db.commit()  # Commit to get the ID and timestamps

    # Update content review count
    await update_content_review_count(db, content_id)

    # Refresh to get all fields including timestamps
    await db.refresh(review)

    # Load user relationship separately
    user_query = select(User).where(User.id == user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()
    if user:
        review.user = user

    return review


async def update_content_review(
    db: AsyncSession, review_id: UUID, user_id: UUID, review_data: dict
) -> Optional[ContentReview]:
    """Update an existing review - user-facing only"""
    # Get the review with user relationship
    query = (
        select(ContentReview)
        .where(and_(ContentReview.id == review_id, ContentReview.user_id == user_id))
        .options(selectinload(ContentReview.user))
    )
    result = await db.execute(query)
    review = result.scalar_one_or_none()

    if not review:
        return None

    # Update only user-facing fields
    if "rating" in review_data:
        review.rating = review_data["rating"]
    if "title" in review_data:
        review.title = review_data["title"]
    if "review_text" in review_data:
        review.review_text = review_data["review_text"]
    if "language" in review_data:
        review.language = review_data["language"]

    # Mark as edited (this is the only admin field users can affect)
    review.is_edited = True
    review.last_edited_at = datetime.utcnow()

    # Add to session and commit
    db.add(review)
    await db.commit()
    await db.refresh(review)

    return review


async def delete_content_review(
    db: AsyncSession, review_id: UUID, user_id: UUID
) -> bool:
    """Delete a review"""
    # Get the review
    query = select(ContentReview).where(
        and_(ContentReview.id == review_id, ContentReview.user_id == user_id)
    )
    result = await db.execute(query)
    review = result.scalar_one_or_none()

    if not review:
        return False

    content_id = review.content_id

    # Delete the review
    await db.delete(review)
    await db.commit()

    # Update content review count
    await update_content_review_count(db, content_id)

    return True


async def vote_on_review(
    db: AsyncSession, review_id: UUID, user_id: UUID, is_helpful: bool
) -> Optional[ContentReview]:
    """Vote on a review (helpful/not helpful)"""
    # Get the review
    query = select(ContentReview).where(ContentReview.id == review_id)
    result = await db.execute(query)
    review = result.scalar_one_or_none()

    if not review:
        return None

    # Update vote counts
    if is_helpful:
        review.helpful_votes += 1
    review.total_votes += 1

    await db.commit()
    await db.refresh(review, ["user"])

    return review


async def update_content_review_count(db: AsyncSession, content_id: UUID):
    """Update the review count for content"""
    # Count published reviews
    count_query = select(func.count()).where(
        and_(
            ContentReview.content_id == content_id, ContentReview.status == "published"
        )
    )
    count_result = await db.execute(count_query)
    review_count = count_result.scalar()

    # Update content
    content_query = select(Content).where(Content.id == content_id)
    content_result = await db.execute(content_query)
    content = content_result.scalar_one_or_none()

    if content:
        content.reviews_count = review_count
        await db.commit()


async def get_content_review_stats(db: AsyncSession, content_id: UUID) -> dict:
    """Get comprehensive review statistics for content"""
    # Total reviews count
    total_reviews_query = select(func.count()).where(
        and_(
            ContentReview.content_id == content_id, ContentReview.status == "published"
        )
    )
    total_reviews_result = await db.execute(total_reviews_query)
    total_reviews = total_reviews_result.scalar()

    if total_reviews == 0:
        return {
            "total_reviews": 0,
            "average_rating": None,
            "rating_distribution": {},
            "featured_reviews_count": 0,
            "recent_reviews_count": 0,
            "helpful_reviews_count": 0,
        }

    # Average rating
    avg_rating_query = select(func.avg(ContentReview.rating)).where(
        and_(
            ContentReview.content_id == content_id, ContentReview.status == "published"
        )
    )
    avg_rating_result = await db.execute(avg_rating_query)
    average_rating = avg_rating_result.scalar()

    # Rating distribution
    rating_dist_query = (
        select(ContentReview.rating, func.count().label("count"))
        .where(
            and_(
                ContentReview.content_id == content_id,
                ContentReview.status == "published",
            )
        )
        .group_by(ContentReview.rating)
        .order_by(ContentReview.rating)
    )
    rating_dist_result = await db.execute(rating_dist_query)
    rating_distribution = {
        str(row.rating): row.count for row in rating_dist_result.fetchall()
    }

    # Featured reviews count
    featured_query = select(func.count()).where(
        and_(
            ContentReview.content_id == content_id,
            ContentReview.status == "published",
            ContentReview.is_featured == True,
        )
    )
    featured_result = await db.execute(featured_query)
    featured_reviews_count = featured_result.scalar()

    # Recent reviews count (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_query = select(func.count()).where(
        and_(
            ContentReview.content_id == content_id,
            ContentReview.status == "published",
            ContentReview.created_at >= thirty_days_ago,
        )
    )
    recent_result = await db.execute(recent_query)
    recent_reviews_count = recent_result.scalar()

    # Helpful reviews count (reviews with helpful votes)
    helpful_query = select(func.count()).where(
        and_(
            ContentReview.content_id == content_id,
            ContentReview.status == "published",
            ContentReview.helpful_votes > 0,
        )
    )
    helpful_result = await db.execute(helpful_query)
    helpful_reviews_count = helpful_result.scalar()

    return {
        "total_reviews": total_reviews,
        "average_rating": round(average_rating, 2) if average_rating else None,
        "rating_distribution": rating_distribution,
        "featured_reviews_count": featured_reviews_count,
        "recent_reviews_count": recent_reviews_count,
        "helpful_reviews_count": helpful_reviews_count,
    }
