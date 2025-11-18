"""User notifications endpoints."""
from typing import Any
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationListItem, NotificationOut, NotificationUnreadCount
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.utils.auth import get_current_user

router = APIRouter(tags=["Notifications"])


@router.get("/")
async def get_notifications(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Get all notifications for the logged-in user."""
    try:
        # Build query for user's notifications
        query = select(Notification).where(
            Notification.user_id == current_user.id,
            Notification.is_deleted.is_(False)
        )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering (newest first)
        query = query.order_by(Notification.created_at.desc())
        query = query.offset(pagination.offset).limit(pagination.limit)
        
        # Execute query
        result = await session.execute(query)
        notifications = result.scalars().all()
        
        notifications_list = [
            NotificationListItem(
                id=notification.id,
                title=notification.title,
                message=notification.message,
                is_read=notification.is_read,
                notification_type=notification.notification_type,
                created_at=notification.created_at,
            ).model_dump()
            for notification in notifications
        ]
        
        paginated_response = PaginatedResponse(
            items=notifications_list,
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            total_pages=(total + pagination.limit - 1) // pagination.limit if pagination.limit > 0 else 0
        )
        
        return success_response(
            message="Notifications retrieved successfully",
            data=paginated_response.model_dump()
        )
        
    except Exception as e:
        return error_response(
            message=f"Error retrieving notifications: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Get count of unread notifications for the logged-in user."""
    try:
        result = await session.execute(
            select(func.count(Notification.id))
            .where(
                Notification.user_id == current_user.id,
                Notification.is_read.is_(False),
                Notification.is_deleted.is_(False)
            )
        )
        unread_count = result.scalar() or 0
        
        response = NotificationUnreadCount(unread_count=unread_count)
        
        return success_response(
            message="Unread count retrieved successfully",
            data=response.model_dump()
        )
        
    except Exception as e:
        return error_response(
            message=f"Error retrieving unread count: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/mark-all-read")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Mark all notifications as read for the logged-in user."""
    try:
        # Get all unread notifications for user
        result = await session.execute(
            select(Notification).where(
                Notification.user_id == current_user.id,
                Notification.is_read.is_(False),
                Notification.is_deleted.is_(False)
            )
        )
        notifications = result.scalars().all()
        
        # Mark all as read
        count = 0
        for notification in notifications:
            notification.is_read = True
            count += 1
        
        await session.commit()
        
        return success_response(
            message=f"Marked {count} notification(s) as read",
            data={"marked_count": count}
        )
        
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error marking notifications as read: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Mark a specific notification as read."""
    try:
        # Get notification
        result = await session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == current_user.id,
                Notification.is_deleted.is_(False)
            )
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            return error_response(
                message="Notification not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Mark as read
        notification.is_read = True
        await session.commit()
        await session.refresh(notification)
        
        notification_out = NotificationOut(
            id=notification.id,
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            is_read=notification.is_read,
            notification_type=notification.notification_type,
            related_id=notification.related_id,
            created_at=notification.created_at,
            updated_at=notification.updated_at,
        )
        
        return success_response(
            message="Notification marked as read",
            data=notification_out.model_dump()
        )
        
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error marking notification as read: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

