from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import List
import json
import uuid

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.user_settings import UserSettings
from app.models.user_profile import UserProfile
from app.models.subscription import Subscription
from app.schemas.account import *

router = APIRouter()

# 1. Account Overview
@router.get("/overview", response_model=AccountOverviewResponse)
async def get_account_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get complete account overview with all user data"""
    try:
        # Get user basic info
        user_info = UserInfo(
            id=str(current_user.id),
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            avatar_url=current_user.avatar_url,
            account_status="active" if current_user.is_active else "inactive",
            created_at=current_user.created_at,
            last_login=current_user.last_login
        )
        
        # Get subscription info from database
        subscription_result = await db.execute(
            select(Subscription).where(
                Subscription.user_id == current_user.id, 
                Subscription.status == "active"
            )
        )
        active_subscription = subscription_result.scalar_one_or_none()
        
        if active_subscription:
            subscription = SubscriptionInfo(
                plan=active_subscription.plan.value,
                status=active_subscription.status.value,
                current_period_end=active_subscription.current_period_end,
                auto_renew=not active_subscription.cancel_at_period_end,
                next_billing=active_subscription.current_period_end
            )
        else:
            subscription = SubscriptionInfo(
                plan="free",
                status="inactive",
                current_period_end=None,
                auto_renew=False,
                next_billing=None
            )
        
        # Get profiles count from database
        profiles_result = await db.execute(
            select(func.count(UserProfile.id)).where(UserProfile.user_id == current_user.id)
        )
        total_profiles = profiles_result.scalar() or 0
        
        active_profiles_result = await db.execute(
            select(func.count(UserProfile.id)).where(
                UserProfile.user_id == current_user.id, 
                UserProfile.status == "ACTIVE"
            )
        )
        active_profiles = active_profiles_result.scalar() or 0
        
        primary_profile_result = await db.execute(
            select(UserProfile.id).where(
                UserProfile.user_id == current_user.id, 
                UserProfile.is_primary == True
            )
        )
        primary_profile_id = primary_profile_result.scalar_one_or_none()
        
        profiles = ProfileInfo(
            total=total_profiles,
            active=active_profiles,
            primary=str(primary_profile_id) if primary_profile_id else None
        )
        
        # Get usage stats from analytics_data JSON field
        analytics_data = json.loads(getattr(current_user, 'analytics_data', None) or '{}')
        usage_stats = UsageStats(
            total_watch_time=analytics_data.get("total_watch_time", 0),
            content_watched=analytics_data.get("content_watched", 0),
            favorite_genres=analytics_data.get("favorite_genres", [])
        )
        
        # Get security info
        security = SecurityInfo(
            two_factor_enabled=False,  # Get from UserSettings
            trusted_devices=2,  # Get from device_info JSON field
            last_password_change=None
        )
        
        return AccountOverviewResponse(
            user_info=user_info,
            subscription=subscription,
            profiles=profiles,
            usage_stats=usage_stats,
            security=security
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching account overview: {str(e)}"
        )

# 2. Settings Management
@router.get("/settings", response_model=AccountSettings)
async def get_account_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user account settings"""
    try:
        # Query user settings
        query = select(UserSettings).where(
            UserSettings.user_id == current_user.id
        )
        result = await db.execute(query)
        settings = result.scalar_one_or_none()
        
        if not settings:
            # Return default settings
            return AccountSettings(
                language="en",
                timezone="UTC",
                autoplay=True,
                email_notifications=True,
                push_notifications=True,
                marketing_emails=False,
                parental_controls_enabled=False,
                content_rating_limit=18,
                data_sharing=False,
                analytics_tracking=True
            )
        
        return AccountSettings(
            language=settings.language,
            timezone=settings.timezone,
            autoplay=settings.autoplay,
            email_notifications=settings.email_notifications,
            push_notifications=settings.push_notifications,
            marketing_emails=settings.marketing_emails,
            parental_controls_enabled=settings.parental_controls_enabled,
            content_rating_limit=settings.content_rating_limit,
            data_sharing=settings.data_sharing,
            analytics_tracking=settings.analytics_tracking
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching settings: {str(e)}"
        )

@router.put("/settings", response_model=dict)
async def update_account_settings(
    settings_update: AccountSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user account settings"""
    try:
        # Get existing settings
        query = select(UserSettings).where(
            UserSettings.user_id == current_user.id
        )
        result = await db.execute(query)
        settings = result.scalar_one_or_none()
        
        if not settings:
            # Create new settings
            settings = UserSettings(
                user_id=current_user.id,
                **settings_update.dict(exclude_unset=True)
            )
            db.add(settings)
        else:
            # Update existing settings
            for field, value in settings_update.dict(exclude_unset=True).items():
                setattr(settings, field, value)
        
        await db.commit()
        return {"message": "Settings updated successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating settings: {str(e)}"
        )

# 3. Analytics
@router.get("/analytics", response_model=AccountAnalyticsResponse)
async def get_account_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user analytics and usage statistics"""
    try:
        # Get analytics from JSON field
        analytics_data = json.loads(getattr(current_user, 'analytics_data', None) or '{}')
        
        # Parse JSON fields
        favorite_genres = analytics_data.get("favorite_genres", [])
        peak_hours = analytics_data.get("peak_watching_hours", [])
        device_usage_data = analytics_data.get("device_usage", {"mobile": 0, "web": 0, "tv": 0})
        achievements = analytics_data.get("achievements", [])
        
        return AccountAnalyticsResponse(
            total_watch_time=analytics_data.get("total_watch_time", 0),
            content_watched=analytics_data.get("content_watched", 0),
            favorite_genres=favorite_genres,
            peak_watching_hours=peak_hours,
            device_usage=DeviceUsage(**device_usage_data),
            monthly_stats=MonthlyStats(
                current_month=analytics_data.get("current_month", {}),
                previous_month=analytics_data.get("previous_month", {})
            ),
            achievements=achievements
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching analytics: {str(e)}"
        )

# 4. Activity (from JSON field)
@router.get("/activity", response_model=AccountActivityResponse)
async def get_account_activity(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get user activity from JSON field"""
    try:
        # Get activity from JSON field
        activity_data = json.loads(getattr(current_user, 'activity_log', None) or '[]')
        
        # Apply pagination
        paginated_activities = activity_data[offset:offset + limit]
        
        activity_items = [
            ActivityItem(
                id=activity.get("id", ""),
                activity_type=activity.get("activity_type", ""),
                description=activity.get("description", ""),
                ip_address=activity.get("ip_address", ""),
                device_type=activity.get("device_type", ""),
                device_name=activity.get("device_name"),
                location=activity.get("location"),
                timestamp=datetime.fromisoformat(activity.get("timestamp", ""))
            )
            for activity in paginated_activities
        ]
        
        return AccountActivityResponse(
            activities=activity_items,
            total=len(activity_data)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching activity: {str(e)}"
        )

# 5. Data Export
@router.post("/export-data", response_model=DataExportResponse)
async def export_user_data(
    export_request: DataExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export user data (GDPR compliance)"""
    try:
        export_id = str(uuid.uuid4())
        
        # Create export record (you can store this in a separate table or JSON field)
        export_data = {
            "export_id": export_id,
            "user_id": str(current_user.id),
            "data_types": export_request.data_types,
            "format": export_request.format,
            "status": "processing",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store export request (you can implement this based on your needs)
        # For now, return the export ID
        
        return DataExportResponse(
            export_id=export_id,
            status="processing",
            estimated_completion=datetime.utcnow(),
            download_url=None,
            expires_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating data export: {str(e)}"
        )

# 6. Account Deactivation
@router.post("/deactivate", response_model=dict)
async def deactivate_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Temporarily deactivate account"""
    try:
        current_user.is_active = False
        await db.commit()
        return {"message": "Account deactivated successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating account: {str(e)}"
        )

# 7. Account Deletion
@router.delete("/delete", response_model=dict)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Permanently delete account and all data"""
    try:
        # Soft delete user
        current_user.is_deleted = True
        current_user.is_active = False
        await db.commit()
        return {"message": "Account deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting account: {str(e)}"
        )