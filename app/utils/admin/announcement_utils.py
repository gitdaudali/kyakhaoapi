from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.announcement import Announcement, AnnouncementStatus
from app.schemas.admin import AnnouncementAdminQueryParams


async def create_announcement(
    db: AsyncSession, 
    announcement_data: dict
) -> Announcement:
    """Create a new announcement"""
    announcement = Announcement(**announcement_data)
    db.add(announcement)
    await db.commit()
    await db.refresh(announcement)
    return announcement


async def get_announcements_admin_list(
    db: AsyncSession, 
    query_params: AnnouncementAdminQueryParams
) -> Tuple[List[Announcement], int]:
    """Get paginated list of announcements for admin"""
    
    # Build query
    query = select(Announcement).where(Announcement.is_deleted == False)
    
    # Apply filters
    if query_params.search:
        search_term = f"%{query_params.search}%"
        query = query.where(
            or_(
                Announcement.title.ilike(search_term),
                Announcement.description.ilike(search_term)
            )
        )
    
    if query_params.status:
        query = query.where(Announcement.status == query_params.status)
    
    if query_params.is_active is not None:
        query = query.where(Announcement.is_active == query_params.is_active)
    
    # Apply sorting
    sort_column = getattr(Announcement, query_params.sort_by, Announcement.created_at)
    if query_params.sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Get total count
    count_query = select(func.count(Announcement.id)).where(Announcement.is_deleted == False)
    if query_params.search:
        search_term = f"%{query_params.search}%"
        count_query = count_query.where(
            or_(
                Announcement.title.ilike(search_term),
                Announcement.description.ilike(search_term)
            )
        )
    if query_params.status:
        count_query = count_query.where(Announcement.status == query_params.status)
    if query_params.is_active is not None:
        count_query = count_query.where(Announcement.is_active == query_params.is_active)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (query_params.page - 1) * query_params.size
    query = query.offset(offset).limit(query_params.size)
    
    result = await db.execute(query)
    announcements = result.scalars().all()
    
    return announcements, total


async def get_announcement_admin_by_id(db: AsyncSession, announcement_id: UUID) -> Optional[Announcement]:
    """Get announcement by ID for admin"""
    query = select(Announcement).where(
        and_(Announcement.id == announcement_id, Announcement.is_deleted == False)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_announcement(
    db: AsyncSession, 
    announcement_id: UUID, 
    announcement_data: dict
) -> Optional[Announcement]:
    """Update announcement"""
    # Remove None values
    update_data = {k: v for k, v in announcement_data.items() if v is not None}
    if not update_data:
        return await get_announcement_admin_by_id(db, announcement_id)
    
    query = (
        update(Announcement)
        .where(and_(Announcement.id == announcement_id, Announcement.is_deleted == False))
        .values(**update_data)
        .returning(Announcement)
    )
    
    result = await db.execute(query)
    await db.commit()
    return result.scalar_one_or_none()


async def delete_announcement(db: AsyncSession, announcement_id: UUID) -> bool:
    """Soft delete announcement"""
    query = (
        update(Announcement)
        .where(and_(Announcement.id == announcement_id, Announcement.is_deleted == False))
        .values(is_deleted=True)
    )
    
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0

