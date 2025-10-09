from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.core.messages import (
    CAMPAIGN_DELETED, 
    CAMPAIGN_NOT_FOUND,
    CAMPAIGN_CREATED,
    CAMPAIGN_UPDATED,
    CAMPAIGN_STAT_CREATED,
    ACTIVITY_CREATED,
    PERFORMANCE_SUMMARY_SUCCESS,
    PERFORMANCE_TRENDS_SUCCESS,
    ENGAGEMENT_BY_TYPE_SUCCESS,
    SUBSCRIBER_SEGMENTATION_SUCCESS
)
from app.core.response_handler import (
    success_response,
    error_response,
    NotFoundException,
    InternalServerException
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


@router.post("/campaigns/", response_model=AdCampaignResponse)
async def create_ad_campaign(
    current_user: AdminUser,
    campaign_data: AdCampaignCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new ad campaign
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

        return success_response(
            message=CAMPAIGN_CREATED,
            data=campaign.dict() if hasattr(campaign, 'dict') else campaign
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error creating campaign: {str(e)}"
        )


@router.get("/campaigns/", response_model=AdCampaignListResponse)
async def get_ad_campaigns(
    current_user: AdminUser,
    query_params: AdCampaignQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get ad campaigns list with pagination and filtering
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

        response_data = AdCampaignListResponse(items=campaigns, **pagination_info)
        return success_response(
            message="Campaigns retrieved successfully",
            data=response_data.dict()
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving campaigns: {str(e)}"
        )


@router.get("/campaigns/{campaign_id}", response_model=AdCampaignResponse)
async def get_ad_campaign(
    current_user: AdminUser,
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get ad campaign by ID.
    Returns detailed information about a specific campaign.
    """
    try:
        campaign = await get_campaign_by_id(db, campaign_id)
        if not campaign:
            raise NotFoundException(detail=CAMPAIGN_NOT_FOUND)
        
        return success_response(
            message="Campaign retrieved successfully",
            data=campaign.dict() if hasattr(campaign, 'dict') else campaign
        )
    except HTTPException:
        raise
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving campaign: {str(e)}"
        )


@router.put("/campaigns/{campaign_id}", response_model=AdCampaignResponse)
async def update_ad_campaign(
    current_user: AdminUser,
    campaign_id: UUID,
    campaign_data: AdCampaignUpdate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update ad campaign.
    Updates an existing advertising campaign.
    """
    try:
        campaign = await update_campaign(db, campaign_id, campaign_data)
        if not campaign:
            raise NotFoundException(detail=CAMPAIGN_NOT_FOUND)

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

        return success_response(
            message=CAMPAIGN_UPDATED,
            data=campaign.dict() if hasattr(campaign, 'dict') else campaign
        )
    except HTTPException:
        raise
    except Exception as e:
        raise InternalServerException(
            detail=f"Error updating campaign: {str(e)}"
        )


@router.delete("/campaigns/{campaign_id}")
async def delete_ad_campaign(
    current_user: AdminUser,
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete ad campaign.
    Soft deletes an advertising campaign.
    """
    try:
        # Get campaign before deletion for logging
        campaign = await get_campaign_by_id(db, campaign_id)
        if not campaign:
            raise NotFoundException(detail=CAMPAIGN_NOT_FOUND)

        success = await delete_campaign(db, campaign_id)
        if not success:
            raise NotFoundException(detail=CAMPAIGN_NOT_FOUND)

        # Log activity
        await create_activity(
            db,
            ActivityCreate(
                campaign_id=campaign_id,
                action="deleted_campaign",
                note=f"Deleted campaign: {campaign.title}",
            ),
        )

        return success_response(
            message=CAMPAIGN_DELETED,
            data={"campaign_id": str(campaign_id)}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise InternalServerException(
            detail=f"Error deleting campaign: {str(e)}"
        )


# Campaign Stats endpoints
@router.post("/campaigns/stats/", response_model=AdCampaignStatResponse)
async def create_campaign_stat_endpoint(
    current_user: AdminUser,
    stat_data: AdCampaignStatCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create campaign stat.
    Adds daily statistics for a campaign.
    """
    try:
        stat = await create_campaign_stat(db, stat_data)
        return success_response(
            message=CAMPAIGN_STAT_CREATED,
            data=stat.dict() if hasattr(stat, 'dict') else stat
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error creating campaign stat: {str(e)}"
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
    Get campaign stats.
    Returns recent statistics for a campaign.
    """
    try:
        # Verify campaign exists
        campaign = await get_campaign_by_id(db, campaign_id)
        if not campaign:
            raise NotFoundException(detail=CAMPAIGN_NOT_FOUND)

        stats = await get_campaign_stats(db, campaign_id, limit)
        return success_response(
            message="Campaign stats retrieved successfully",
            data=[stat.dict() if hasattr(stat, 'dict') else stat for stat in stats]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving campaign stats: {str(e)}"
        )


@router.get("/activities/", response_model=list[ActivityResponse])
async def get_activities_endpoint(
    current_user: AdminUser,
    limit: int = Query(50, ge=1, le=200, description="Number of activities to return"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get monetization activities.
    Returns recent monetization activities.
    """
    try:
        activities = await get_activities(db, limit)
        return success_response(
            message="Activities retrieved successfully",
            data=[activity.dict() if hasattr(activity, 'dict') else activity for activity in activities]
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving activities: {str(e)}"
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
        return success_response(
            message=ACTIVITY_CREATED,
            data=activity.dict() if hasattr(activity, 'dict') else activity
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error creating activity: {str(e)}"
        )


@router.get("/performance/summary/", response_model=PerformanceSummary)
async def get_performance_summary_endpoint(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get performance summary.
    Returns overall monetization performance metrics.
    """
    try:
        summary = await get_performance_summary(db)
        return success_response(
            message=PERFORMANCE_SUMMARY_SUCCESS,
            data=PerformanceSummary(**summary).dict()
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving performance summary: {str(e)}"
        )


@router.get("/performance/trends/", response_model=PerformanceTrendsResponse)
async def get_performance_trends_endpoint(
    current_user: AdminUser,
    months: int = Query(6, ge=1, le=24, description="Number of months to analyze"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get performance trends.
    Returns performance trends over time.
    """
    try:
        trends = await get_performance_trends(db, months)
        return success_response(
            message=PERFORMANCE_TRENDS_SUCCESS,
            data=PerformanceTrendsResponse(trends=trends, total_months=len(trends)).dict()
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving performance trends: {str(e)}"
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
        return success_response(
            message=ENGAGEMENT_BY_TYPE_SUCCESS,
            data=EngagementByTypeResponse(by_type=engagement).dict()
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving engagement by type: {str(e)}"
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
    Get subscriber segmentation.
    Returns subscriber counts by plan.
    """
    try:
        segments = await get_subscriber_segmentation(db)
        return success_response(
            message=SUBSCRIBER_SEGMENTATION_SUCCESS,
            data=SubscriberSegmentationResponse(segments=segments).dict()
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving subscriber segmentation: {str(e)}"
        )
