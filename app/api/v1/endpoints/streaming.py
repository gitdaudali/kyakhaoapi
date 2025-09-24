from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.core.messages import (
    STREAMING_CHANNEL_DETAIL_SUCCESS,
    STREAMING_CHANNEL_LIST_SUCCESS,
    STREAMING_CHANNEL_NOT_FOUND,
)
from app.models.streaming import StreamingChannelCategory
from app.models.user import User
from app.schemas.streaming import (
    StreamingChannel,
    StreamingChannelListResponse,
    StreamingChannelQueryParams,
    StreamingChannelSimple,
)
from app.utils.content_utils import calculate_pagination_info
from app.utils.streaming_utils import (
    get_streaming_channel_by_id,
    get_streaming_channels_list,
)

router = APIRouter()


@router.get("/channels", response_model=StreamingChannelListResponse)
async def get_streaming_channels(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Page size",
    ),
    search: Optional[str] = Query(
        None, min_length=1, max_length=255, description="Search by channel name"
    ),
    category: Optional[StreamingChannelCategory] = Query(
        None, description="Filter by category"
    ),
    language: Optional[str] = Query(
        None, max_length=50, description="Filter by language"
    ),
    country: Optional[str] = Query(
        None, max_length=100, description="Filter by country"
    ),
    quality: Optional[str] = Query(
        None, max_length=20, description="Filter by stream quality"
    ),
    sort_by: str = Query("name", description="Sort field"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get paginated list of streaming channels with filtering and search.
    """
    try:
        # Create query parameters
        query_params = StreamingChannelQueryParams(
            page=page,
            size=size,
            search=search,
            category=category,
            language=language,
            country=country,
            quality=quality,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Get channels and total count
        channels, total = await get_streaming_channels_list(db, query_params)

        # Convert to response schemas using list comprehension (no loops)
        channel_responses = [
            StreamingChannelSimple(
                id=channel.id,
                name=channel.name,
                icon=channel.icon,
                description=channel.description,
                category=channel.category,
                language=channel.language,
                country=channel.country,
                quality=channel.quality,
            )
            for channel in channels
        ]

        # Calculate pagination info using existing utility
        pagination_info = calculate_pagination_info(page, size, total)

        return StreamingChannelListResponse(
            items=channel_responses,
            total=pagination_info["total"],
            page=pagination_info["page"],
            size=pagination_info["size"],
            pages=pagination_info["pages"],
            has_next=pagination_info["has_next"],
            has_prev=pagination_info["has_prev"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving streaming channels: {str(e)}",
        )
