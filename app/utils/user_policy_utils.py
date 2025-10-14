from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.policy import Policy, PolicyStatus
# No query params needed


async def get_user_policies_list(db: AsyncSession) -> List[Policy]:
    """Get all policies for user access (simple list)"""
    
    # Simple query - get all policies (not deleted)
    query = (
        select(Policy)
        .where(Policy.is_deleted == False)
        .order_by(Policy.created_at.desc())
    )
    
    # Execute query
    result = await db.execute(query)
    policies = result.scalars().all()
    
    return policies


async def get_user_policy_by_id(
    db: AsyncSession, policy_id: UUID
) -> Optional[Policy]:
    """Get policy by ID for user access (full details)"""
    
    query = (
        select(Policy)
        .where(
            and_(
                Policy.id == policy_id,
                Policy.is_deleted == False
            )
        )
    )
    
    result = await db.execute(query)
    return result.scalar_one_or_none()
