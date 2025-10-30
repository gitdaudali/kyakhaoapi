from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskPriority, TaskStatus
from app.schemas.admin import TaskAdminQueryParams


async def create_task(
    db: AsyncSession, 
    task_data: dict
) -> Task:
    """Create a new task"""
    task = Task(**task_data)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_tasks_admin_list(
    db: AsyncSession, 
    query_params: TaskAdminQueryParams
) -> Tuple[List[Task], int]:
    """Get paginated list of tasks for admin"""
    
    # Build query
    query = select(Task).where(Task.is_deleted == False)
    
    # Apply filters
    if query_params.search:
        search_term = f"%{query_params.search}%"
        conditions = [Task.task_title.ilike(search_term)]
        conditions.append(Task.description.ilike(search_term))
        conditions.append(Task.project.ilike(search_term))
        query = query.where(or_(*conditions))
    
    if query_params.priority:
        query = query.where(Task.priority == query_params.priority)
    
    if query_params.status:
        query = query.where(Task.status == query_params.status)
    
    if query_params.assigned_to:
        query = query.where(Task.assigned_to == query_params.assigned_to)
    
    if query_params.project:
        query = query.where(Task.project.ilike(f"%{query_params.project}%"))
    
    if query_params.is_active is not None:
        query = query.where(Task.is_active == query_params.is_active)
    
    # Apply sorting
    sort_column = getattr(Task, query_params.sort_by, Task.created_at)
    if query_params.sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Get total count
    count_query = select(func.count(Task.id)).where(Task.is_deleted == False)
    if query_params.search:
        search_term = f"%{query_params.search}%"
        conditions = [Task.task_title.ilike(search_term)]
        conditions.append(Task.description.ilike(search_term))
        conditions.append(Task.project.ilike(search_term))
        count_query = count_query.where(or_(*conditions))
    if query_params.priority:
        count_query = count_query.where(Task.priority == query_params.priority)
    if query_params.status:
        count_query = count_query.where(Task.status == query_params.status)
    if query_params.assigned_to:
        count_query = count_query.where(Task.assigned_to == query_params.assigned_to)
    if query_params.project:
        count_query = count_query.where(Task.project.ilike(f"%{query_params.project}%"))
    if query_params.is_active is not None:
        count_query = count_query.where(Task.is_active == query_params.is_active)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (query_params.page - 1) * query_params.size
    query = query.offset(offset).limit(query_params.size)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return tasks, total


async def get_task_admin_by_id(db: AsyncSession, task_id: UUID) -> Optional[Task]:
    """Get task by ID for admin"""
    query = select(Task).where(
        and_(Task.id == task_id, Task.is_deleted == False)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_task(
    db: AsyncSession, 
    task_id: UUID, 
    task_data: dict
) -> Optional[Task]:
    """Update task"""
    # Remove None values
    update_data = {k: v for k, v in task_data.items() if v is not None}
    if not update_data:
        return await get_task_admin_by_id(db, task_id)
    
    query = (
        update(Task)
        .where(and_(Task.id == task_id, Task.is_deleted == False))
        .values(**update_data)
        .returning(Task)
    )
    
    result = await db.execute(query)
    await db.commit()
    return result.scalar_one_or_none()


async def delete_task(db: AsyncSession, task_id: UUID) -> bool:
    """Soft delete task"""
    query = (
        update(Task)
        .where(and_(Task.id == task_id, Task.is_deleted == False))
        .values(is_deleted=True)
    )
    
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0

