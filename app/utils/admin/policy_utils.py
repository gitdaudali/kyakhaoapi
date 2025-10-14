from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.policy import Policy, PolicyType, PolicyStatus
from app.schemas.admin import PolicyAdminQueryParams

async def create_policy(
    db: AsyncSession, 
    policy_data: dict, 
    author_id: UUID
) -> Policy:
    """Create a new policy"""
    policy_data["author_id"] = author_id
    policy = Policy(**policy_data)
    db.add(policy)
    await db.commit()
    await db.refresh(policy)
    return policy

async def get_policies_admin_list(
    db: AsyncSession, 
    query_params: PolicyAdminQueryParams
) -> Tuple[List[Policy], int]:
    """Get paginated list of policies for admin"""
    
    # Build query
    query = select(Policy).where(Policy.is_deleted == False)
    
    # Apply filters
    if query_params.search:
        search_term = f"%{query_params.search}%"
        query = query.where(
            or_(
                Policy.title.ilike(search_term),
                Policy.content.ilike(search_term),
                Policy.slug.ilike(search_term)
            )
        )
    
    if query_params.policy_type:
        query = query.where(Policy.policy_type == query_params.policy_type)
    
    if query_params.status:
        query = query.where(Policy.status == query_params.status)
    
    if query_params.is_active is not None:
        query = query.where(Policy.is_active == query_params.is_active)
    
    # Apply sorting
    sort_column = getattr(Policy, query_params.sort_by, Policy.created_at)
    if query_params.sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Get total count
    count_query = select(Policy.id).where(Policy.is_deleted == False)
    if query_params.search:
        search_term = f"%{query_params.search}%"
        count_query = count_query.where(
            or_(
                Policy.title.ilike(search_term),
                Policy.content.ilike(search_term),
                Policy.slug.ilike(search_term)
            )
        )
    if query_params.policy_type:
        count_query = count_query.where(Policy.policy_type == query_params.policy_type)
    if query_params.status:
        count_query = count_query.where(Policy.status == query_params.status)
    if query_params.is_active is not None:
        count_query = count_query.where(Policy.is_active == query_params.is_active)
    
    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())
    
    # Apply pagination
    offset = (query_params.page - 1) * query_params.size
    query = query.offset(offset).limit(query_params.size)
    
    result = await db.execute(query)
    policies = result.scalars().all()
    
    return policies, total

async def get_policy_admin_by_id(db: AsyncSession, policy_id: UUID) -> Optional[Policy]:
    """Get policy by ID for admin"""
    query = select(Policy).where(
        and_(Policy.id == policy_id, Policy.is_deleted == False)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_policy(
    db: AsyncSession, 
    policy_id: UUID, 
    policy_data: dict, 
    reviewer_id: UUID
) -> Optional[Policy]:
    """Update policy"""
    # Remove None values
    update_data = {k: v for k, v in policy_data.items() if v is not None}
    if not update_data:
        return await get_policy_admin_by_id(db, policy_id)
    
    update_data["reviewer_id"] = reviewer_id
    
    query = (
        update(Policy)
        .where(and_(Policy.id == policy_id, Policy.is_deleted == False))
        .values(**update_data)
        .returning(Policy)
    )
    
    result = await db.execute(query)
    await db.commit()
    return result.scalar_one_or_none()

async def delete_policy(db: AsyncSession, policy_id: UUID) -> bool:
    """Soft delete policy"""
    query = (
        update(Policy)
        .where(and_(Policy.id == policy_id, Policy.is_deleted == False))
        .values(is_deleted=True)
    )
    
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0
