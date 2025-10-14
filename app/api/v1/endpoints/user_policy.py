from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user_policy import (
    UserPolicyResponse,
    UserPolicyListResponse,
    UserPolicyItem,
)
from app.utils.user_policy_utils import (
    get_user_policies_list,
    get_user_policy_by_id,
)

router = APIRouter()

@router.get("/", response_model=UserPolicyListResponse)
async def get_user_policies(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get all published policies (user access - simple list)"""
    try:
        policies = await get_user_policies_list(db)
        
        # Convert to simple list response (title, description, status only)
        policy_items = [
            UserPolicyItem(
                id=policy.id,
                title=policy.title,
                description=policy.description,
                status=policy.status.value
            )
            for policy in policies
        ]
        
        return UserPolicyListResponse(policies=policy_items)
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
                detail="Policy not found",
            )
        # Return full policy details
        return UserPolicyResponse(
            id=policy.id,
            title=policy.title,
            description=policy.description,
            content=policy.content,
            status=policy.status.value,
            policy_type=policy.policy_type.value,
            version=policy.version,
            effective_date=policy.effective_date,
            created_at=policy.created_at,
            updated_at=policy.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching policy: {str(e)}",
        )
