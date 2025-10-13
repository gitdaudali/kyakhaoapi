from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.core.messages import (
    ACTIVITY_CREATED,
    CAMPAIGN_CREATED,
    CAMPAIGN_DELETED,
    CAMPAIGN_NOT_FOUND,
    CAMPAIGN_STAT_CREATED,
    CAMPAIGN_UPDATED,
    ENGAGEMENT_BY_TYPE_SUCCESS,
    PERFORMANCE_SUMMARY_SUCCESS,
    PERFORMANCE_TRENDS_SUCCESS,
    SUBSCRIBER_SEGMENTATION_SUCCESS,
)
from app.schemas.admin import (
    ActivityCreate,
    ActivityResponse,
    AdCampaignCreate,
    AdCampaignListResponse,
    AdCampaignQueryParams,
    AdCampaignResponse,
    AdCampaignStatCreate,
    AdCampaignStatResponse,
    AdCampaignUpdate,
    EngagementByTypeResponse,
    PerformanceSummary,
    PerformanceTrendsResponse,
    SubscriberSegmentationResponse,
)
from app.utils.admin.monetization_utils import (
    create_activity,
    create_campaign,
    create_campaign_stat,
    delete_campaign,
    get_activities,
    get_campaign_by_id,
    get_campaign_stats,
    get_campaigns_list,
    get_engagement_by_ad_type,
    get_performance_summary,
    get_performance_trends,
    get_subscriber_segmentation,
    update_campaign,
)
from app.utils.content_utils import calculate_pagination_info

router = APIRouter()


@router.get("/debug/auth-test")
async def debug_auth_test(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Debug endpoint to test authentication and authorization dependency injection.
    This endpoint will only work if the dependency chain is working properly.
    """
    return {
        "status": "SUCCESS",
        "message": "Dependency injection is working correctly",
        "user_info": {
            "user_id": str(current_user.id),
            "email": current_user.email,
            "is_staff": current_user.is_staff,
            "is_superuser": current_user.is_superuser,
            "role": current_user.role,
            "is_active": current_user.is_active,
        },
        "dependency_chain": {
            "HTTPBearer": "✅ Working",
            "get_current_user": "✅ Working", 
            "get_admin_user": "✅ Working",
            "AdminUser": "✅ Working"
        }
    }


@router.post("/campaigns/", response_model=AdCampaignResponse)
async def create_ad_campaign(
    current_user: AdminUser,
    campaign_data: AdCampaignCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new ad campaign (Admin only).
    Creates a new advertising campaign for monetization.
    """
    try:
        campaign = await create_campaign(db, campaign_data)

        # Log activity
        await create_activity(
            db,
            ActivityCreate(
                campaign_id=campaign.id,
                action="created_campaign",
                note=f"Created campaign: {campaign.title}",
            ),
        )

        return campaign
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating campaign: {str(e)}",
        )


@router.get("/campaigns/", response_model=AdCampaignListResponse)
async def get_ad_campaigns(
    current_user: AdminUser,
    query_params: AdCampaignQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get ad campaigns list with pagination and filtering (Admin only).
    Returns a paginated list of advertising campaigns.
    """
    try:
        filters = query_params.to_filters()
        pagination = query_params.to_pagination()

        campaigns, total = await get_campaigns_list(
            db=db,
            page=pagination["page"],
            size=pagination["size"],
            sort_by=pagination["sort_by"],
            sort_order=pagination["sort_order"],
            **filters,
        )

        pagination_info = calculate_pagination_info(
            pagination["page"], pagination["size"], total
        )

        return AdCampaignListResponse(items=campaigns, **pagination_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving campaigns: {str(e)}",
        )


@router.get("/campaigns/{campaign_id}", response_model=AdCampaignResponse)
async def get_ad_campaign(
    current_user: AdminUser,
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get ad campaign by ID (Admin only).
    Returns detailed information about a specific campaign.
    """
    try:
        campaign = await get_campaign_by_id(db, campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CAMPAIGN_NOT_FOUND
            )
        return campaign
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving campaign: {str(e)}",
        )


@router.put("/campaigns/{campaign_id}", response_model=AdCampaignResponse)
async def update_ad_campaign(
    current_user: AdminUser,
    campaign_id: UUID,
    campaign_data: AdCampaignUpdate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update ad campaign (Admin only).
    Updates an existing advertising campaign.
    """
    try:
        campaign = await update_campaign(db, campaign_id, campaign_data)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CAMPAIGN_NOT_FOUND
            )

        # Log activity
        await create_activity(
            db,
            ActivityCreate(
                campaign_id=campaign.id,
                action="updated_campaign",
                note=f"Updated campaign: {campaign.title}",
                meta=str(campaign_data.model_dump(exclude_unset=True)),
            ),
        )

        return campaign
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating campaign: {str(e)}",
        )


@router.delete("/campaigns/{campaign_id}")
async def delete_ad_campaign(
    current_user: AdminUser,
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete ad campaign (Admin only).
    Soft deletes an advertising campaign.
    """
    try:
        # Get campaign before deletion for logging
        campaign = await get_campaign_by_id(db, campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CAMPAIGN_NOT_FOUND
            )

        success = await delete_campaign(db, campaign_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CAMPAIGN_NOT_FOUND
            )

        # Log activity
        await create_activity(
            db,
            ActivityCreate(
                campaign_id=campaign_id,
                action="deleted_campaign",
                note=f"Deleted campaign: {campaign.title}",
            ),
        )

        return {"message": CAMPAIGN_DELETED}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting campaign: {str(e)}",
        )


# Campaign Stats endpoints
@router.post("/campaigns/stats/", response_model=AdCampaignStatResponse)
async def create_campaign_stat_endpoint(
    current_user: AdminUser,
    stat_data: AdCampaignStatCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create campaign stat (Admin only).
    Adds daily statistics for a campaign.
    """
    try:
        stat = await create_campaign_stat(db, stat_data)
        return stat
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating campaign stat: {str(e)}",
        )


@router.get(
    "/campaigns/{campaign_id}/stats/", response_model=list[AdCampaignStatResponse]
)
async def get_campaign_stats_endpoint(
    current_user: AdminUser,
    campaign_id: UUID,
    limit: int = Query(30, ge=1, le=100, description="Number of stats to return"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get campaign stats (Admin only).
    Returns recent statistics for a campaign.
    """
    try:
        # Verify campaign exists
        campaign = await get_campaign_by_id(db, campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CAMPAIGN_NOT_FOUND
            )

        stats = await get_campaign_stats(db, campaign_id, limit)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving campaign stats: {str(e)}",
        )


# Activity endpoints
@router.get("/activities/", response_model=list[ActivityResponse])
async def get_activities_endpoint(
    current_user: AdminUser,
    limit: int = Query(50, ge=1, le=200, description="Number of activities to return"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get monetization activities (Admin only).
    Returns recent monetization activities.
    """
    try:
        activities = await get_activities(db, limit)
        return activities
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving activities: {str(e)}",
        )


@router.post("/activities/", response_model=ActivityResponse)
async def create_activity_log(
    current_user: AdminUser,
    activity_data: ActivityCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create activity log (Admin only).
    Logs a monetization activity.
    """
    try:
        activity = await create_activity(db, activity_data)
        return activity
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating activity: {str(e)}",
        )


# Performance & Analytics endpoints
@router.get("/performance/summary/", response_model=PerformanceSummary)
async def get_performance_summary_endpoint(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get performance summary (Admin only).
    Returns overall monetization performance metrics.
    """
    try:
        summary = await get_performance_summary(db)
        return PerformanceSummary(**summary)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving performance summary: {str(e)}",
        )


@router.get("/performance/trends/", response_model=PerformanceTrendsResponse)
async def get_performance_trends_endpoint(
    current_user: AdminUser,
    months: int = Query(6, ge=1, le=24, description="Number of months to analyze"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get performance trends (Admin only).
    Returns performance trends over time.
    """
    try:
        trends = await get_performance_trends(db, months)
        return PerformanceTrendsResponse(trends=trends, total_months=len(trends))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving performance trends: {str(e)}",
        )


@router.get("/performance/engagement-by-type/", response_model=EngagementByTypeResponse)
async def get_engagement_by_type_endpoint(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get engagement by ad type (Admin only).
    Returns engagement metrics grouped by ad type.
    """
    try:
        engagement = await get_engagement_by_ad_type(db)
        return EngagementByTypeResponse(by_type=engagement)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving engagement by type: {str(e)}",
        )


@router.get(
    "/performance/subscriber-segmentation/",
    response_model=SubscriberSegmentationResponse,
)
async def get_subscriber_segmentation_endpoint(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get subscriber segmentation (Admin only).
    Returns subscriber counts by plan.
    """
    try:
        segments = await get_subscriber_segmentation(db)
        return SubscriberSegmentationResponse(segments=segments)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving subscriber segmentation: {str(e)}",
        )
