from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.streaming import StreamingChannel, StreamingChannelCategory
from app.schemas.streaming import StreamingChannelQueryParams
from app.utils.content_utils import calculate_pagination_info


async def get_streaming_channels_list(
    db: AsyncSession,
    query_params: StreamingChannelQueryParams,
) -> Tuple[List[StreamingChannel], int]:
    """
    Get paginated list of streaming channels with optimized queries.

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
    sort_field = getattr(StreamingChannel, query_params.sort_by, StreamingChannel.name)
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


async def get_streaming_channel_by_id(
    db: AsyncSession, channel_id: str
) -> Optional[StreamingChannel]:
    """
    Get streaming channel by ID.

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
