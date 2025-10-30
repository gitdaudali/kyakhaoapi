from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.core.messages import (
    POPUP_CREATED,
    POPUP_DELETED,
    POPUP_NOT_FOUND,
    POPUP_UPDATED,
)
from app.schemas.admin import (
    PopupAdminCreate,
    PopupAdminListResponse,
    PopupAdminQueryParams,
    PopupAdminResponse,
    PopupAdminUpdate,
)
from app.utils.admin.popup_utils import (
    create_popup,
    delete_popup,
    get_popup_admin_by_id,
    get_popups_admin_list,
    update_popup,
)
from app.utils.content_utils import calculate_pagination_info

router = APIRouter()


@router.post("/", response_model=PopupAdminResponse)
async def create_popup_admin(
    popup_data: PopupAdminCreate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create new popup (Admin only)"""
    try:
        # Auto-populate assignee_id with current user if not provided
        popup_dict = popup_data.model_dump()
        if not popup_dict.get("assignee_id"):
            popup_dict["assignee_id"] = current_user.id
        
        popup = await create_popup(db, popup_dict)
        return PopupAdminResponse.model_validate(popup)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating popup: {str(e)}",
        )


@router.get("/", response_model=PopupAdminListResponse)
async def get_popups_admin(
    current_user: AdminUser,
    query_params: PopupAdminQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get popups list (Admin only)"""
    try:
        popups, total = await get_popups_admin_list(db, query_params)
        pagination_info = calculate_pagination_info(
            query_params.page, query_params.size, total
        )
        
        return PopupAdminListResponse(
            items=[PopupAdminResponse.model_validate(popup) for popup in popups],
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
            detail=f"Error fetching popups: {str(e)}",
        )


@router.get("/{popup_id}", response_model=PopupAdminResponse)
async def get_popup_admin(
    popup_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get popup by ID (Admin only)"""
    try:
        popup = await get_popup_admin_by_id(db, popup_id)
        if not popup:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=POPUP_NOT_FOUND,
            )
        return PopupAdminResponse.model_validate(popup)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching popup: {str(e)}",
        )


@router.put("/{popup_id}", response_model=PopupAdminResponse)
async def update_popup_admin(
    popup_id: UUID,
    popup_data: PopupAdminUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update popup (Admin only)"""
    try:
        popup = await update_popup(db, popup_id, popup_data.model_dump())
        if not popup:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=POPUP_NOT_FOUND,
            )
        return PopupAdminResponse.model_validate(popup)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating popup: {str(e)}",
        )


@router.delete("/{popup_id}")
async def delete_popup_admin(
    popup_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Delete popup (Admin only)"""
    try:
        success = await delete_popup(db, popup_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=POPUP_NOT_FOUND,
            )
        return {"message": POPUP_DELETED}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting popup: {str(e)}",
        )

