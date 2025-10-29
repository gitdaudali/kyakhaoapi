from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.core.messages import (
    ANNOUNCEMENT_CREATED,
    ANNOUNCEMENT_DELETED,
    ANNOUNCEMENT_NOT_FOUND,
    ANNOUNCEMENT_UPDATED,
)
from app.schemas.admin import (
    AnnouncementAdminCreate,
    AnnouncementAdminListResponse,
    AnnouncementAdminQueryParams,
    AnnouncementAdminResponse,
    AnnouncementAdminUpdate,
)
from app.utils.admin.announcement_utils import (
    create_announcement,
    delete_announcement,
    get_announcement_admin_by_id,
    get_announcements_admin_list,
    update_announcement,
)
from app.utils.content_utils import calculate_pagination_info

router = APIRouter()


@router.post("/", response_model=AnnouncementAdminResponse)
async def create_announcement_admin(
    announcement_data: AnnouncementAdminCreate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create new announcement (Admin only)"""
    try:
        # Auto-populate author_id with current user if not provided
        announcement_dict = announcement_data.model_dump()
        if not announcement_dict.get("author_id"):
            announcement_dict["author_id"] = current_user.id
        
        announcement = await create_announcement(db, announcement_dict)
        return AnnouncementAdminResponse.model_validate(announcement)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating announcement: {str(e)}",
        )


@router.get("/", response_model=AnnouncementAdminListResponse)
async def get_announcements_admin(
    current_user: AdminUser,
    query_params: AnnouncementAdminQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get announcements list (Admin only)"""
    try:
        announcements, total = await get_announcements_admin_list(db, query_params)
        pagination_info = calculate_pagination_info(
            query_params.page, query_params.size, total
        )
        
        return AnnouncementAdminListResponse(
            items=[AnnouncementAdminResponse.model_validate(announcement) for announcement in announcements],
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
            detail=f"Error fetching announcements: {str(e)}",
        )


@router.get("/{announcement_id}", response_model=AnnouncementAdminResponse)
async def get_announcement_admin(
    announcement_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get announcement by ID (Admin only)"""
    try:
        announcement = await get_announcement_admin_by_id(db, announcement_id)
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ANNOUNCEMENT_NOT_FOUND,
            )
        return AnnouncementAdminResponse.model_validate(announcement)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching announcement: {str(e)}",
        )


@router.put("/{announcement_id}", response_model=AnnouncementAdminResponse)
async def update_announcement_admin(
    announcement_id: UUID,
    announcement_data: AnnouncementAdminUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update announcement (Admin only)"""
    try:
        announcement = await update_announcement(db, announcement_id, announcement_data.model_dump())
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ANNOUNCEMENT_NOT_FOUND,
            )
        return AnnouncementAdminResponse.model_validate(announcement)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating announcement: {str(e)}",
        )


@router.delete("/{announcement_id}")
async def delete_announcement_admin(
    announcement_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Delete announcement (Admin only)"""
    try:
        success = await delete_announcement(db, announcement_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ANNOUNCEMENT_NOT_FOUND,
            )
        return {"message": ANNOUNCEMENT_DELETED}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting announcement: {str(e)}",
        )

