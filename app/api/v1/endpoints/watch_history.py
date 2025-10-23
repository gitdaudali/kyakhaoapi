"""
Watch History API Endpoints

This module contains FastAPI endpoints for watch history operations.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.watch_history import (
    WatchHistoryCreate,
    WatchHistoryUpdate,
    WatchHistoryResponse,
    WatchHistoryListResponse,
    WatchHistoryDeleteResponse,
    WatchHistoryClearResponse,
    PaginationParams
)
from app.utils.watch_history_utils import (
    create_watch_history,
    get_watch_history_by_id,
    get_user_watch_history,
    update_watch_history,
    delete_watch_history,
    clear_user_watch_history
)

router = APIRouter(
    tags=["Watch History"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)


@router.get(
    "/history",
    response_model=WatchHistoryListResponse,
    summary="Get user watch history",
    description="Get paginated watch history for a user, sorted by last_watched_at DESC"
)
async def get_watch_history(
    user_id: UUID = Query(..., description="User ID to get watch history for"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    db: AsyncSession = Depends(get_db)
) -> WatchHistoryListResponse:
    """
    Get paginated watch history for a user.
    
    Args:
        user_id: The user ID to get watch history for
        page: Page number (starts from 1)
        limit: Number of items per page (max 100)
        db: Database session
        
    Returns:
        WatchHistoryListResponse: Paginated watch history response
        
    Raises:
        HTTPException: If there's an error fetching the data
    """
    try:
        pagination = PaginationParams(page=page, limit=limit)
        result = await get_user_watch_history(db, user_id, pagination)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching watch history: {str(e)}"
        )


@router.post(
    "/history",
    response_model=WatchHistoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add watch history record",
    description="Add a new watch history record for a user"
)
async def add_watch_history(
    watch_history_data: WatchHistoryCreate,
    db: AsyncSession = Depends(get_db)
) -> WatchHistoryResponse:
    """
    Add a new watch history record.
    
    Args:
        watch_history_data: Data for creating the watch history record
        db: Database session
        
    Returns:
        WatchHistoryResponse: The created watch history record
        
    Raises:
        HTTPException: If there's an error creating the record
    """
    try:
        watch_history = await create_watch_history(db, watch_history_data)
        return WatchHistoryResponse.from_orm(watch_history)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating watch history: {str(e)}"
        )


@router.get(
    "/history/{history_id}",
    response_model=WatchHistoryResponse,
    summary="Get watch history by ID",
    description="Get a specific watch history record by its ID"
)
async def get_watch_history_by_id_endpoint(
    history_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> WatchHistoryResponse:
    """
    Get a specific watch history record by ID.
    
    Args:
        history_id: The ID of the watch history record
        db: Database session
        
    Returns:
        WatchHistoryResponse: The watch history record
        
    Raises:
        HTTPException: If the record is not found or there's an error
    """
    try:
        watch_history = await get_watch_history_by_id(db, history_id)
        if not watch_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watch history record not found"
            )
        
        return WatchHistoryResponse.from_orm(watch_history)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching watch history: {str(e)}"
        )


@router.put(
    "/history/{history_id}",
    response_model=WatchHistoryResponse,
    summary="Update watch history",
    description="Update an existing watch history record"
)
async def update_watch_history_endpoint(
    history_id: UUID,
    update_data: WatchHistoryUpdate,
    db: AsyncSession = Depends(get_db)
) -> WatchHistoryResponse:
    """
    Update an existing watch history record.
    
    Args:
        history_id: The ID of the watch history record to update
        update_data: Data for updating the record
        db: Database session
        
    Returns:
        WatchHistoryResponse: The updated watch history record
        
    Raises:
        HTTPException: If the record is not found or there's an error
    """
    try:
        watch_history = await update_watch_history(db, history_id, update_data)
        if not watch_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watch history record not found"
            )
        
        return WatchHistoryResponse.from_orm(watch_history)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating watch history: {str(e)}"
        )


@router.delete(
    "/history/{history_id}",
    response_model=WatchHistoryDeleteResponse,
    summary="Delete watch history record",
    description="Delete a specific watch history record by its ID"
)
async def delete_watch_history_endpoint(
    history_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> WatchHistoryDeleteResponse:
    """
    Delete a specific watch history record.
    
    Args:
        history_id: The ID of the watch history record to delete
        db: Database session
        
    Returns:
        WatchHistoryDeleteResponse: Confirmation of deletion
        
    Raises:
        HTTPException: If the record is not found or there's an error
    """
    try:
        deleted = await delete_watch_history(db, history_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watch history record not found"
            )
        
        return WatchHistoryDeleteResponse(
            message="Watch history record deleted successfully",
            deleted_id=history_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting watch history: {str(e)}"
        )


@router.delete(
    "/history/clear",
    response_model=WatchHistoryClearResponse,
    summary="Clear all watch history",
    description="Clear all watch history records for a user"
)
async def clear_watch_history(
    user_id: UUID = Query(..., description="User ID to clear watch history for"),
    db: AsyncSession = Depends(get_db)
) -> WatchHistoryClearResponse:
    """
    Clear all watch history records for a user.
    
    Args:
        user_id: The user ID to clear watch history for
        db: Database session
        
    Returns:
        WatchHistoryClearResponse: Confirmation of clearing with count
        
    Raises:
        HTTPException: If there's an error clearing the history
    """
    try:
        deleted_count = await clear_user_watch_history(db, user_id)
        
        return WatchHistoryClearResponse(
            message=f"Successfully cleared {deleted_count} watch history records",
            deleted_count=deleted_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing watch history: {str(e)}"
        )


@router.get(
    "/history/stats/{user_id}",
    summary="Get watch history statistics",
    description="Get statistics about a user's watch history"
)
async def get_watch_history_stats(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get watch history statistics for a user.
    
    Args:
        user_id: The user ID to get statistics for
        db: Database session
        
    Returns:
        dict: Statistics about the user's watch history
        
    Raises:
        HTTPException: If there's an error fetching statistics
    """
    try:
        from app.utils.watch_history_utils import WatchHistoryService
        service = WatchHistoryService(db)
        stats = await service.get_watch_history_stats(user_id)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching watch history statistics: {str(e)}"
        )
