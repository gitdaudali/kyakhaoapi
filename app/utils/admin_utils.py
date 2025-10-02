import time
from typing import List, Optional, Tuple
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlalchemy import and_, delete, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.messages import (
    CONTENT_ALREADY_EXISTS,
    USER_ALREADY_EXISTS,
    USER_CREATED,
    USER_DELETED,
    USER_NOT_FOUND,
    USER_ROLE_UPDATED,
    USER_STATUS_UPDATED,
    USER_UPDATED,
)
from app.models.content import (
    Content,
    ContentCast,
    ContentCrew,
    ContentGenre,
    Genre,
    MovieFile,
    Person,
)
from app.models.streaming import StreamingChannel
from app.models.user import User
from app.schemas.admin import (
    ContentAdminQueryParams,
    GenreAdminQueryParams,
    PersonAdminQueryParams,
    StreamingChannelAdminQueryParams,
    UserAdminQueryParams,
)
from app.utils.s3_utils import delete_file_from_s3, upload_file_to_s3

# =============================================================================
# STREAMING CHANNEL ADMIN UTILS
# =============================================================================


async def create_streaming_channel(
    db: AsyncSession, channel_data: dict
) -> StreamingChannel:
    """
    Create a new streaming channel.

    Args:
        db: Database session
        channel_data: Channel data dictionary

    Returns:
        StreamingChannel: Created channel

    Raises:
        ValueError: If channel with same name already exists
    """
    # Check if channel with same name already exists
    existing_query = select(StreamingChannel).where(
        and_(
            StreamingChannel.name == channel_data["name"],
            StreamingChannel.is_deleted == False,
        )
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise ValueError("Channel with this name already exists")

    # Create new channel
    channel = StreamingChannel(**channel_data)
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    return channel


async def update_streaming_channel(
    db: AsyncSession, channel_id: UUID, update_data: dict
) -> Optional[StreamingChannel]:
    """
    Update a streaming channel.

    Args:
        db: Database session
        channel_id: Channel ID
        update_data: Update data dictionary

    Returns:
        StreamingChannel: Updated channel or None if not found

    Raises:
        ValueError: If channel with same name already exists
    """
    # Get existing channel
    query = select(StreamingChannel).where(
        and_(StreamingChannel.id == channel_id, StreamingChannel.is_deleted == False)
    )
    result = await db.execute(query)
    channel = result.scalar_one_or_none()

    if not channel:
        return None

    # Check if name is being changed and if new name already exists
    if "name" in update_data and update_data["name"] != channel.name:
        existing_query = select(StreamingChannel).where(
            and_(
                StreamingChannel.name == update_data["name"],
                StreamingChannel.id != channel_id,
                StreamingChannel.is_deleted == False,
            )
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise ValueError("Channel with this name already exists")

    # Update channel
    for key, value in update_data.items():
        if value is not None:
            setattr(channel, key, value)

    await db.commit()
    await db.refresh(channel)
    return channel


async def delete_streaming_channel(db: AsyncSession, channel_id: UUID) -> bool:
    """
    Soft delete a streaming channel.

    Args:
        db: Database session
        channel_id: Channel ID

    Returns:
        bool: True if deleted, False if not found
    """
    query = select(StreamingChannel).where(
        and_(StreamingChannel.id == channel_id, StreamingChannel.is_deleted == False)
    )
    result = await db.execute(query)
    channel = result.scalar_one_or_none()

    if not channel:
        return False

    channel.is_deleted = True
    await db.commit()
    return True


async def get_streaming_channels_admin_list(
    db: AsyncSession,
    query_params: StreamingChannelAdminQueryParams,
) -> Tuple[List[StreamingChannel], int]:
    """
    Get paginated list of streaming channels for admin with optimized queries.

    Args:
        db: Database session
        query_params: Query parameters for filtering and pagination

    Returns:
        Tuple of (channels_list, total_count)
    """
    # Build base query
    query = select(StreamingChannel).where(StreamingChannel.is_deleted == False)

    # Apply filters
    if query_params.search:
        search_term = f"%{query_params.search.lower()}%"
        query = query.where(
            or_(
                StreamingChannel.name.ilike(search_term),
                StreamingChannel.description.ilike(search_term),
            )
        )

    if query_params.category:
        query = query.where(StreamingChannel.category == query_params.category)

    if query_params.language:
        query = query.where(StreamingChannel.language == query_params.language)

    if query_params.country:
        query = query.where(StreamingChannel.country == query_params.country)

    if query_params.quality:
        query = query.where(StreamingChannel.quality == query_params.quality)

    # Get total count before pagination
    count_query = select(func.count(StreamingChannel.id)).where(
        StreamingChannel.is_deleted == False
    )

    # Apply the same filters to count query
    if query_params.search:
        search_term = f"%{query_params.search.lower()}%"
        count_query = count_query.where(
            or_(
                StreamingChannel.name.ilike(search_term),
                StreamingChannel.description.ilike(search_term),
            )
        )

    if query_params.category:
        count_query = count_query.where(
            StreamingChannel.category == query_params.category
        )

    if query_params.language:
        count_query = count_query.where(
            StreamingChannel.language == query_params.language
        )

    if query_params.country:
        count_query = count_query.where(
            StreamingChannel.country == query_params.country
        )

    if query_params.quality:
        count_query = count_query.where(
            StreamingChannel.quality == query_params.quality
        )

    total_count = await db.scalar(count_query)

    # Apply sorting
    sort_field = getattr(
        StreamingChannel, query_params.sort_by, StreamingChannel.created_at
    )
    if query_params.sort_order.lower() == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(sort_field)

    # Apply pagination
    offset = (query_params.page - 1) * query_params.size
    query = query.offset(offset).limit(query_params.size)

    # Execute query
    result = await db.execute(query)
    channels = result.scalars().all()

    return channels, total_count


async def get_streaming_channel_admin_by_id(
    db: AsyncSession, channel_id: UUID
) -> Optional[StreamingChannel]:
    """
    Get streaming channel by ID for admin.

    Args:
        db: Database session
        channel_id: Channel ID

    Returns:
        StreamingChannel or None
    """
    query = select(StreamingChannel).where(
        and_(StreamingChannel.id == channel_id, StreamingChannel.is_deleted == False)
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def test_stream_url(stream_url: str) -> dict:
    """
    Test if a stream URL is accessible.

    Args:
        stream_url: Stream URL to test

    Returns:
        dict: Test result with accessibility status and response time
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            start_time = time.time()
            response = await client.head(stream_url)
            end_time = time.time()

            response_time_ms = int((end_time - start_time) * 1000)

            return {
                "is_accessible": response.status_code < 400,
                "response_time_ms": response_time_ms,
                "error_message": None
                if response.status_code < 400
                else f"HTTP {response.status_code}",
                "stream_info": {
                    "content_type": response.headers.get("content-type"),
                    "content_length": response.headers.get("content-length"),
                }
                if response.status_code < 400
                else None,
            }
    except Exception as e:
        return {
            "is_accessible": False,
            "response_time_ms": None,
            "error_message": str(e),
            "stream_info": None,
        }


# =============================================================================
# GENRE ADMIN UTILS
# =============================================================================


async def create_genre(db: AsyncSession, genre_data: dict) -> Genre:
    """
    Create a new genre.

    Args:
        db: Database session
        genre_data: Genre data dictionary

    Returns:
        Genre: Created genre

    Raises:
        ValueError: If genre with same name or slug already exists
    """
    # Check if genre with same name already exists
    existing_name_query = select(Genre).where(
        and_(Genre.name == genre_data["name"], Genre.is_deleted == False)
    )
    existing_name_result = await db.execute(existing_name_query)
    if existing_name_result.scalar_one_or_none():
        raise ValueError("Genre with this name already exists")

    # Check if genre with same slug already exists
    existing_slug_query = select(Genre).where(
        and_(Genre.slug == genre_data["slug"], Genre.is_deleted == False)
    )
    existing_slug_result = await db.execute(existing_slug_query)
    if existing_slug_result.scalar_one_or_none():
        raise ValueError("Genre with this slug already exists")

    # Create new genre
    genre = Genre(**genre_data)
    db.add(genre)
    await db.commit()
    await db.refresh(genre)
    return genre


async def update_genre(
    db: AsyncSession, genre_id: UUID, update_data: dict
) -> Optional[Genre]:
    """
    Update a genre.

    Args:
        db: Database session
        genre_id: Genre ID
        update_data: Update data dictionary

    Returns:
        Genre: Updated genre or None if not found

    Raises:
        ValueError: If genre with same name or slug already exists
    """
    # Get existing genre
    query = select(Genre).where(and_(Genre.id == genre_id, Genre.is_deleted == False))
    result = await db.execute(query)
    genre = result.scalar_one_or_none()

    if not genre:
        return None

    # Check if name is being changed and if new name already exists
    if "name" in update_data and update_data["name"] != genre.name:
        existing_name_query = select(Genre).where(
            and_(
                Genre.name == update_data["name"],
                Genre.id != genre_id,
                Genre.is_deleted == False,
            )
        )
        existing_name_result = await db.execute(existing_name_query)
        if existing_name_result.scalar_one_or_none():
            raise ValueError("Genre with this name already exists")

    # Check if slug is being changed and if new slug already exists
    if "slug" in update_data and update_data["slug"] != genre.slug:
        existing_slug_query = select(Genre).where(
            and_(
                Genre.slug == update_data["slug"],
                Genre.id != genre_id,
                Genre.is_deleted == False,
            )
        )
        existing_slug_result = await db.execute(existing_slug_query)
        if existing_slug_result.scalar_one_or_none():
            raise ValueError("Genre with this slug already exists")

    # Update genre
    for key, value in update_data.items():
        if value is not None:
            setattr(genre, key, value)

    await db.commit()
    await db.refresh(genre)
    return genre


async def delete_genre(db: AsyncSession, genre_id: UUID) -> bool:
    """
    Soft delete a genre.

    Args:
        db: Database session
        genre_id: Genre ID

    Returns:
        bool: True if deleted, False if not found
    """
    query = select(Genre).where(and_(Genre.id == genre_id, Genre.is_deleted == False))
    result = await db.execute(query)
    genre = result.scalar_one_or_none()

    if not genre:
        return False

    genre.is_deleted = True
    await db.commit()
    return True


async def get_genres_admin_list(
    db: AsyncSession,
    query_params: GenreAdminQueryParams,
) -> Tuple[List[Genre], int]:
    """
    Get paginated list of genres for admin with optimized queries.

    Args:
        db: Database session
        query_params: Query parameters for filtering and pagination

    Returns:
        Tuple of (genres_list, total_count)
    """
    # Build base query
    query = select(Genre).where(Genre.is_deleted == False)

    # Apply filters
    if query_params.search:
        search_term = f"%{query_params.search.lower()}%"
        query = query.where(
            or_(
                Genre.name.ilike(search_term),
                Genre.description.ilike(search_term),
            )
        )

    if query_params.is_active is not None:
        query = query.where(Genre.is_active == query_params.is_active)

    if query_params.is_featured is not None:
        query = query.where(Genre.is_featured == query_params.is_featured)

    if query_params.parent_genre_id:
        query = query.where(Genre.parent_genre_id == query_params.parent_genre_id)

    # Get total count before pagination
    count_query = select(func.count(Genre.id)).where(Genre.is_deleted == False)

    # Apply the same filters to count query
    if query_params.search:
        search_term = f"%{query_params.search.lower()}%"
        count_query = count_query.where(
            or_(
                Genre.name.ilike(search_term),
                Genre.description.ilike(search_term),
            )
        )

    if query_params.is_active is not None:
        count_query = count_query.where(Genre.is_active == query_params.is_active)

    if query_params.is_featured is not None:
        count_query = count_query.where(Genre.is_featured == query_params.is_featured)

    if query_params.parent_genre_id:
        count_query = count_query.where(
            Genre.parent_genre_id == query_params.parent_genre_id
        )

    total_count = await db.scalar(count_query)

    # Apply sorting
    sort_field = getattr(Genre, query_params.sort_by, Genre.created_at)
    if query_params.sort_order.lower() == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(sort_field)

    # Apply pagination
    offset = (query_params.page - 1) * query_params.size
    query = query.offset(offset).limit(query_params.size)

    # Execute query
    result = await db.execute(query)
    genres = result.scalars().all()

    return genres, total_count


async def get_genre_admin_by_id(db: AsyncSession, genre_id: UUID) -> Optional[Genre]:
    """
    Get genre by ID for admin.

    Args:
        db: Database session
        genre_id: Genre ID

    Returns:
        Genre or None
    """
    query = select(Genre).where(and_(Genre.id == genre_id, Genre.is_deleted == False))

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def toggle_genre_featured(db: AsyncSession, genre_id: UUID) -> Optional[Genre]:
    """
    Toggle genre featured status.

    Args:
        db: Database session
        genre_id: Genre ID

    Returns:
        Genre: Updated genre or None if not found
    """
    query = select(Genre).where(and_(Genre.id == genre_id, Genre.is_deleted == False))
    result = await db.execute(query)
    genre = result.scalar_one_or_none()

    if not genre:
        return None

    genre.is_featured = not genre.is_featured
    await db.commit()
    await db.refresh(genre)
    return genre


# =============================================================================
# CONTENT ADMIN UTILS
# =============================================================================


async def create_content(db: AsyncSession, content_data: dict) -> Content:
    """
    Create new content.

    Args:
        db: Database session
        content_data: Content data dictionary

    Returns:
        Content: Created content

    Raises:
        ValueError: If content with same title or slug already exists
    """
    # Check if content with same title already exists
    existing_title_query = select(Content).where(
        and_(Content.title == content_data["title"], Content.is_deleted == False)
    )
    existing_title_result = await db.execute(existing_title_query)
    if existing_title_result.scalar_one_or_none():
        raise ValueError("Content with this title already exists")

    # Check if content with same slug already exists
    existing_slug_query = select(Content).where(
        and_(Content.slug == content_data["slug"], Content.is_deleted == False)
    )
    existing_slug_result = await db.execute(existing_slug_query)
    if existing_slug_result.scalar_one_or_none():
        raise ValueError("Content with this slug already exists")

    # Extract genre IDs if provided
    genre_ids = content_data.pop("genre_ids", [])

    # Create new content
    content = Content(**content_data)
    db.add(content)
    await db.commit()
    await db.refresh(content)

    # Add genres if provided
    if genre_ids:
        genres_query = select(Genre).where(
            and_(Genre.id.in_(genre_ids), Genre.is_deleted == False)
        )
        genres_result = await db.execute(genres_query)
        genres = genres_result.scalars().all()
        content.genres = genres
        await db.commit()
        await db.refresh(content)

    return content


async def update_content(
    db: AsyncSession, content_id: UUID, update_data: dict
) -> Optional[Content]:
    """
    Update content.

    Args:
        db: Database session
        content_id: Content ID
        update_data: Update data dictionary

    Returns:
        Content: Updated content or None if not found

    Raises:
        ValueError: If content with same title or slug already exists
    """
    # Get existing content
    query = select(Content).where(
        and_(Content.id == content_id, Content.is_deleted == False)
    )
    result = await db.execute(query)
    content = result.scalar_one_or_none()

    if not content:
        return None

    # Check if title is being changed and if new title already exists
    if "title" in update_data and update_data["title"] != content.title:
        existing_title_query = select(Content).where(
            and_(
                Content.title == update_data["title"],
                Content.id != content_id,
                Content.is_deleted == False,
            )
        )
        existing_title_result = await db.execute(existing_title_query)
        if existing_title_result.scalar_one_or_none():
            raise ValueError("Content with this title already exists")

    # Check if slug is being changed and if new slug already exists
    if "slug" in update_data and update_data["slug"] != content.slug:
        existing_slug_query = select(Content).where(
            and_(
                Content.slug == update_data["slug"],
                Content.id != content_id,
                Content.is_deleted == False,
            )
        )
        existing_slug_result = await db.execute(existing_slug_query)
        if existing_slug_result.scalar_one_or_none():
            raise ValueError("Content with this slug already exists")

    # Extract genre IDs if provided
    genre_ids = update_data.pop("genre_ids", None)

    # Update content
    for key, value in update_data.items():
        if value is not None:
            setattr(content, key, value)

    # Update genres if provided
    if genre_ids is not None:
        genres_query = select(Genre).where(
            and_(Genre.id.in_(genre_ids), Genre.is_deleted == False)
        )
        genres_result = await db.execute(genres_query)
        genres = genres_result.scalars().all()
        content.genres = genres

    await db.commit()
    await db.refresh(content)
    return content


async def delete_content(db: AsyncSession, content_id: UUID) -> bool:
    """
    Soft delete content.

    Args:
        db: Database session
        content_id: Content ID

    Returns:
        bool: True if deleted, False if not found
    """
    query = select(Content).where(
        and_(Content.id == content_id, Content.is_deleted == False)
    )
    result = await db.execute(query)
    content = result.scalar_one_or_none()

    if not content:
        return False

    content.is_deleted = True
    await db.commit()
    return True


async def get_content_admin_list(
    db: AsyncSession,
    query_params: ContentAdminQueryParams,
) -> Tuple[List[Content], int]:
    """
    Get paginated list of content for admin with optimized queries.

    Args:
        db: Database session
        query_params: Query parameters for filtering and pagination

    Returns:
        Tuple of (content_list, total_count)
    """
    # Build base query with genres
    query = (
        select(Content)
        .where(Content.is_deleted == False)
        .options(selectinload(Content.genres))
    )

    # Apply filters
    if query_params.search:
        search_term = f"%{query_params.search.lower()}%"
        query = query.where(
            or_(
                Content.title.ilike(search_term),
                Content.description.ilike(search_term),
                Content.tagline.ilike(search_term),
            )
        )

    if query_params.content_type:
        query = query.where(Content.content_type == query_params.content_type)

    if query_params.status:
        query = query.where(Content.status == query_params.status)

    if query_params.is_featured is not None:
        query = query.where(Content.is_featured == query_params.is_featured)

    if query_params.is_trending is not None:
        query = query.where(Content.is_trending == query_params.is_trending)

    if query_params.is_new_release is not None:
        query = query.where(Content.is_new_release == query_params.is_new_release)

    if query_params.is_premium is not None:
        query = query.where(Content.is_premium == query_params.is_premium)

    if query_params.genre_id:
        query = query.join(Content.genres).where(Genre.id == query_params.genre_id)

    # Get total count before pagination
    count_query = select(func.count(Content.id)).where(Content.is_deleted == False)

    # Apply the same filters to count query
    if query_params.search:
        search_term = f"%{query_params.search.lower()}%"
        count_query = count_query.where(
            or_(
                Content.title.ilike(search_term),
                Content.description.ilike(search_term),
                Content.tagline.ilike(search_term),
            )
        )

    if query_params.content_type:
        count_query = count_query.where(
            Content.content_type == query_params.content_type
        )

    if query_params.status:
        count_query = count_query.where(Content.status == query_params.status)

    if query_params.is_featured is not None:
        count_query = count_query.where(Content.is_featured == query_params.is_featured)

    if query_params.is_trending is not None:
        count_query = count_query.where(Content.is_trending == query_params.is_trending)

    if query_params.is_new_release is not None:
        count_query = count_query.where(
            Content.is_new_release == query_params.is_new_release
        )

    if query_params.is_premium is not None:
        count_query = count_query.where(Content.is_premium == query_params.is_premium)

    if query_params.genre_id:
        count_query = count_query.join(Content.genres).where(
            Genre.id == query_params.genre_id
        )

    total_count = await db.scalar(count_query)

    # Apply sorting
    sort_field = getattr(Content, query_params.sort_by, Content.created_at)
    if query_params.sort_order.lower() == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(sort_field)

    # Apply pagination
    offset = (query_params.page - 1) * query_params.size
    query = query.offset(offset).limit(query_params.size)

    # Execute query
    result = await db.execute(query)
    content_list = result.scalars().all()

    return content_list, total_count


async def get_content_admin_by_id(
    db: AsyncSession, content_id: UUID
) -> Optional[Content]:
    """
    Get content by ID for admin.

    Args:
        db: Database session
        content_id: Content ID

    Returns:
        Content or None
    """
    query = (
        select(Content)
        .where(Content.id == content_id)
        .options(
            selectinload(Content.genres),
            selectinload(Content.seasons),
            selectinload(Content.cast),
            selectinload(Content.crew),
            selectinload(Content.movie_files),
        )
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def toggle_content_featured(
    db: AsyncSession, content_id: UUID
) -> Optional[Content]:
    """
    Toggle content featured status.

    Args:
        db: Database session
        content_id: Content ID

    Returns:
        Content: Updated content or None if not found
    """
    query = select(Content).where(
        and_(Content.id == content_id, Content.is_deleted == False)
    )
    result = await db.execute(query)
    content = result.scalar_one_or_none()

    if not content:
        return None

    content.is_featured = not content.is_featured
    await db.commit()
    await db.refresh(content)
    return content


async def toggle_content_trending(
    db: AsyncSession, content_id: UUID
) -> Optional[Content]:
    """
    Toggle content trending status.

    Args:
        db: Database session
        content_id: Content ID

    Returns:
        Content: Updated content or None if not found
    """
    query = select(Content).where(
        and_(Content.id == content_id, Content.is_deleted == False)
    )
    result = await db.execute(query)
    content = result.scalar_one_or_none()

    if not content:
        return None

    content.is_trending = not content.is_trending
    await db.commit()
    await db.refresh(content)
    return content


async def publish_content(db: AsyncSession, content_id: UUID) -> Optional[Content]:
    """
    Publish content.

    Args:
        db: Database session
        content_id: Content ID

    Returns:
        Content: Updated content or None if not found
    """
    query = select(Content).where(
        and_(Content.id == content_id, Content.is_deleted == False)
    )
    result = await db.execute(query)
    content = result.scalar_one_or_none()

    if not content:
        return None

    content.status = "published"
    await db.commit()
    await db.refresh(content)
    return content


async def unpublish_content(db: AsyncSession, content_id: UUID) -> Optional[Content]:
    """
    Unpublish content.

    Args:
        db: Database session
        content_id: Content ID

    Returns:
        Content: Updated content or None if not found
    """
    query = select(Content).where(
        and_(Content.id == content_id, Content.is_deleted == False)
    )
    result = await db.execute(query)
    content = result.scalar_one_or_none()

    if not content:
        return None

    content.status = "draft"
    await db.commit()
    await db.refresh(content)
    return content


# =============================================================================
# USER ADMIN UTILS
# =============================================================================


async def get_users_admin_list(
    db: AsyncSession,
    query_params: UserAdminQueryParams,
) -> Tuple[List[User], int]:
    """
    Get paginated list of users for admin with optimized queries.

    Args:
        db: Database session
        query_params: Query parameters for filtering and pagination

    Returns:
        Tuple of (users_list, total_count)
    """
    # Build base query
    query = select(User).where(User.is_deleted == False)

    # Apply filters
    if query_params.search:
        search_term = f"%{query_params.search.lower()}%"
        query = query.where(
            or_(
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
            )
        )

    if query_params.role:
        query = query.where(User.role == query_params.role)

    if query_params.profile_status:
        query = query.where(User.profile_status == query_params.profile_status)

    if query_params.is_active is not None:
        query = query.where(User.is_active == query_params.is_active)

    if query_params.is_staff is not None:
        query = query.where(User.is_staff == query_params.is_staff)

    if query_params.is_superuser is not None:
        query = query.where(User.is_superuser == query_params.is_superuser)

    # Get total count before pagination
    count_query = select(func.count(User.id)).where(User.is_deleted == False)

    # Apply the same filters to count query
    if query_params.search:
        search_term = f"%{query_params.search.lower()}%"
        count_query = count_query.where(
            or_(
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
            )
        )

    if query_params.role:
        count_query = count_query.where(User.role == query_params.role)

    if query_params.profile_status:
        count_query = count_query.where(
            User.profile_status == query_params.profile_status
        )

    if query_params.is_active is not None:
        count_query = count_query.where(User.is_active == query_params.is_active)

    if query_params.is_staff is not None:
        count_query = count_query.where(User.is_staff == query_params.is_staff)

    if query_params.is_superuser is not None:
        count_query = count_query.where(User.is_superuser == query_params.is_superuser)

    total_count = await db.scalar(count_query)

    # Apply sorting
    sort_field = getattr(User, query_params.sort_by, User.created_at)
    if query_params.sort_order.lower() == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(sort_field)

    # Apply pagination
    offset = (query_params.page - 1) * query_params.size
    query = query.offset(offset).limit(query_params.size)

    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()

    return users, total_count


async def get_user_admin_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    Get user by ID for admin.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User or None
    """
    query = select(User).where(and_(User.id == user_id, User.is_deleted == False))

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_user_admin(
    db: AsyncSession, user_id: UUID, update_data: dict
) -> Optional[User]:
    """
    Update user via admin.

    Args:
        db: Database session
        user_id: User ID
        update_data: Update data dictionary

    Returns:
        User: Updated user or None if not found
    """
    query = select(User).where(and_(User.id == user_id, User.is_deleted == False))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None

    # Update user
    for key, value in update_data.items():
        if value is not None:
            setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user


async def suspend_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    Suspend user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User: Updated user or None if not found
    """
    query = select(User).where(and_(User.id == user_id, User.is_deleted == False))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None

    user.profile_status = "suspended"
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user


async def activate_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    Activate user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User: Updated user or None if not found
    """
    query = select(User).where(and_(User.id == user_id, User.is_deleted == False))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None

    user.profile_status = "active"
    user.is_active = True
    await db.commit()
    await db.refresh(user)
    return user


async def ban_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    Ban user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User: Updated user or None if not found
    """
    query = select(User).where(and_(User.id == user_id, User.is_deleted == False))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None

    user.profile_status = "banned"
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user


async def unban_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    Unban user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User: Updated user or None if not found
    """
    query = select(User).where(and_(User.id == user_id, User.is_deleted == False))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None

    user.profile_status = "active"
    user.is_active = True
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user_admin(db: AsyncSession, user_id: UUID) -> bool:
    """
    Soft delete user via admin.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        bool: True if deleted, False if not found
    """
    query = select(User).where(and_(User.id == user_id, User.is_deleted == False))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return False

    user.is_deleted = True
    await db.commit()
    return True


# =============================================================================
# GENRE ADMIN UTILS
# =============================================================================


async def create_genre(db: AsyncSession, genre_data: dict) -> Genre:
    """
    Create a new genre.

    Args:
        db: Database session
        genre_data: Genre data dictionary

    Returns:
        Genre: Created genre

    Raises:
        ValueError: If genre with same name or slug already exists
    """
    # Check if genre with same name already exists
    existing_name_query = select(Genre).where(
        and_(Genre.name == genre_data["name"], Genre.is_deleted == False)
    )
    existing_name_result = await db.execute(existing_name_query)
    if existing_name_result.scalar_one_or_none():
        raise ValueError("Genre with this name already exists")

    # Check if genre with same slug already exists
    existing_slug_query = select(Genre).where(
        and_(Genre.slug == genre_data["slug"], Genre.is_deleted == False)
    )
    existing_slug_result = await db.execute(existing_slug_query)
    if existing_slug_result.scalar_one_or_none():
        raise ValueError("Genre with this slug already exists")

    # Create new genre
    genre = Genre(**genre_data)
    db.add(genre)
    await db.commit()
    await db.refresh(genre)
    return genre


async def get_genres_admin_list(
    db: AsyncSession, query_params: GenreAdminQueryParams
) -> Tuple[List[Genre], int]:
    """
    Get paginated list of genres for admin.

    Args:
        db: Database session
        query_params: Query parameters

    Returns:
        Tuple of (genres list, total count)
    """
    # Build base query
    query = select(Genre).where(Genre.is_deleted == False)

    # Apply filters
    if query_params.search:
        search_filter = or_(
            Genre.name.ilike(f"%{query_params.search}%"),
            Genre.slug.ilike(f"%{query_params.search}%"),
            Genre.description.ilike(f"%{query_params.search}%"),
        )
        query = query.where(search_filter)

    if query_params.is_active is not None:
        query = query.where(Genre.is_active == query_params.is_active)

    if query_params.is_featured is not None:
        query = query.where(Genre.is_featured == query_params.is_featured)

    if query_params.parent_genre_id:
        query = query.where(Genre.parent_genre_id == query_params.parent_genre_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Apply sorting
    if query_params.sort_by == "name":
        sort_column = Genre.name
    elif query_params.sort_by == "slug":
        sort_column = Genre.slug
    elif query_params.sort_by == "content_count":
        sort_column = Genre.content_count
    elif query_params.sort_by == "sort_order":
        sort_column = Genre.sort_order
    else:
        sort_column = Genre.created_at

    if query_params.sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Apply pagination
    offset = (query_params.page - 1) * query_params.size
    query = query.offset(offset).limit(query_params.size)

    # Execute query
    result = await db.execute(query)
    genres = result.scalars().all()

    return genres, total


async def get_genre_admin_by_id(db: AsyncSession, genre_id: UUID) -> Optional[Genre]:
    """
    Get genre by ID for admin.

    Args:
        db: Database session
        genre_id: Genre ID

    Returns:
        Genre or None
    """
    query = select(Genre).where(and_(Genre.id == genre_id, Genre.is_deleted == False))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_genre(
    db: AsyncSession, genre_id: UUID, update_data: dict
) -> Optional[Genre]:
    """
    Update genre.

    Args:
        db: Database session
        genre_id: Genre ID
        update_data: Update data dictionary

    Returns:
        Updated Genre or None if not found

    Raises:
        ValueError: If genre with same name or slug already exists
    """
    # Get existing genre
    genre = await get_genre_admin_by_id(db, genre_id)
    if not genre:
        return None

    # Check for name conflicts if name is being updated
    if "name" in update_data and update_data["name"] != genre.name:
        existing_name_query = select(Genre).where(
            and_(
                Genre.name == update_data["name"],
                Genre.id != genre_id,
                Genre.is_deleted == False,
            )
        )
        existing_name_result = await db.execute(existing_name_query)
        if existing_name_result.scalar_one_or_none():
            raise ValueError("Genre with this name already exists")

    # Check for slug conflicts if slug is being updated
    if "slug" in update_data and update_data["slug"] != genre.slug:
        existing_slug_query = select(Genre).where(
            and_(
                Genre.slug == update_data["slug"],
                Genre.id != genre_id,
                Genre.is_deleted == False,
            )
        )
        existing_slug_result = await db.execute(existing_slug_query)
        if existing_slug_result.scalar_one_or_none():
            raise ValueError("Genre with this slug already exists")

    # Update genre
    for key, value in update_data.items():
        setattr(genre, key, value)

    await db.commit()
    await db.refresh(genre)
    return genre


async def delete_genre(db: AsyncSession, genre_id: UUID) -> bool:
    """
    Soft delete genre.

    Args:
        db: Database session
        genre_id: Genre ID

    Returns:
        bool: True if deleted, False if not found
    """
    genre = await get_genre_admin_by_id(db, genre_id)
    if not genre:
        return False

    # Delete cover image from S3 if exists
    if genre.cover_image_url:
        delete_file_from_s3(genre.cover_image_url)

    genre.is_deleted = True
    await db.commit()
    return True


async def toggle_genre_featured(db: AsyncSession, genre_id: UUID) -> Optional[Genre]:
    """
    Toggle genre featured status.

    Args:
        db: Database session
        genre_id: Genre ID

    Returns:
        Updated Genre or None if not found
    """
    genre = await get_genre_admin_by_id(db, genre_id)
    if not genre:
        return None

    genre.is_featured = not genre.is_featured
    await db.commit()
    await db.refresh(genre)
    return genre


async def upload_genre_cover_image(file, genre_id: UUID) -> str:
    """
    Upload genre cover image to S3.

    Args:
        file: UploadFile object
        genre_id: Genre ID for folder structure

    Returns:
        str: Public URL of uploaded image

    Raises:
        HTTPException: If upload fails
    """
    # Define allowed extensions for genre images
    allowed_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    max_size_mb = 10  # 10MB for cover images

    # Upload to genre-specific folder
    folder = f"genres/{genre_id}/covers"

    try:
        url = await upload_file_to_s3(
            file=file,
            folder=folder,
            allowed_extensions=allowed_extensions,
            max_size_mb=max_size_mb,
        )
        return url
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading genre cover image: {str(e)}",
        )


# =============================================================================
# CONTENT ADMIN UTILS
# =============================================================================


async def create_content(db: AsyncSession, content_data: dict) -> Content:
    """Create new content"""
    try:
        # Check for title/slug conflicts
        existing_title = await db.execute(
            select(Content).where(Content.title == content_data["title"])
        )
        if existing_title.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=CONTENT_ALREADY_EXISTS,
            )

        existing_slug = await db.execute(
            select(Content).where(Content.slug == content_data["slug"])
        )
        if existing_slug.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content with this slug already exists",
            )

        # Extract related data before creating content
        genre_ids = content_data.pop("genre_ids", None)
        movie_files_data = content_data.pop("movie_files", None)
        cast_data = content_data.pop("cast", None)
        crew_data = content_data.pop("crew", None)

        # Create content
        content = Content(**content_data)
        db.add(content)

        # Handle genre associations
        if genre_ids:
            await _associate_content_genres(db, content.id, genre_ids)

        # Handle movie files creation
        if movie_files_data:
            await _create_movie_files(db, content.id, movie_files_data)

        # Handle cast creation
        if cast_data:
            await _create_content_cast(db, content.id, cast_data)

        # Handle crew creation
        if crew_data:
            await _create_content_crew(db, content.id, crew_data)

        # Commit all changes
        await db.commit()
        await db.refresh(content)

        # Refresh with relationships loaded for return
        content_with_relationships = await db.execute(
            select(Content)
            .where(Content.id == content.id)
            .options(
                selectinload(Content.genres),
                selectinload(Content.seasons),
                selectinload(Content.cast),
                selectinload(Content.crew),
                selectinload(Content.movie_files),
            )
        )
        content = content_with_relationships.scalar_one()

        return content
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating content: {str(e)}",
        )


async def get_contents_admin_list(
    db: AsyncSession, query_params: ContentAdminQueryParams
) -> Tuple[List[Content], int]:
    """Get paginated list of content for admin"""
    try:
        # Build query
        query = select(Content)
        count_query = select(func.count(Content.id))

        # Apply filters
        filters = []

        if query_params.search:
            search_filter = or_(
                Content.title.ilike(f"%{query_params.search}%"),
                Content.description.ilike(f"%{query_params.search}%"),
                Content.tagline.ilike(f"%{query_params.search}%"),
            )
            filters.append(search_filter)

        if query_params.content_type:
            filters.append(Content.content_type == query_params.content_type)

        if query_params.status:
            filters.append(Content.status == query_params.status)

        if query_params.is_featured is not None:
            filters.append(Content.is_featured == query_params.is_featured)

        if query_params.is_trending is not None:
            filters.append(Content.is_trending == query_params.is_trending)

        if query_params.is_new_release is not None:
            filters.append(Content.is_new_release == query_params.is_new_release)

        if query_params.is_premium is not None:
            filters.append(Content.is_premium == query_params.is_premium)

        if query_params.genre_id:
            # Join with content_genres table
            query = query.join(ContentGenre).where(
                ContentGenre.genre_id == query_params.genre_id
            )
            count_query = count_query.join(ContentGenre).where(
                ContentGenre.genre_id == query_params.genre_id
            )

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Apply sorting
        sort_column = getattr(Content, query_params.sort_by, Content.created_at)
        if query_params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)

        # Apply pagination
        offset = (query_params.page - 1) * query_params.size
        query = query.offset(offset).limit(query_params.size)

        # Execute queries
        result = await db.execute(
            query.options(
                selectinload(Content.genres),
                selectinload(Content.seasons),
                selectinload(Content.cast),
                selectinload(Content.crew),
                selectinload(Content.movie_files),
            )
        )
        contents = result.scalars().all()

        count_result = await db.execute(count_query)
        total = count_result.scalar()

        return contents, total
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving content list: {str(e)}",
        )


async def update_content(
    db: AsyncSession, content_id: UUID, update_data: dict
) -> Optional[Content]:
    """Update content"""
    try:
        content = await get_content_admin_by_id(db, content_id)
        if not content:
            return None

        # Check for title/slug conflicts (excluding current content)
        if "title" in update_data:
            existing_title = await db.execute(
                select(Content).where(
                    and_(
                        Content.title == update_data["title"], Content.id != content_id
                    )
                )
            )
            if existing_title.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=CONTENT_ALREADY_EXISTS,
                )

        if "slug" in update_data:
            existing_slug = await db.execute(
                select(Content).where(
                    and_(Content.slug == update_data["slug"], Content.id != content_id)
                )
            )
            if existing_slug.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Content with this slug already exists",
                )

        # Update content fields
        for field, value in update_data.items():
            if field != "genre_ids" and hasattr(content, field):
                setattr(content, field, value)

        # Handle genre associations
        if "genre_ids" in update_data:
            await _associate_content_genres(db, content_id, update_data["genre_ids"])

        await db.commit()
        await db.refresh(content)
        return content
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating content: {str(e)}",
        )


async def delete_content(db: AsyncSession, content_id: UUID) -> bool:
    """Soft delete content"""
    try:
        content = await get_content_admin_by_id(db, content_id)
        if not content:
            return False

        # Soft delete by updating status
        content.status = "archived"
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting content: {str(e)}",
        )


async def toggle_content_featured(
    db: AsyncSession, content_id: UUID
) -> Optional[Content]:
    """Toggle content featured status"""
    try:
        content = await get_content_admin_by_id(db, content_id)
        if not content:
            return None

        content.is_featured = not content.is_featured
        await db.commit()
        await db.refresh(content)
        return content
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling content featured status: {str(e)}",
        )


async def toggle_content_trending(
    db: AsyncSession, content_id: UUID
) -> Optional[Content]:
    """Toggle content trending status"""
    try:
        content = await get_content_admin_by_id(db, content_id)
        if not content:
            return None

        content.is_trending = not content.is_trending
        await db.commit()
        await db.refresh(content)
        return content
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling content trending status: {str(e)}",
        )


async def publish_content(db: AsyncSession, content_id: UUID) -> Optional[Content]:
    """Publish content"""
    try:
        content = await get_content_admin_by_id(db, content_id)
        if not content:
            return None

        content.status = "published"
        await db.commit()
        await db.refresh(content)
        return content
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error publishing content: {str(e)}",
        )


async def unpublish_content(db: AsyncSession, content_id: UUID) -> Optional[Content]:
    """Unpublish content"""
    try:
        content = await get_content_admin_by_id(db, content_id)
        if not content:
            return None

        content.status = "draft"
        await db.commit()
        await db.refresh(content)
        return content
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error unpublishing content: {str(e)}",
        )


async def _associate_content_genres(
    db: AsyncSession, content_id: UUID, genre_ids: List[UUID]
):
    """Associate content with genres"""
    try:
        # Remove existing associations
        await db.execute(
            delete(ContentGenre).where(ContentGenre.content_id == content_id)
        )

        # Add new associations
        for i, genre_id in enumerate(genre_ids):
            content_genre = ContentGenre(
                content_id=content_id,
                genre_id=genre_id,
                is_primary=(i == 0),  # First genre is primary
                relevance_score=1.0 - (i * 0.1),  # Decreasing relevance
            )
            db.add(content_genre)

        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error associating content with genres: {str(e)}",
        )


async def _create_movie_files(
    db: AsyncSession, content_id: UUID, movie_files_data: List[dict]
) -> None:
    """
    Create movie files for content.

    Args:
        db: Database session
        content_id: Content ID
        movie_files_data: List of movie file data dictionaries
    """
    try:
        for movie_file_data in movie_files_data:
            # Add content_id to movie file data
            movie_file_data["content_id"] = content_id

            # Create movie file
            movie_file = MovieFile(**movie_file_data)
            db.add(movie_file)

        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating movie files: {str(e)}",
        )


async def _create_content_cast(
    db: AsyncSession, content_id: UUID, cast_data: List[dict]
) -> None:
    """
    Create cast members for content.

    Args:
        db: Database session
        content_id: Content ID
        cast_data: List of cast member data dictionaries
    """
    try:
        for cast_member_data in cast_data:
            # Add content_id to cast data
            cast_member_data["content_id"] = content_id

            # Create cast member
            cast_member = ContentCast(**cast_member_data)
            db.add(cast_member)

        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating cast members: {str(e)}",
        )


async def _create_content_crew(
    db: AsyncSession, content_id: UUID, crew_data: List[dict]
) -> None:
    """
    Create crew members for content.

    Args:
        db: Database session
        content_id: Content ID
        crew_data: List of crew member data dictionaries
    """
    try:
        for crew_member_data in crew_data:
            # Add content_id to crew data
            crew_member_data["content_id"] = content_id

            # Create crew member
            crew_member = ContentCrew(**crew_member_data)
            db.add(crew_member)

        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating crew members: {str(e)}",
        )


# =============================================================================
# USER ADMIN UTILS
# =============================================================================


async def create_user(db: AsyncSession, user_data: dict) -> User:
    """Create new user"""
    try:
        # Check for email conflicts
        existing_email = await db.execute(
            select(User).where(User.email == user_data["email"])
        )
        if existing_email.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=USER_ALREADY_EXISTS,
            )

        # Hash password if provided
        if user_data.get("password"):
            from app.core.auth import get_password_hash

            user_data["password"] = get_password_hash(user_data["password"])

        # Create user
        user = User(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )


async def get_users_admin_list(
    db: AsyncSession, query_params: UserAdminQueryParams
) -> Tuple[List[User], int]:
    """Get paginated list of users for admin"""
    try:
        # Build query
        query = select(User).where(User.is_deleted == False)
        count_query = select(func.count(User.id)).where(User.is_deleted == False)

        # Apply filters
        if query_params.search:
            search_term = f"%{query_params.search}%"
            query = query.where(
                or_(
                    User.email.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                )
            )
            count_query = count_query.where(
                or_(
                    User.email.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                )
            )

        if query_params.role:
            query = query.where(User.role == query_params.role)
            count_query = count_query.where(User.role == query_params.role)

        if query_params.profile_status:
            query = query.where(User.profile_status == query_params.profile_status)
            count_query = count_query.where(
                User.profile_status == query_params.profile_status
            )

        if query_params.is_active is not None:
            query = query.where(User.is_active == query_params.is_active)
            count_query = count_query.where(User.is_active == query_params.is_active)

        if query_params.is_staff is not None:
            query = query.where(User.is_staff == query_params.is_staff)
            count_query = count_query.where(User.is_staff == query_params.is_staff)

        if query_params.is_superuser is not None:
            query = query.where(User.is_superuser == query_params.is_superuser)
            count_query = count_query.where(
                User.is_superuser == query_params.is_superuser
            )

        if query_params.signup_type:
            query = query.where(User.signup_type == query_params.signup_type)
            count_query = count_query.where(
                User.signup_type == query_params.signup_type
            )

        # Apply sorting
        sort_column = getattr(User, query_params.sort_by, User.created_at)
        if query_params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)

        # Apply pagination
        offset = (query_params.page - 1) * query_params.size
        query = query.offset(offset).limit(query_params.size)

        # Execute queries
        result = await db.execute(query)
        users = result.scalars().all()

        count_result = await db.execute(count_query)
        total = count_result.scalar()

        return users, total
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users list: {str(e)}",
        )


async def get_user_admin_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    Get user by ID for admin.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User or None
    """
    query = select(User).where(and_(User.id == user_id, User.is_deleted == False))

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_user(
    db: AsyncSession, user_id: UUID, update_data: dict
) -> Optional[User]:
    """Update user"""
    try:
        # Get user
        user = await get_user_admin_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )

        # Check for email conflicts if email is being updated
        if "email" in update_data and update_data["email"] != user.email:
            existing_email = await db.execute(
                select(User).where(User.email == update_data["email"])
            )
            if existing_email.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=USER_ALREADY_EXISTS,
                )

        # Hash password if provided
        if update_data.get("password"):
            from app.core.auth import get_password_hash

            update_data["password"] = get_password_hash(update_data["password"])

        # Update user
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        await db.commit()
        await db.refresh(user)
        return user
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}",
        )


async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
    """Delete user (soft delete)"""
    try:
        user = await get_user_admin_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )

        # Soft delete
        user.is_deleted = True
        await db.commit()
        return True
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}",
        )


async def toggle_user_active(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Toggle user active status"""
    try:
        user = await get_user_admin_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )

        user.is_active = not user.is_active
        await db.commit()
        await db.refresh(user)
        return user
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling user active status: {str(e)}",
        )


async def update_user_role(
    db: AsyncSession, user_id: UUID, role: str
) -> Optional[User]:
    """Update user role"""
    try:
        user = await get_user_admin_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )

        user.role = role
        await db.commit()
        await db.refresh(user)
        return user
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user role: {str(e)}",
        )


async def update_user_status(
    db: AsyncSession, user_id: UUID, status: str
) -> Optional[User]:
    """Update user profile status"""
    try:
        user = await get_user_admin_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )

        user.profile_status = status
        await db.commit()
        await db.refresh(user)
        return user
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user status: {str(e)}",
        )


# =============================================================================
# PEOPLE ADMIN UTILS
# =============================================================================


async def create_person(db: AsyncSession, person_data: dict) -> Person:
    """Create new person"""
    try:
        # Check for name/slug conflicts
        existing_name = await db.execute(
            select(Person).where(Person.name == person_data["name"])
        )
        if existing_name.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Person with this name already exists",
            )

        existing_slug = await db.execute(
            select(Person).where(Person.slug == person_data["slug"])
        )
        if existing_slug.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Person with this slug already exists",
            )

        # Create person
        person = Person(**person_data)
        db.add(person)
        await db.commit()
        await db.refresh(person)

        return person
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating person: {str(e)}",
        )


async def get_people_admin_list(
    db: AsyncSession, query_params: PersonAdminQueryParams
) -> Tuple[List[Person], int]:
    """Get paginated list of people for admin"""
    try:
        # Build base query
        query = select(Person)

        # Apply filters
        if query_params.search:
            search_term = f"%{query_params.search}%"
            query = query.where(
                or_(
                    Person.name.ilike(search_term),
                    Person.biography.ilike(search_term),
                    Person.birth_place.ilike(search_term),
                    Person.nationality.ilike(search_term),
                )
            )

        if query_params.is_verified is not None:
            query = query.where(Person.is_verified == query_params.is_verified)

        if query_params.is_featured is not None:
            query = query.where(Person.is_featured == query_params.is_featured)

        if query_params.known_for_department:
            query = query.where(
                Person.known_for_department == query_params.known_for_department
            )

        if query_params.nationality:
            query = query.where(Person.nationality == query_params.nationality)

        if query_params.gender:
            query = query.where(Person.gender == query_params.gender)

        # Apply sorting
        sort_column = getattr(Person, query_params.sort_by, Person.created_at)
        if query_params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)

        # Get total count before pagination
        count_query = select(func.count(Person.id))

        # Apply the same filters to count query
        if query_params.search:
            search_term = f"%{query_params.search}%"
            count_query = count_query.where(
                or_(
                    Person.name.ilike(search_term),
                    Person.biography.ilike(search_term),
                    Person.birth_place.ilike(search_term),
                    Person.nationality.ilike(search_term),
                )
            )

        if query_params.is_verified is not None:
            count_query = count_query.where(
                Person.is_verified == query_params.is_verified
            )

        if query_params.is_featured is not None:
            count_query = count_query.where(
                Person.is_featured == query_params.is_featured
            )

        if query_params.known_for_department:
            count_query = count_query.where(
                Person.known_for_department == query_params.known_for_department
            )

        if query_params.nationality:
            count_query = count_query.where(
                Person.nationality == query_params.nationality
            )

        if query_params.gender:
            count_query = count_query.where(Person.gender == query_params.gender)

        total_count = await db.scalar(count_query)

        # Apply pagination
        offset = (query_params.page - 1) * query_params.size
        query = query.offset(offset).limit(query_params.size)

        # Execute query with relationships
        result = await db.execute(
            query.options(
                selectinload(Person.content_cast),
                selectinload(Person.content_crew),
            )
        )
        people = result.scalars().all()

        return people, total_count
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving people list: {str(e)}",
        )


async def get_person_admin_by_id(db: AsyncSession, person_id: UUID) -> Optional[Person]:
    """Get person by ID for admin"""
    try:
        result = await db.execute(
            select(Person)
            .where(Person.id == person_id)
            .options(
                selectinload(Person.content_cast),
                selectinload(Person.content_crew),
            )
        )
        return result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving person: {str(e)}",
        )


async def update_person(
    db: AsyncSession, person_id: UUID, update_data: dict
) -> Optional[Person]:
    """Update person"""
    try:
        # Get existing person
        query = select(Person).where(Person.id == person_id)
        result = await db.execute(query)
        person = result.scalar_one_or_none()

        if not person:
            return None

        # Check for name conflicts if name is being updated
        if "name" in update_data and update_data["name"] != person.name:
            existing_name = await db.execute(
                select(Person).where(
                    and_(Person.name == update_data["name"], Person.id != person_id)
                )
            )
            if existing_name.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Person with this name already exists",
                )

        # Check for slug conflicts if slug is being updated
        if "slug" in update_data and update_data["slug"] != person.slug:
            existing_slug = await db.execute(
                select(Person).where(
                    and_(Person.slug == update_data["slug"], Person.id != person_id)
                )
            )
            if existing_slug.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Person with this slug already exists",
                )

        # Update person
        for field, value in update_data.items():
            if hasattr(person, field):
                setattr(person, field, value)

        await db.commit()
        await db.refresh(person)

        return person
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating person: {str(e)}",
        )


async def delete_person(db: AsyncSession, person_id: UUID) -> bool:
    """Delete person (soft delete)"""
    try:
        query = select(Person).where(Person.id == person_id)
        result = await db.execute(query)
        person = result.scalar_one_or_none()

        if not person:
            return False

        # Soft delete
        person.is_deleted = True
        await db.commit()

        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting person: {str(e)}",
        )


async def toggle_person_featured(db: AsyncSession, person_id: UUID) -> Optional[Person]:
    """Toggle person featured status"""
    try:
        query = select(Person).where(Person.id == person_id)
        result = await db.execute(query)
        person = result.scalar_one_or_none()

        if not person:
            return None

        person.is_featured = not person.is_featured
        await db.commit()
        await db.refresh(person)

        return person
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling person featured status: {str(e)}",
        )


async def toggle_person_verified(db: AsyncSession, person_id: UUID) -> Optional[Person]:
    """Toggle person verified status"""
    try:
        query = select(Person).where(Person.id == person_id)
        result = await db.execute(query)
        person = result.scalar_one_or_none()

        if not person:
            return None

        person.is_verified = not person.is_verified
        await db.commit()
        await db.refresh(person)

        return person
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling person verified status: {str(e)}",
        )
