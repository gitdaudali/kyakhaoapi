from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.core.response_handler import (
    success_response,
    InternalServerException
)
from app.schemas.admin_analytics import (
    AnalyticsOverviewResponse,
    SubscriberGrowthResponse,
    RegionDistributionResponse,
    DeviceUsageResponse,
    RetentionResponse,
    AcquisitionChannelsResponse,
    MonetizationResponse,
    ActivityFeedResponse,
    OverviewSummary,
    SubscriberGrowthPoint,
    RegionDistributionItem,
    DeviceUsageItem,
    RetentionMetrics,
    AcquisitionChannelItem,
    MonetizationMetrics,
    ActivityFeedEvent,
)
from app.utils.analytics_utils import (
    get_overview_summary,
    get_subscriber_growth,
    get_region_distribution,
    get_device_usage,
    get_retention_metrics,
    get_acquisition_channels,
    get_monetization_metrics,
    get_activity_feed,
)

router = APIRouter()


# =============================================================================
# ANALYTICS OVERVIEW
# =============================================================================

@router.get("/overview", response_model=Any)
async def get_analytics_overview(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
    start_date: Optional[date] = Query(None, description="Start date for the overview period (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date for the overview period (YYYY-MM-DD)"),
) -> Any:
    """
    Get analytics overview with key performance indicators (KPIs).
    
    Returns:
    - Active Subscribers
    - Average View Time (in minutes)
    - Revenue per User (ARPU)
    - Monthly Churn Rate (percentage)
    """
    try:
        summary_data = await get_overview_summary(db, start_date, end_date)
        
        summary = OverviewSummary(**summary_data)
        
        response = AnalyticsOverviewResponse(
            summary=summary,
            period_start=start_date,
            period_end=end_date,
        )
        
        return success_response(
            message="Analytics overview retrieved successfully",
            data=response.dict()
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving analytics overview: {str(e)}"
        )


# =============================================================================
# SUBSCRIBER GROWTH
# =============================================================================

@router.get("/subscriber-growth", response_model=Any)
async def get_subscriber_growth_endpoint(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
    months: int = Query(12, ge=1, le=24, description="Number of months to analyze"),
) -> Any:
    """
    Get subscriber growth over time (monthly data points).
    
    Returns monthly subscriber counts with growth rates.
    """
    try:
        growth_data, total_subscribers = await get_subscriber_growth(db, months)
        
        growth_points = [
            SubscriberGrowthPoint(**point) for point in growth_data
        ]
        
        response = SubscriberGrowthResponse(
            data=growth_points,
            total_months=len(growth_points),
            total_subscribers=total_subscribers,
        )
        
        return success_response(
            message="Subscriber growth data retrieved successfully",
            data=response.dict()
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving subscriber growth: {str(e)}"
        )


# =============================================================================
# REGION DISTRIBUTION
# =============================================================================

@router.get("/region-distribution", response_model=Any)
async def get_region_distribution_endpoint(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get subscriber distribution by region.
    
    Returns:
    - Region name
    - Number of subscribers per region
    - Percentage of total subscribers
    """
    try:
        regions_data, total_subscribers = await get_region_distribution(db)
        
        regions = [
            RegionDistributionItem(**region) for region in regions_data
        ]
        
        response = RegionDistributionResponse(
            regions=regions,
            total_subscribers=total_subscribers,
        )
        
        return success_response(
            message="Region distribution retrieved successfully",
            data=response.dict()
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving region distribution: {str(e)}"
        )


# =============================================================================
# DEVICE USAGE
# =============================================================================

@router.get("/device-usage", response_model=Any)
async def get_device_usage_endpoint(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get device usage distribution.
    
    Returns:
    - Device type (Mobile, Web Browser, Smart TV, etc.)
    - Number of subscribers using each device
    - Percentage of total subscribers
    """
    try:
        devices_data, total_subscribers = await get_device_usage(db)
        
        devices = [
            DeviceUsageItem(**device) for device in devices_data
        ]
        
        response = DeviceUsageResponse(
            devices=devices,
            total_subscribers=total_subscribers,
        )
        
        return success_response(
            message="Device usage data retrieved successfully",
            data=response.dict()
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving device usage: {str(e)}"
        )


# =============================================================================
# RETENTION METRICS
# =============================================================================

@router.get("/retention", response_model=Any)
async def get_retention_endpoint(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
    start_date: Optional[date] = Query(None, description="Start date for retention analysis (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date for retention analysis (YYYY-MM-DD)"),
) -> Any:
    """
    Get retention rate metrics.
    
    Returns:
    - Overall retention rate (percentage)
    - New users (30D) retention rate
    - Existing users (90D) retention rate
    """
    try:
        retention_data = await get_retention_metrics(db, start_date, end_date)
        
        retention = RetentionMetrics(**retention_data)
        
        response = RetentionResponse(
            retention=retention,
            period_start=start_date,
            period_end=end_date,
        )
        
        return success_response(
            message="Retention metrics retrieved successfully",
            data=response.dict()
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving retention metrics: {str(e)}"
        )


# =============================================================================
# ACQUISITION CHANNELS
# =============================================================================

@router.get("/acquisition-channels", response_model=Any)
async def get_acquisition_channels_endpoint(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get acquisition channel distribution.
    
    Returns:
    - Channel name (Organic Search, Social Media, Paid Ads, Referrals)
    - Number of subscribers acquired through each channel
    - Percentage of total acquisitions
    """
    try:
        channels_data, total_acquisitions = await get_acquisition_channels(db)
        
        channels = [
            AcquisitionChannelItem(**channel) for channel in channels_data
        ]
        
        response = AcquisitionChannelsResponse(
            channels=channels,
            total_acquisitions=total_acquisitions,
        )
        
        return success_response(
            message="Acquisition channels data retrieved successfully",
            data=response.dict()
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving acquisition channels: {str(e)}"
        )


# =============================================================================
# MONETIZATION METRICS
# =============================================================================

@router.get("/monetization", response_model=Any)
async def get_monetization_endpoint(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
    start_date: Optional[date] = Query(None, description="Start date for monetization analysis (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date for monetization analysis (YYYY-MM-DD)"),
) -> Any:
    """
    Get monetization performance metrics.
    
    Returns:
    - ARPU (Average Revenue Per User)
    - CLTV (Customer Lifetime Value)
    - MRR (Monthly Recurring Revenue)
    - Premium percentage (percentage of premium subscribers)
    """
    try:
        monetization_data = await get_monetization_metrics(db, start_date, end_date)
        
        metrics = MonetizationMetrics(**monetization_data)
        
        response = MonetizationResponse(
            metrics=metrics,
            period_start=start_date,
            period_end=end_date,
        )
        
        return success_response(
            message="Monetization metrics retrieved successfully",
            data=response.dict()
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving monetization metrics: {str(e)}"
        )


# =============================================================================
# ACTIVITY FEED
# =============================================================================

@router.get("/activity-feed", response_model=Any)
async def get_activity_feed_endpoint(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="Number of events to return"),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
) -> Any:
    """
    Get recent platform activity feed.
    
    Returns:
    - List of recent platform events (content releases, milestones, etc.)
    - Event type, description, timestamp, and metadata
    """
    try:
        events_data, total = await get_activity_feed(db, limit, offset)
        
        events = [
            ActivityFeedEvent(**event) for event in events_data
        ]
        
        response = ActivityFeedResponse(
            events=events,
            total=total,
            page=(offset // limit) + 1 if limit > 0 else 1,
            size=limit,
        )
        
        return success_response(
            message="Activity feed retrieved successfully",
            data=response.dict()
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving activity feed: {str(e)}"
        )

