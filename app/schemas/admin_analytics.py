from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# =============================================================================
# ANALYTICS OVERVIEW SCHEMAS
# =============================================================================

class OverviewSummary(BaseModel):
    """Summary KPIs for analytics overview"""
    active_subscribers: int = Field(..., description="Total active subscribers")
    average_view_time_minutes: int = Field(..., description="Average view time in minutes")
    revenue_per_user: float = Field(..., description="Average revenue per user (ARPU)")
    monthly_churn_rate: float = Field(..., description="Monthly churn rate percentage")

class AnalyticsOverviewResponse(BaseModel):
    """Response schema for analytics overview"""
    summary: OverviewSummary
    period_start: Optional[date] = Field(None, description="Start date of the period")
    period_end: Optional[date] = Field(None, description="End date of the period")
    
    class Config:
        from_attributes = True


# =============================================================================
# SUBSCRIBER GROWTH SCHEMAS
# =============================================================================

class SubscriberGrowthPoint(BaseModel):
    """Data point for subscriber growth chart"""
    month: str = Field(..., description="Month in YYYY-MM format")
    subscribers: int = Field(..., description="Number of subscribers for that month")
    growth_rate: Optional[float] = Field(None, description="Growth rate percentage")

class SubscriberGrowthResponse(BaseModel):
    """Response schema for subscriber growth"""
    data: List[SubscriberGrowthPoint] = Field(..., description="List of growth data points")
    total_months: int = Field(..., description="Total number of months")
    total_subscribers: int = Field(..., description="Current total subscribers")
    
    class Config:
        from_attributes = True


# =============================================================================
# REGION DISTRIBUTION SCHEMAS
# =============================================================================

class RegionDistributionItem(BaseModel):
    """Region distribution data item"""
    region: str = Field(..., description="Region name")
    subscribers: int = Field(..., description="Number of subscribers in this region")
    percentage: float = Field(..., description="Percentage of total subscribers")

class RegionDistributionResponse(BaseModel):
    """Response schema for region distribution"""
    regions: List[RegionDistributionItem] = Field(..., description="List of region distributions")
    total_subscribers: int = Field(..., description="Total subscribers across all regions")
    
    class Config:
        from_attributes = True


# =============================================================================
# DEVICE USAGE SCHEMAS
# =============================================================================

class DeviceUsageItem(BaseModel):
    """Device usage data item"""
    device_type: str = Field(..., description="Device type (mobile, web, smart_tv, etc.)")
    subscribers: int = Field(..., description="Number of subscribers using this device")
    percentage: float = Field(..., description="Percentage of total subscribers")

class DeviceUsageResponse(BaseModel):
    """Response schema for device usage"""
    devices: List[DeviceUsageItem] = Field(..., description="List of device usage data")
    total_subscribers: int = Field(..., description="Total subscribers")
    
    class Config:
        from_attributes = True


# =============================================================================
# RETENTION SCHEMAS
# =============================================================================

class RetentionMetrics(BaseModel):
    """Retention rate metrics"""
    overall_retention: float = Field(..., description="Overall retention rate percentage")
    new_users_30d: float = Field(..., description="Retention rate for new users (30 days)")
    existing_users_90d: float = Field(..., description="Retention rate for existing users (90 days)")

class RetentionResponse(BaseModel):
    """Response schema for retention metrics"""
    retention: RetentionMetrics
    period_start: Optional[date] = Field(None, description="Start date of analysis period")
    period_end: Optional[date] = Field(None, description="End date of analysis period")
    
    class Config:
        from_attributes = True


# =============================================================================
# ACQUISITION CHANNELS SCHEMAS
# =============================================================================

class AcquisitionChannelItem(BaseModel):
    """Acquisition channel data item"""
    channel: str = Field(..., description="Acquisition channel name")
    subscribers: int = Field(..., description="Number of subscribers acquired through this channel")
    percentage: float = Field(..., description="Percentage of total acquisitions")

class AcquisitionChannelsResponse(BaseModel):
    """Response schema for acquisition channels"""
    channels: List[AcquisitionChannelItem] = Field(..., description="List of acquisition channel data")
    total_acquisitions: int = Field(..., description="Total acquisitions")
    
    class Config:
        from_attributes = True


# =============================================================================
# MONETIZATION SCHEMAS
# =============================================================================

class MonetizationMetrics(BaseModel):
    """Monetization performance metrics"""
    arpu: float = Field(..., description="Average Revenue Per User (ARPU)")
    cltv: float = Field(..., description="Customer Lifetime Value (CLTV)")
    mrr: float = Field(..., description="Monthly Recurring Revenue (MRR)")
    premium_percentage: float = Field(..., description="Percentage of premium subscribers")

class MonetizationResponse(BaseModel):
    """Response schema for monetization metrics"""
    metrics: MonetizationMetrics
    period_start: Optional[date] = Field(None, description="Start date of the period")
    period_end: Optional[date] = Field(None, description="End date of the period")
    
    class Config:
        from_attributes = True


# =============================================================================
# ACTIVITY FEED SCHEMAS
# =============================================================================

class ActivityFeedEvent(BaseModel):
    """Activity feed event item"""
    id: str = Field(..., description="Event ID")
    event_type: str = Field(..., description="Type of event")
    description: str = Field(..., description="Event description")
    timestamp: datetime = Field(..., description="Event timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional event metadata")

class ActivityFeedResponse(BaseModel):
    """Response schema for activity feed"""
    events: List[ActivityFeedEvent] = Field(..., description="List of recent platform events")
    total: int = Field(..., description="Total number of events")
    page: int = Field(1, description="Current page number")
    size: int = Field(20, description="Page size")
    
    class Config:
        from_attributes = True

