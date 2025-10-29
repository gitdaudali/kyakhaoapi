from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.core.messages import (
    TASK_CREATED,
    TASK_DELETED,
    TASK_NOT_FOUND,
    TASK_UPDATED,
)
from app.schemas.admin import (
    TaskAdminCreate,
    TaskAdminListResponse,
    TaskAdminQueryParams,
    TaskAdminResponse,
    TaskAdminUpdate,
)
from app.utils.admin.task_utils import (
    create_task,
    delete_task,
    get_task_admin_by_id,
    get_tasks_admin_list,
    update_task,
)
from app.utils.content_utils import calculate_pagination_info

router = APIRouter()


@router.post("/", response_model=TaskAdminResponse)
async def create_task_admin(
    task_data: TaskAdminCreate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create new task (Admin only)"""
    try:
        # Auto-populate assigned_to with current user if not provided
        task_dict = task_data.model_dump()
        if not task_dict.get("assigned_to"):
            task_dict["assigned_to"] = current_user.id
        
        task = await create_task(db, task_dict)
        return TaskAdminResponse.model_validate(task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}",
        )


@router.get("/", response_model=TaskAdminListResponse)
async def get_tasks_admin(
    current_user: AdminUser,
    query_params: TaskAdminQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get tasks list (Admin only)"""
    try:
        tasks, total = await get_tasks_admin_list(db, query_params)
        pagination_info = calculate_pagination_info(
            query_params.page, query_params.size, total
        )
        
        return TaskAdminListResponse(
            items=[TaskAdminResponse.model_validate(task) for task in tasks],
            total=pagination_info["total"],
            page=pagination_info["page"],
            size=pagination_info["size"],
            pages=pagination_info["pages"],
            has_next=pagination_info["has_next"],
            has_prev=pagination_info["has_prev"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching tasks: {str(e)}",
        )


@router.get("/{task_id}", response_model=TaskAdminResponse)
async def get_task_admin(
    task_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get task by ID (Admin only)"""
    try:
        task = await get_task_admin_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=TASK_NOT_FOUND,
            )
        return TaskAdminResponse.model_validate(task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching task: {str(e)}",
        )


@router.put("/{task_id}", response_model=TaskAdminResponse)
async def update_task_admin(
    task_id: UUID,
    task_data: TaskAdminUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update task (Admin only)"""
    try:
        task = await update_task(db, task_id, task_data.model_dump())
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=TASK_NOT_FOUND,
            )
        return TaskAdminResponse.model_validate(task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating task: {str(e)}",
        )


@router.delete("/{task_id}")
async def delete_task_admin(
    task_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Delete task (Admin only)"""
    try:
        success = await delete_task(db, task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=TASK_NOT_FOUND,
            )
        return {"message": TASK_DELETED}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting task: {str(e)}",
        )

