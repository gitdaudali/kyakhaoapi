from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.popup import Popup, PopupStatus, PopupPriority
from app.schemas.admin import PopupAdminQueryParams


async def create_popup(
    db: AsyncSession, 
    popup_data: dict
) -> Popup:
    """Create a new popup"""
    popup = Popup(**popup_data)
    db.add(popup)
    await db.commit()
    await db.refresh(popup)
    return popup


async def get_popups_admin_list(
    db: AsyncSession, 
    query_params: PopupAdminQueryParams
) -> Tuple[List[Popup], int]:
    """Get paginated list of popups for admin"""
    
    # Build query
    query = select(Popup).where(Popup.is_deleted == False)
    
    # Apply filters
    if query_params.search:
        search_term = f"%{query_params.search}%"
        conditions = [Popup.popup_name.ilike(search_term)]
        conditions.append(Popup.description.ilike(search_term))
        conditions.append(Popup.project.ilike(search_term))
        query = query.where(or_(*conditions))
    
    if query_params.status:
        query = query.where(Popup.status == query_params.status)
    
    if query_params.priority:
        query = query.where(Popup.priority == query_params.priority)
    
    if query_params.assignee_id:
        query = query.where(Popup.assignee_id == query_params.assignee_id)
    
    if query_params.project:
        query = query.where(Popup.project.ilike(f"%{query_params.project}%"))
    
    if query_params.is_active is not None:
        query = query.where(Popup.is_active == query_params.is_active)
    
    # Apply sorting
    sort_column = getattr(Popup, query_params.sort_by, Popup.created_at)
    if query_params.sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Get total count
    count_query = select(func.count(Popup.id)).where(Popup.is_deleted == False)
    if query_params.search:
        search_term = f"%{query_params.search}%"
        conditions = [Popup.popup_name.ilike(search_term)]
        conditions.append(Popup.description.ilike(search_term))
        conditions.append(Popup.project.ilike(search_term))
        count_query = count_query.where(or_(*conditions))
    if query_params.status:
        count_query = count_query.where(Popup.status == query_params.status)
    if query_params.priority:
        count_query = count_query.where(Popup.priority == query_params.priority)
    if query_params.assignee_id:
        count_query = count_query.where(Popup.assignee_id == query_params.assignee_id)
    if query_params.project:
        count_query = count_query.where(Popup.project.ilike(f"%{query_params.project}%"))
    if query_params.is_active is not None:
        count_query = count_query.where(Popup.is_active == query_params.is_active)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (query_params.page - 1) * query_params.size
    query = query.offset(offset).limit(query_params.size)
    
    result = await db.execute(query)
    popups = result.scalars().all()
    
    return popups, total


async def get_popup_admin_by_id(db: AsyncSession, popup_id: UUID) -> Optional[Popup]:
    """Get popup by ID for admin"""
    query = select(Popup).where(
        and_(Popup.id == popup_id, Popup.is_deleted == False)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_popup(
    db: AsyncSession, 
    popup_id: UUID, 
    popup_data: dict
) -> Optional[Popup]:
    """Update popup"""
    # Remove None values
    update_data = {k: v for k, v in popup_data.items() if v is not None}
    if not update_data:
        return await get_popup_admin_by_id(db, popup_id)
    
    query = (
        update(Popup)
        .where(and_(Popup.id == popup_id, Popup.is_deleted == False))
        .values(**update_data)
        .returning(Popup)
    )
    
    result = await db.execute(query)
    await db.commit()
    return result.scalar_one_or_none()


async def delete_popup(db: AsyncSession, popup_id: UUID) -> bool:
    """Soft delete popup"""
    query = (
        update(Popup)
        .where(and_(Popup.id == popup_id, Popup.is_deleted == False))
        .values(is_deleted=True)
    )
    
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0

