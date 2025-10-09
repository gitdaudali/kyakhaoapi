from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.config import settings
from app.core.constants import (
    DOCUMENTARY_CONTENT_TYPES,
    MOST_REVIEWED_MIN_RATING,
    MOST_REVIEWED_MIN_REVIEWS,
    MOVIE_CONTENT_TYPES,
    SERIES_CONTENT_TYPES,
)
from app.models.content import (
    Content,
    ContentCast,
    ContentCrew,
    ContentGenre,
    ContentReview,
    ContentType,
    Episode,
    Genre,
    Person,
    Season,
)
from app.models.user import User
from app.schemas.content import (
    CastFilters,
    CastMemberDetail,
    ContentFilters,
    ContentMinimal,
    ContentSection,
    CrewFilters,
    CrewMemberDetail,
    EpisodeMinimal,
    GenreFilters,
    MovieFileMinimal,
    PaginationParams,
    PersonDetail,
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


# Content Discovery Utilities
async def get_featured_content_discovery(
    db: AsyncSession,
    page: int,
    size: int,
    content_type_filter: Optional[str] = None,
    genre_id_filter: Optional[UUID] = None,
) -> Tuple[List[Content], int]:
    """Get featured content for discovery API"""
    # Build base query
    query = select(Content).where(
        and_(
            Content.is_deleted == False,
            Content.is_featured == True,
            Content.status == "published",
        )
    )

    # Apply filters
    if content_type_filter:
        query = query.where(Content.content_type == content_type_filter)

    if genre_id_filter:
        query = query.join(Content.genres).where(Genre.id == genre_id_filter)

    # Get total count
    count_query = select(func.count(Content.id)).where(
        and_(
            Content.is_deleted == False,
            Content.is_featured == True,
            Content.status == "published",
        )
    )

    if content_type_filter:
        count_query = count_query.where(Content.content_type == content_type_filter)

    if genre_id_filter:
        count_query = count_query.join(Content.genres).where(
            Genre.id == genre_id_filter
        )

    count_result = await db.execute(count_query)
    total_items = count_result.scalar() or 0

    # Apply pagination and ordering
    offset = (page - 1) * size
    query = query.order_by(desc(Content.created_at)).offset(offset).limit(size)

    # Load relationships for discovery API
    query = query.options(
        selectinload(Content.movie_files),  # For movies
        selectinload(Content.seasons).selectinload(Season.episodes),  # For TV series
    )

    # Execute query
    result = await db.execute(query)
    contents = result.scalars().all()

    return contents, total_items


async def get_all_genres_for_discovery(db: AsyncSession) -> List[Genre]:
    """Get all active genres for discovery API"""
    query = (
        select(Genre)
        .where(
            and_(
                Genre.is_deleted == False,
                Genre.is_active == True,
            )
        )
        .order_by(Genre.name)
    )

    result = await db.execute(query)
    genres = result.scalars().all()

    return genres


async def get_trending_content_discovery(
    db: AsyncSession,
    page: int,
    size: int,
    content_type_filter: Optional[str] = None,
    genre_id_filter: Optional[UUID] = None,
) -> Tuple[List[Content], int]:
    """Get trending content for discovery API"""
    # Build base query
    query = select(Content).where(
        and_(
            Content.is_deleted == False,
            Content.is_trending == True,
            Content.status == "published",
        )
    )

    # Apply filters
    if content_type_filter:
        query = query.where(Content.content_type == content_type_filter)

    if genre_id_filter:
        query = query.join(Content.genres).where(Genre.id == genre_id_filter)

    # Get total count
    count_query = select(func.count(Content.id)).where(
        and_(
            Content.is_deleted == False,
            Content.is_trending == True,
            Content.status == "published",
        )
    )

    if content_type_filter:
        count_query = count_query.where(Content.content_type == content_type_filter)

    if genre_id_filter:
        count_query = count_query.join(Content.genres).where(
            Genre.id == genre_id_filter
        )

    count_result = await db.execute(count_query)
    total_items = count_result.scalar() or 0

    # Apply pagination and ordering
    offset = (page - 1) * size
    query = (
        query.order_by(desc(Content.total_views), desc(Content.created_at))
        .offset(offset)
        .limit(size)
    )

    # Load relationships for discovery API
    query = query.options(
        selectinload(Content.movie_files),  # For movies
        selectinload(Content.seasons).selectinload(Season.episodes),  # For TV series
    )

    # Execute query
    result = await db.execute(query)
    contents = result.scalars().all()

    return contents, total_items


async def get_all_genres_for_discovery(db: AsyncSession) -> List[Genre]:
    """Get all active genres for discovery API"""
    query = (
        select(Genre)
        .where(
            and_(
                Genre.is_deleted == False,
                Genre.is_active == True,
            )
        )
        .order_by(Genre.name)
    )

    result = await db.execute(query)
    genres = result.scalars().all()

    return genres


async def get_most_reviewed_content_discovery(
    db: AsyncSession,
    page: int,
    size: int,
    content_type_filter: Optional[str] = None,
    genre_id_filter: Optional[UUID] = None,
) -> Tuple[List[Content], int]:
    """Get most reviewed content from last month for discovery API"""
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
                func.count(ContentReview.id) >= MOST_REVIEWED_MIN_REVIEWS,
                func.avg(ContentReview.rating) >= MOST_REVIEWED_MIN_RATING,
            )
        )
    )

    # Apply additional filters
    if content_type_filter:
        query = query.where(Content.content_type == content_type_filter)

    if genre_id_filter:
        query = query.join(Content.genres).where(Genre.id == genre_id_filter)

    # Order by review count (most reviewed first)
    query = query.order_by(desc(func.count(ContentReview.id)))

    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # Load relationships for discovery API
    query = query.options(
        selectinload(Content.movie_files),  # For movies
        selectinload(Content.seasons).selectinload(Season.episodes),  # For TV series
    )

    # Execute query
    result = await db.execute(query)
    contents = result.scalars().all()

    # Get total count with same filters
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
                func.count(ContentReview.id) >= MOST_REVIEWED_MIN_REVIEWS,
                func.avg(ContentReview.rating) >= MOST_REVIEWED_MIN_RATING,
            )
        )
    )

    if content_type_filter:
        count_query = count_query.where(Content.content_type == content_type_filter)

    if genre_id_filter:
        count_query = count_query.join(Content.genres).where(
            Genre.id == genre_id_filter
        )

    count_result = await db.execute(count_query)
    total_items = count_result.scalar() or 0

    return contents, total_items


async def get_all_genres_for_discovery(db: AsyncSession) -> List[Genre]:
    """Get all active genres for discovery API"""
    query = (
        select(Genre)
        .where(
            and_(
                Genre.is_deleted == False,
                Genre.is_active == True,
            )
        )
        .order_by(Genre.name)
    )

    result = await db.execute(query)
    genres = result.scalars().all()

    return genres


async def get_new_releases_content_discovery(
    db: AsyncSession,
    page: int,
    size: int,
    content_type_filter: Optional[str] = None,
    genre_id_filter: Optional[UUID] = None,
) -> Tuple[List[Content], int]:
    """Get new releases content for discovery API"""
    thirty_days_ago = datetime.now().date() - timedelta(days=30)

    # Build base query
    query = select(Content).where(
        and_(
            Content.is_deleted == False,
            Content.status == "published",
            Content.release_date >= thirty_days_ago,
        )
    )

    # Apply filters
    if content_type_filter:
        query = query.where(Content.content_type == content_type_filter)

    if genre_id_filter:
        query = query.join(Content.genres).where(Genre.id == genre_id_filter)

    # Get total count
    count_query = select(func.count(Content.id)).where(
        and_(
            Content.is_deleted == False,
            Content.status == "published",
            Content.release_date >= thirty_days_ago,
        )
    )

    if content_type_filter:
        count_query = count_query.where(Content.content_type == content_type_filter)

    if genre_id_filter:
        count_query = count_query.join(Content.genres).where(
            Genre.id == genre_id_filter
        )

    count_result = await db.execute(count_query)
    total_items = count_result.scalar() or 0

    # Apply pagination and ordering
    offset = (page - 1) * size
    query = (
        query.order_by(desc(Content.release_date), desc(Content.created_at))
        .offset(offset)
        .limit(size)
    )

    # Load relationships for discovery API
    query = query.options(
        selectinload(Content.movie_files),  # For movies
        selectinload(Content.seasons).selectinload(Season.episodes),  # For TV series
    )

    # Execute query
    result = await db.execute(query)
    contents = result.scalars().all()

    return contents, total_items


async def get_all_genres_for_discovery(db: AsyncSession) -> List[Genre]:
    """Get all active genres for discovery API"""
    query = (
        select(Genre)
        .where(
            and_(
                Genre.is_deleted == False,
                Genre.is_active == True,
            )
        )
        .order_by(Genre.name)
    )

    result = await db.execute(query)
    genres = result.scalars().all()

    return genres


# =============================================================================
# DISCOVERY API OPTIMIZATION HELPERS
# =============================================================================


def convert_movie_files_to_minimal_format(movie_files) -> List[MovieFileMinimal]:
    """Convert movie files to minimal format efficiently"""
    return [
        MovieFileMinimal(
            id=file.id,
            quality_level=file.quality_level,
            file_url=file.file_url,
            duration_seconds=file.duration_seconds,
            is_ready=file.is_ready,
        )
        for file in movie_files
    ]


def convert_episodes_to_minimal_format(seasons) -> List[EpisodeMinimal]:
    """Convert first episodes of each season to minimal format efficiently"""
    episode_files = []
    for season in seasons:
        if season.episodes:
            first_episode = season.episodes[0]
            episode_files.append(
                EpisodeMinimal(
                    id=first_episode.id,
                    episode_number=first_episode.episode_number,
                    title=first_episode.title,
                    slug=first_episode.slug,
                    description=first_episode.description,
                    runtime=first_episode.runtime,
                    air_date=first_episode.air_date,
                    thumbnail_url=first_episode.thumbnail_url,
                    views_count=first_episode.views_count,
                    is_available=first_episode.is_available,
                )
            )
    return episode_files


def get_content_media_files(
    content: Content, include_media_files: bool = True
) -> Tuple[List[MovieFileMinimal], List[EpisodeMinimal]]:
    """Get appropriate media files for content based on type and include_media_files flag"""
    if not include_media_files:
        return [], []

    movie_files = []
    episode_files = []

    if content.content_type in MOVIE_CONTENT_TYPES:
        # Movies and anime movies should have movie files
        if content.movie_files:
            movie_files = convert_movie_files_to_minimal_format(content.movie_files)
    elif content.content_type in SERIES_CONTENT_TYPES:
        # TV series should have episode files
        if content.seasons:
            episode_files = convert_episodes_to_minimal_format(content.seasons)
    elif content.content_type in DOCUMENTARY_CONTENT_TYPES:
        # Documentaries can be either single movies or series
        if content.seasons:
            # Documentary series - use episode files
            episode_files = convert_episodes_to_minimal_format(content.seasons)
        elif content.movie_files:
            # Single documentary movie - use movie files
            movie_files = convert_movie_files_to_minimal_format(content.movie_files)

    return movie_files, episode_files


def convert_content_to_minimal_format(
    content: Content, include_media_files: bool = True
) -> ContentMinimal:
    """Convert content to minimal format efficiently"""
    movie_files, episode_files = get_content_media_files(content, include_media_files)

    return ContentMinimal(
        id=content.id,
        title=content.title,
        slug=content.slug,
        description=content.description,
        poster_url=content.poster_url,
        backdrop_url=content.backdrop_url,
        trailer_url=content.trailer_url,
        release_date=content.release_date,
        content_type=content.content_type,
        content_rating=content.content_rating,
        runtime=content.runtime,
        average_rating=content.average_rating,
        total_reviews=content.reviews_count,
        total_views=content.total_views or 0,
        is_featured=content.is_featured,
        is_trending=content.is_trending,
        movie_files=movie_files,
        episode_files=episode_files,
    )


def create_content_section_with_pagination(
    section_name: str,
    content_items: List[ContentMinimal],
    total_items: int,
    page: int,
    page_size: int,
) -> ContentSection:
    """Create content section with pagination info efficiently"""
    offset = (page - 1) * page_size
    has_more = (offset + page_size) < total_items
    next_page = page + 1 if has_more else None

    return ContentSection(
        section_name=section_name,
        items=content_items,
        total_items=total_items,
        has_more=has_more,
        next_page=next_page,
    )


async def get_person_by_id(db: AsyncSession, person_id: UUID) -> Optional[Person]:
    """Get person by ID with all details"""
    try:
        query = select(Person).where(
            and_(Person.id == person_id, Person.is_deleted == False)
        )
        result = await db.execute(query)
        person = result.scalar_one_or_none()
        return person
    except Exception as e:
        print(f"Error getting person by ID: {e}")
        return None


async def get_people_list(
    db: AsyncSession,
    page: int = 1,
    size: int = 10,
    search: Optional[str] = None,
    department: Optional[str] = None,
    nationality: Optional[str] = None,
    is_featured: Optional[bool] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
) -> Tuple[List[Person], int]:
    """Get paginated list of people with filtering"""
    try:
        # Base query
        query = select(Person).where(Person.is_deleted == False)

        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.where(Person.name.ilike(search_term))

        if department:
            query = query.where(Person.known_for_department.ilike(f"%{department}%"))

        if nationality:
            query = query.where(Person.nationality.ilike(f"%{nationality}%"))

        if is_featured is not None:
            query = query.where(Person.is_featured == is_featured)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply sorting
        if sort_by == "name":
            sort_field = Person.name
        elif sort_by == "birth_date":
            sort_field = Person.birth_date
        elif sort_by == "created_at":
            sort_field = Person.created_at
        else:
            sort_field = Person.name

        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(sort_field)

        # Apply pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await db.execute(query)
        people = result.scalars().all()

        return people, total

    except Exception as e:
        print(f"Error getting people list: {e}")
        return [], 0


async def get_genres_with_movies(
    db: AsyncSession,
    pagination: PaginationParams,
    filters: Optional[GenreFilters] = None,
) -> Tuple[List[dict], int]:
    """
    Ultra-fast query to get genres with movie poster URLs only.
    Uses single optimized query with window functions for maximum speed.
    """
    try:
        # Single optimized query using window functions to get genres with movie posters
        from sqlalchemy import text

        # Build the base WHERE clause
        where_conditions = ["g.is_deleted = false", "g.is_active = true"]
        params = {}

        if filters:
            if filters.is_active is not None:
                where_conditions.append("g.is_active = :is_active")
                params["is_active"] = filters.is_active
            if filters.search:
                where_conditions.append(
                    "(g.name ILIKE :search OR g.description ILIKE :search)"
                )
                params["search"] = f"%{filters.search}%"

        where_clause = " AND ".join(where_conditions)

        # Single query with window function to get genres and their movie posters
        query = text(
            f"""
            WITH genre_movies AS (
                SELECT
                    g.id as genre_id,
                    g.name as genre_name,
                    g.slug as genre_slug,
                    g.description as genre_description,
                    g.icon_name as genre_icon_name,
                    g.cover_image_url as genre_cover_image_url,
                    c.poster_url,
                    ROW_NUMBER() OVER (PARTITION BY g.id ORDER BY c.created_at DESC) as rn
                FROM genres g
                LEFT JOIN content_genres cg ON g.id = cg.genre_id
                LEFT JOIN contents c ON cg.content_id = c.id
                    AND c.is_deleted = false
                    AND c.status = 'published'
                    AND c.content_type IN ('movie', 'anime')
                WHERE {where_clause}
            )
            SELECT
                genre_id,
                genre_name,
                genre_slug,
                genre_description,
                genre_icon_name,
                genre_cover_image_url,
                poster_url
            FROM genre_movies
            WHERE rn <= 4
            ORDER BY genre_name, rn
        """
        )

        # Execute the optimized query
        result = await db.execute(query, params)
        rows = result.fetchall()

        # Get total count for pagination
        count_query = text(
            f"""
            SELECT COUNT(DISTINCT g.id)
            FROM genres g
            WHERE {where_clause}
        """
        )
        count_result = await db.execute(count_query, params)
        total = count_result.scalar()

        # Group results by genre
        genres_dict = {}
        for row in rows:
            genre_id = row.genre_id
            if genre_id not in genres_dict:
                genres_dict[genre_id] = {
                    "id": genre_id,
                    "name": row.genre_name,
                    "slug": row.genre_slug,
                    "description": row.genre_description,
                    "icon_name": row.genre_icon_name,
                    "cover_image_url": row.genre_cover_image_url,
                    "movies": [],
                }

            # Add poster URL if it exists
            if row.poster_url:
                genres_dict[genre_id]["movies"].append({"poster_url": row.poster_url})

        # Convert to list and apply pagination
        genres_list = list(genres_dict.values())

        # Apply pagination manually since we're using raw SQL
        start_idx = (pagination.page - 1) * pagination.size
        end_idx = start_idx + pagination.size
        paginated_genres = genres_list[start_idx:end_idx]

        return paginated_genres, total

    except Exception as e:
        print(f"Error getting genres with movies: {e}")
        return [], 0


async def search_content(
    db: AsyncSession,
    pagination: PaginationParams,
    filters: ContentFilters,
    search_query: str,
) -> Tuple[List[dict], int]:
    """
    Ultra-fast content search with minimal data.
    Returns only id, title, poster_url, and trailer_url for maximum speed.
    """
    try:
        from sqlalchemy import text

        # Build WHERE conditions
        where_conditions = ["c.is_deleted = false", "c.status = 'published'"]
        params = {"search_query": f"%{search_query}%"}

        # Add search condition
        where_conditions.append(
            "(c.title ILIKE :search_query OR c.description ILIKE :search_query)"
        )

        # Add filters
        if filters.content_type:
            where_conditions.append("c.content_type = :content_type")
            params["content_type"] = filters.content_type.value

        if filters.status:
            where_conditions.append("c.status = :status")
            params["status"] = filters.status.value

        if filters.rating:
            where_conditions.append("c.content_rating = :rating")
            params["rating"] = filters.rating.value

        if filters.is_featured is not None:
            where_conditions.append("c.is_featured = :is_featured")
            params["is_featured"] = filters.is_featured

        if filters.is_trending is not None:
            where_conditions.append("c.is_trending = :is_trending")
            params["is_trending"] = filters.is_trending

        if filters.year:
            where_conditions.append("EXTRACT(YEAR FROM c.release_date) = :year")
            params["year"] = filters.year

        if filters.genre_ids:
            genre_placeholders = ",".join(
                [f":genre_id_{i}" for i in range(len(filters.genre_ids))]
            )
            where_conditions.append(
                f"c.id IN (SELECT content_id FROM content_genres WHERE genre_id IN ({genre_placeholders}))"
            )
            for i, genre_id in enumerate(filters.genre_ids):
                params[f"genre_id_{i}"] = str(genre_id)

        # Handle new releases filter
        if filters.is_new_release:
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            where_conditions.append("c.release_date >= :new_release_date")
            params["new_release_date"] = thirty_days_ago

        where_clause = " AND ".join(where_conditions)

        # Build ORDER BY clause
        order_by = "c.created_at DESC"  # Default
        if pagination.sort_by == "relevance":
            # For relevance, we could use full-text search ranking, but for now use title similarity
            order_by = "c.title ILIKE :search_query DESC, c.total_views DESC"
        elif pagination.sort_by == "title":
            order_by = f"c.title {pagination.sort_order.upper()}"
        elif pagination.sort_by == "release_date":
            order_by = f"c.release_date {pagination.sort_order.upper()}"
        elif pagination.sort_by == "rating":
            order_by = f"c.average_rating {pagination.sort_order.upper()}"
        elif pagination.sort_by == "views":
            order_by = f"c.total_views {pagination.sort_order.upper()}"

        # Build the main query
        query = text(
            f"""
            SELECT
                c.id,
                c.title,
                c.poster_url,
                c.trailer_url
            FROM contents c
            WHERE {where_clause}
            ORDER BY {order_by}
            LIMIT :limit OFFSET :offset
        """
        )

        # Add pagination parameters
        params["limit"] = pagination.size
        params["offset"] = (pagination.page - 1) * pagination.size

        # Execute query
        result = await db.execute(query, params)
        rows = result.fetchall()

        # Convert to list of dicts
        search_results = []
        for row in rows:
            search_results.append(
                {
                    "id": row.id,
                    "title": row.title,
                    "poster_url": row.poster_url,
                    "trailer_url": row.trailer_url,
                }
            )

        # Get total count
        count_query = text(
            f"""
            SELECT COUNT(*)
            FROM contents c
            WHERE {where_clause}
        """
        )

        # Remove pagination params for count query
        count_params = {k: v for k, v in params.items() if k not in ["limit", "offset"]}
        count_result = await db.execute(count_query, count_params)
        total = count_result.scalar()

        return search_results, total

    except Exception as e:
        return [], 0
