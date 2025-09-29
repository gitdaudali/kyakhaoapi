from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.schemas.streaming import (
    StreamingChannelListResponse,
    StreamingChannelQueryParams,
    StreamingChannelSimple,
)
from app.utils.content_utils import calculate_pagination_info
from app.utils.streaming_utils import get_streaming_channels_list

router = APIRouter()


@router.get("/channels", response_model=StreamingChannelListResponse)
async def get_streaming_channels(
    query_params: StreamingChannelQueryParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get paginated list of streaming channels with filtering and search.
    """
    try:
        channels, total = await get_streaming_channels_list(db, query_params)

        channel_responses = [
            StreamingChannelSimple(
                id=channel.id,
                name=channel.name,
                icon=channel.icon,
                stream_url=channel.stream_url,
                description=channel.description,
                category=channel.category,
                language=channel.language,
                country=channel.country,
                quality=channel.quality,
            )
            for channel in channels
        ]

        pagination_info = calculate_pagination_info(
            query_params.page, query_params.size, total
        )

        return StreamingChannelListResponse(
            items=channel_responses,
            total=pagination_info["total"],
            page=pagination_info["page"],
            size=pagination_info["size"],
            pages=pagination_info["pages"],
            has_next=pagination_info["has_next"],
            has_prev=pagination_info["has_prev"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving streaming channels: {str(e)}",
        )
