from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.policy import Policy, PolicyStatus
from app.schemas.user_policy import UserPolicyQueryParams


async def get_user_policies_list(
    db: AsyncSession, query_params: UserPolicyQueryParams
) -> Tuple[List[Policy], int]:
    """Get published policies for user access (names only)"""
    
    # Base query - only published and active policies
    query = (
        select(Policy)
        .where(
            and_(
                Policy.status == PolicyStatus.PUBLISHED,
                Policy.is_active == True,
                Policy.is_deleted == False
            )
        )
    )
    
    # Apply search filter
    if query_params.search:
        search_filter = or_(
            Policy.title.ilike(f"%{query_params.search}%"),
            Policy.description.ilike(f"%{query_params.search}%")
        )
        query = query.where(search_filter)
    
    # Apply policy type filter
    if query_params.policy_type:
        query = query.where(Policy.policy_type == query_params.policy_type)
    
    # Apply sorting
    if query_params.sort_by == "title":
        sort_column = Policy.title
    elif query_params.sort_by == "created_at":
        sort_column = Policy.created_at
    else:
        sort_column = Policy.created_at
    
    if query_params.sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Get total count
    count_query = select(func.count(Policy.id)).where(
        and_(
            Policy.status == PolicyStatus.PUBLISHED,
            Policy.is_active == True,
            Policy.is_deleted == False
        )
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (query_params.page - 1) * query_params.size
    query = query.offset(offset).limit(query_params.size)
    
    # Execute query
    result = await db.execute(query)
    policies = result.scalars().all()
    
    return policies, total


async def get_user_policy_by_id(
    db: AsyncSession, policy_id: UUID
) -> Optional[Policy]:
    """Get published policy by ID for user access"""
    
    query = (
        select(Policy)
        .where(
            and_(
                Policy.id == policy_id,
                Policy.status == PolicyStatus.PUBLISHED,
                Policy.is_active == True,
                Policy.is_deleted == False
            )
        )
    )
    
    result = await db.execute(query)
    return result.scalar_one_or_none()
