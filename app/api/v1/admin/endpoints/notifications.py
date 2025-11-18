"""Admin notifications endpoints."""
from typing import Any
import uuid
from datetime import date, datetime, time, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationAdminOut, NotificationSend
from app.schemas.pagination import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/notifications", tags=["Admin Notifications"])


@router.post("/send", status_code=status.HTTP_201_CREATED)
async def send_notification(
    payload: NotificationSend,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Send notification to a specific user or all users (admin only)."""
    try:
        notifications_created = []
        
        if payload.broadcast or payload.user_id is None:
            # Send to all users
            users_result = await session.execute(
                select(User).where(
                    User.is_active.is_(True),
                    User.is_deleted.is_(False)
                )
            )
            users = users_result.scalars().all()
            
            for user in users:
                notification = Notification(
                    user_id=user.id,
                    title=payload.title,
                    message=payload.message,
                    notification_type=payload.notification_type,
                    related_id=payload.related_id,
                    is_read=False,
                )
                session.add(notification)
                notifications_created.append(notification)
        else:
            # Send to specific user
            user_result = await session.execute(
                select(User).where(
                    User.id == payload.user_id,
                    User.is_deleted.is_(False)
                )
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return error_response(
                    message="User not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            notification = Notification(
                user_id=user.id,
                title=payload.title,
                message=payload.message,
                notification_type=payload.notification_type,
                related_id=payload.related_id,
                is_read=False,
            )
            session.add(notification)
            notifications_created.append(notification)
        
        await session.commit()
        
        # Refresh notifications to get IDs
        for notification in notifications_created:
            await session.refresh(notification)
        
        notifications_out = [
            NotificationAdminOut(
                id=notif.id,
                user_id=notif.user_id,
                title=notif.title,
                message=notif.message,
                is_read=notif.is_read,
                notification_type=notif.notification_type,
                related_id=notif.related_id,
                created_at=notif.created_at,
                updated_at=notif.updated_at,
            ).model_dump()
            for notif in notifications_created
        ]
        
        return success_response(
            message=f"Notification(s) sent successfully to {len(notifications_created)} user(s)",
            data={"notifications": notifications_out, "count": len(notifications_created)},
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error sending notification: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/logs")
async def get_notification_logs(
    pagination: PaginationParams = Depends(),
    user_id: uuid.UUID | None = Query(None, description="Filter by user ID"),
    notification_type: str | None = Query(None, description="Filter by notification type"),
    start_date: date | None = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """View all sent notifications with optional filters (admin only)."""
    try:
        # Build query
        query = select(Notification).where(Notification.is_deleted.is_(False))
        
        # Apply filters
        if user_id:
            query = query.where(Notification.user_id == user_id)
        if notification_type:
            query = query.where(Notification.notification_type == notification_type)
        
        # Handle date filters with exception handling
        start_datetime = None
        end_datetime = None
        
        try:
            if start_date:
                # Validate date is not too far in the past or future
                if start_date.year < 1900 or start_date.year > 2100:
                    return error_response(
                        message="start_date year must be between 1900 and 2100",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                # Convert date to timezone-aware datetime (start of day in UTC)
                start_datetime = datetime.combine(start_date, time.min).replace(tzinfo=timezone.utc)
                query = query.where(Notification.created_at >= start_datetime)
        except (ValueError, TypeError, AttributeError) as e:
            return error_response(
                message=f"Invalid start_date format: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if end_date:
                # Validate date is not too far in the past or future
                if end_date.year < 1900 or end_date.year > 2100:
                    return error_response(
                        message="end_date year must be between 1900 and 2100",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                # Convert date to timezone-aware datetime (end of day in UTC)
                end_datetime = datetime.combine(end_date, time.max).replace(tzinfo=timezone.utc)
                query = query.where(Notification.created_at <= end_datetime)
        except (ValueError, TypeError, AttributeError) as e:
            return error_response(
                message=f"Invalid end_date format: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate date range
        if start_date and end_date and end_date < start_date:
            return error_response(
                message="end_date must be greater than or equal to start_date",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Get total count with exception handling
        try:
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0
        except Exception as e:
            return error_response(
                message=f"Error counting notifications: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Apply pagination and ordering
        query = query.order_by(Notification.created_at.desc())
        query = query.offset(pagination.offset).limit(pagination.limit)
        
        # Execute query with exception handling
        try:
            result = await session.execute(query)
            notifications = result.scalars().all()
        except Exception as e:
            return error_response(
                message=f"Error executing query: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Serialize notifications with exception handling
        try:
            notifications_list = [
                NotificationAdminOut(
                    id=notification.id,
                    user_id=notification.user_id,
                    title=notification.title,
                    message=notification.message,
                    is_read=notification.is_read,
                    notification_type=notification.notification_type,
                    related_id=notification.related_id,
                    created_at=notification.created_at,
                    updated_at=notification.updated_at,
                ).model_dump()
                for notification in notifications
            ]
        except Exception as e:
            return error_response(
                message=f"Error serializing notification data: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create paginated response with exception handling
        try:
            paginated_response = PaginatedResponse(
                items=notifications_list,
                total=total,
                limit=pagination.limit,
                offset=pagination.offset,
                total_pages=(total + pagination.limit - 1) // pagination.limit if pagination.limit > 0 else 0
            )
        except Exception as e:
            return error_response(
                message=f"Error creating paginated response: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return success_response(
            message="Notification logs retrieved successfully",
            data=paginated_response.model_dump()
        )
        
    except Exception as e:
        return error_response(
            message=f"Error retrieving notification logs: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

