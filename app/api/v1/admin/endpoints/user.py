from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.core.messages import (
    USER_ACTIVATED,
    USER_DELETED,
    USER_NOT_FOUND,
    USER_ROLE_UPDATED,
    USER_STATUS_UPDATED,
    USER_SUSPENDED,
)
from app.schemas.admin import (
    UserAdminCreate,
    UserAdminListResponse,
    UserAdminQueryParams,
    UserAdminResponse,
    UserAdminUpdate,
)
from app.utils.admin_utils import (
    create_user,
    delete_user,
    get_user_admin_by_id,
    get_users_admin_list,
    toggle_user_active,
    update_user,
    update_user_role,
    update_user_status,
)
from app.utils.content_utils import calculate_pagination_info

router = APIRouter()


@router.post("/", response_model=UserAdminResponse)
async def create_user_admin(
    current_user: AdminUser,
    user_data: UserAdminCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new user
    """
    try:
        user = await create_user(db, user_data.dict())

        return UserAdminResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )


@router.get("/", response_model=UserAdminListResponse)
async def get_users_admin(
    current_user: AdminUser,
    query_params: UserAdminQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get paginated list of users
    """
    try:
        users, total = await get_users_admin_list(db, query_params)

        pagination_info = calculate_pagination_info(
            total=total,
            page=query_params.page,
            size=query_params.size,
        )

        user_responses = [UserAdminResponse.model_validate(user) for user in users]

        return UserAdminListResponse(
            items=user_responses,
            total=pagination_info["total"],
            page=pagination_info["page"],
            size=pagination_info["size"],
            pages=pagination_info["pages"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users list: {str(e)}",
        )


@router.get("/{user_id}", response_model=UserAdminResponse)
async def get_user_admin(
    user_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get user by ID (Admin only).
    """
    try:
        user = await get_user_admin_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )

        return UserAdminResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}",
        )


@router.put("/{user_id}", response_model=UserAdminResponse)
async def update_user_admin(
    user_id: UUID,
    current_user: AdminUser,
    user_data: UserAdminUpdate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update user
    """
    try:
        # Filter out None values
        update_data = {k: v for k, v in user_data.dict().items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided for update",
            )

        user = await update_user(db, user_id, update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )

        return UserAdminResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}",
        )


@router.delete("/{user_id}")
async def delete_user_admin(
    user_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete user
    """
    try:
        success = await delete_user(db, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )

        return {"message": USER_DELETED}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}",
        )


@router.patch("/{user_id}/toggle-active")
async def toggle_user_active_admin(
    user_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Toggle user active status
    """
    try:
        user = await toggle_user_active(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )

        status_message = USER_ACTIVATED if user.is_active else USER_SUSPENDED
        return {"message": status_message, "is_active": user.is_active}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling user active status: {str(e)}",
        )


@router.patch("/{user_id}/role")
async def update_user_role_admin(
    user_id: UUID,
    current_user: AdminUser,
    role: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update user role
    """
    try:
        user = await update_user_role(db, user_id, role)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )

        return {"message": USER_ROLE_UPDATED, "role": user.role}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user role: {str(e)}",
        )


@router.patch("/{user_id}/status")
async def update_user_status_admin(
    user_id: UUID,
    current_user: AdminUser,
    status: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update user profile status
    """
    try:
        user = await update_user_status(db, user_id, status)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )

        return {"message": USER_STATUS_UPDATED, "profile_status": user.profile_status}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user status: {str(e)}",
        )
