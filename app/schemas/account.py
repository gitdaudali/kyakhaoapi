# File: app/schemas/account.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class AccountStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DEACTIVATED = "deactivated"

class NotificationType(str, Enum):
    BILLING = "billing"
    CONTENT = "content"
    SECURITY = "security"
    SYSTEM = "system"

# Account Overview Schemas
class UserInfo(BaseModel):
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    avatar_url: Optional[str]
    account_status: str
    created_at: datetime
    last_login: Optional[datetime]

class SubscriptionInfo(BaseModel):
    plan: str
    status: str
    current_period_end: Optional[datetime]
    auto_renew: bool
    next_billing: Optional[datetime]

class ProfileInfo(BaseModel):
    total: int
    active: int
    primary: Optional[str]

class UsageStats(BaseModel):
    total_watch_time: int
    content_watched: int
    favorite_genres: List[str]

class SecurityInfo(BaseModel):
    two_factor_enabled: bool
    trusted_devices: int
    last_password_change: Optional[datetime]

class AccountOverviewResponse(BaseModel):
    user_info: UserInfo
    subscription: SubscriptionInfo
    profiles: ProfileInfo
    usage_stats: UsageStats
    security: SecurityInfo

# Settings Schemas
class AccountSettings(BaseModel):
    language: str
    timezone: str
    autoplay: bool
    email_notifications: bool
    push_notifications: bool
    marketing_emails: bool
    parental_controls_enabled: bool
    content_rating_limit: int
    data_sharing: bool
    analytics_tracking: bool

class AccountSettingsUpdate(BaseModel):
    language: Optional[str] = None
    timezone: Optional[str] = None
    autoplay: Optional[bool] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    marketing_emails: Optional[bool] = None
    parental_controls_enabled: Optional[bool] = None
    content_rating_limit: Optional[int] = None
    data_sharing: Optional[bool] = None
    analytics_tracking: Optional[bool] = None

# Analytics Schemas
class DeviceUsage(BaseModel):
    mobile: int
    web: int
    tv: int

class MonthlyStats(BaseModel):
    current_month: Dict[str, Any]
    previous_month: Dict[str, Any]

class AccountAnalyticsResponse(BaseModel):
    total_watch_time: int
    content_watched: int
    favorite_genres: List[str]
    peak_watching_hours: List[int]
    device_usage: DeviceUsage
    monthly_stats: MonthlyStats
    achievements: List[str]

# Activity Schemas
class ActivityItem(BaseModel):
    id: str
    activity_type: str
    description: str
    ip_address: str
    device_type: str
    device_name: Optional[str]
    location: Optional[str]
    timestamp: datetime

class AccountActivityResponse(BaseModel):
    activities: List[ActivityItem]
    total: int

# Notification Schemas
class NotificationItem(BaseModel):
    id: str
    title: str
    message: str
    notification_type: NotificationType
    priority: str
    is_read: bool
    created_at: datetime
    action_url: Optional[str]

class NotificationListResponse(BaseModel):
    notifications: List[NotificationItem]
    unread_count: int
    total: int

# Data Export Schemas
class DataExportRequest(BaseModel):
    data_types: List[str] = ["profile", "watch_history", "preferences", "subscription"]
    format: str = "json"  # or "csv"
    email_notification: bool = True

class DataExportResponse(BaseModel):
    export_id: str
    status: str
    estimated_completion: Optional[datetime]
    download_url: Optional[str]
    expires_at: Optional[datetime]