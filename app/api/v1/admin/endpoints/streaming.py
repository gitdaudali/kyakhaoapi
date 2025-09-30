from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.core.messages import (
    STREAMING_CHANNEL_ALREADY_EXISTS,
    STREAMING_CHANNEL_CREATED,
    STREAMING_CHANNEL_DELETED,
    STREAMING_CHANNEL_NOT_FOUND,
    STREAMING_CHANNEL_UPDATED,
)
from app.models.user import User
from app.schemas.admin import (
    StreamingChannelAdminCreate,
    StreamingChannelAdminListResponse,
    StreamingChannelAdminQueryParams,
    StreamingChannelAdminResponse,
    StreamingChannelAdminUpdate,
)
from app.utils.admin_utils import (
    create_streaming_channel,
    delete_streaming_channel,
    get_streaming_channel_admin_by_id,
    get_streaming_channels_admin_list,
    update_streaming_channel,
)
from app.utils.content_utils import calculate_pagination_info

router = APIRouter()


@router.post("/", response_model=StreamingChannelAdminResponse)
async def create_streaming_channel_admin(
    channel_data: StreamingChannelAdminCreate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new streaming channel.
    """
    try:
        channel = await create_streaming_channel(db, channel_data.dict())
        return StreamingChannelAdminResponse.model_validate(channel)
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=STREAMING_CHANNEL_ALREADY_EXISTS,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating streaming channel: {str(e)}",
        )


@router.get("/", response_model=StreamingChannelAdminListResponse)
async def get_streaming_channels_admin(
    current_user: AdminUser,
    query_params: StreamingChannelAdminQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get paginated list of streaming channels for admin.
    """
    try:
        channels, total = await get_streaming_channels_admin_list(db, query_params)
        pagination_info = calculate_pagination_info(
            query_params.page, query_params.size, total
        )

        return StreamingChannelAdminListResponse(
            items=channels,
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


@router.get("/{channel_id}", response_model=StreamingChannelAdminResponse)
async def get_streaming_channel_admin(
    channel_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get streaming channel details by ID (Admin only).
    """
    try:
        channel = await get_streaming_channel_admin_by_id(db, channel_id)

        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=STREAMING_CHANNEL_NOT_FOUND,
            )

        return StreamingChannelAdminResponse.model_validate(channel)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving streaming channel: {str(e)}",
        )


@router.put("/{channel_id}", response_model=StreamingChannelAdminResponse)
async def update_streaming_channel_admin(
    channel_id: UUID,
    update_data: StreamingChannelAdminUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update streaming channel (Admin only).
    """
    try:
        # Filter out None values
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}

        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update",
            )

        channel = await update_streaming_channel(db, channel_id, update_dict)

        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=STREAMING_CHANNEL_NOT_FOUND,
            )

        return StreamingChannelAdminResponse.model_validate(channel)
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=STREAMING_CHANNEL_ALREADY_EXISTS,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating streaming channel: {str(e)}",
        )


@router.delete("/{channel_id}")
async def delete_streaming_channel_admin(
    channel_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete streaming channel (Admin only).
    """
    try:
        success = await delete_streaming_channel(db, channel_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=STREAMING_CHANNEL_NOT_FOUND,
            )

        return {"message": STREAMING_CHANNEL_DELETED}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting streaming channel: {str(e)}",
        )
