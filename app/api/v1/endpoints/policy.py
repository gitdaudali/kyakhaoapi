from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user_policy import (
    UserPolicyResponse,
    UserPolicyListPaginatedResponse,
    UserPolicyQueryParams,
    UserPolicyListResponse,
)
from app.utils.user_policy_utils import (
    get_user_policies_list,
    get_user_policy_by_id,
)
from app.utils.content_utils import calculate_pagination_info

router = APIRouter()

@router.get("/", response_model=UserPolicyListPaginatedResponse)
async def get_user_policies(
    query_params: UserPolicyQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get list of published policies (user access - names only)"""
    try:
        policies, total = await get_user_policies_list(db, query_params)
        pagination_info = calculate_pagination_info(
            total=total,
            page=query_params.page,
            size=query_params.size
        )
        
        # Convert to simple list response (names only)
        items = [
            UserPolicyListResponse(
                id=policy.id,
                title=policy.title,
                policy_type=policy.policy_type,
                version=policy.version
            )
            for policy in policies
        ]
        
        return UserPolicyListPaginatedResponse(
            items=items,
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

@router.get("/{policy_id}", response_model=UserPolicyResponse)
async def get_user_policy(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get policy details by ID (user access)"""
    try:
        policy = await get_user_policy_by_id(db, policy_id)
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Policy not found or not published",
            )
        return UserPolicyResponse.model_validate(policy)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching policy: {str(e)}",
        )
