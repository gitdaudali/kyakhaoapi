from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.core.messages import (
    POLICY_CREATED,
    POLICY_DELETED,
    POLICY_NOT_FOUND,
    POLICY_UPDATED,
)
from app.schemas.admin import (
    PolicyAdminCreate,
    PolicyAdminListResponse,
    PolicyAdminQueryParams,
    PolicyAdminResponse,
    PolicyAdminUpdate,
)
from app.utils.admin.policy_utils import (
    create_policy,
    delete_policy,
    get_policy_admin_by_id,
    get_policies_admin_list,
    update_policy,
)
from app.utils.content_utils import calculate_pagination_info

router = APIRouter()

@router.post("/", response_model=PolicyAdminResponse)
async def create_policy_admin(
    current_user: AdminUser,
    policy_data: PolicyAdminCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create new policy (Admin only)"""
    try:
        policy = await create_policy(db, policy_data.dict(), current_user.id)
        return PolicyAdminResponse.model_validate(policy)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating policy: {str(e)}",
        )

@router.get("/", response_model=PolicyAdminListResponse)
async def get_policies_admin(
    current_user: AdminUser,
    query_params: PolicyAdminQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get policies list (Admin only)"""
    try:
        policies, total = await get_policies_admin_list(db, query_params)
        pagination_info = calculate_pagination_info(
            total, query_params.page, query_params.size
        )
        
        return PolicyAdminListResponse(
            items=[PolicyAdminResponse.model_validate(policy) for policy in policies],
            total=total,
            page=query_params.page,
            size=query_params.size,
            pages=pagination_info["pages"],
            has_next=pagination_info["has_next"],
            has_prev=pagination_info["has_prev"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching policies: {str(e)}",
        )

@router.get("/{policy_id}", response_model=PolicyAdminResponse)
async def get_policy_admin(
    policy_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get policy by ID (Admin only)"""
    try:
        policy = await get_policy_admin_by_id(db, policy_id)
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=POLICY_NOT_FOUND,
            )
        return PolicyAdminResponse.model_validate(policy)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching policy: {str(e)}",
        )

@router.put("/{policy_id}", response_model=PolicyAdminResponse)
async def update_policy_admin(
    policy_id: UUID,
    policy_data: PolicyAdminUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update policy (Admin only)"""
    try:
        policy = await update_policy(db, policy_id, policy_data.dict(), current_user.id)
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=POLICY_NOT_FOUND,
            )
        return PolicyAdminResponse.model_validate(policy)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating policy: {str(e)}",
        )

@router.delete("/{policy_id}")
async def delete_policy_admin(
    policy_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Delete policy (Admin only)"""
    try:
        success = await delete_policy(db, policy_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=POLICY_NOT_FOUND,
            )
        return {"message": POLICY_DELETED}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting policy: {str(e)}",
        )