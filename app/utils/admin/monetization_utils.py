from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monetization import (
    AdCampaign,
    AdCampaignStat,
    AdType,
    CampaignStatus,
    MonetizationActivity,
    PlatformType,
)
from app.schemas.admin import (
    ActivityCreate,
    AdCampaignCreate,
    AdCampaignStatCreate,
    AdCampaignUpdate,
)


async def create_campaign(
    db: AsyncSession, campaign_data: AdCampaignCreate
) -> AdCampaign:
    """Create a new ad campaign"""
    campaign = AdCampaign(**campaign_data.model_dump())
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def get_campaign_by_id(
    db: AsyncSession, campaign_id: UUID
) -> Optional[AdCampaign]:
    """Get campaign by ID"""
    query = select(AdCampaign).where(
        and_(AdCampaign.id == campaign_id, AdCampaign.is_deleted == False)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_campaigns_list(
    db: AsyncSession,
    page: int = 1,
    size: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    status: Optional[CampaignStatus] = None,
    platform: Optional[PlatformType] = None,
    ad_type: Optional[AdType] = None,
    search: Optional[str] = None,
) -> Tuple[List[AdCampaign], int]:
    """Get paginated list of campaigns with filtering"""
    # Base query
    query = select(AdCampaign).where(AdCampaign.is_deleted == False)

    # Apply filters
    if status:
        query = query.where(AdCampaign.status == status)
    if platform:
        query = query.where(AdCampaign.target_platform == platform)
    if ad_type:
        query = query.where(AdCampaign.ad_type == ad_type)
    if search:
        search_term = f"%{search}%"
        query = query.where(AdCampaign.title.ilike(search_term))

    # Apply sorting
    sort_field = getattr(AdCampaign, sort_by, AdCampaign.created_at)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(sort_field)

    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # Execute query
    result = await db.execute(query)
    campaigns = result.scalars().all()

    # Get total count
    count_query = select(func.count(AdCampaign.id)).where(
        AdCampaign.is_deleted == False
    )
    if status:
        count_query = count_query.where(AdCampaign.status == status)
    if platform:
        count_query = count_query.where(AdCampaign.target_platform == platform)
    if ad_type:
        count_query = count_query.where(AdCampaign.ad_type == ad_type)
    if search:
        search_term = f"%{search}%"
        count_query = count_query.where(AdCampaign.title.ilike(search_term))

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return campaigns, total


async def update_campaign(
    db: AsyncSession, campaign_id: UUID, campaign_data: AdCampaignUpdate
) -> Optional[AdCampaign]:
    """Update campaign"""
    campaign = await get_campaign_by_id(db, campaign_id)
    if not campaign:
        return None

    # Update fields
    update_data = campaign_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)

    await db.commit()
    await db.refresh(campaign)
    return campaign


async def delete_campaign(db: AsyncSession, campaign_id: UUID) -> bool:
    """Soft delete campaign"""
    campaign = await get_campaign_by_id(db, campaign_id)
    if not campaign:
        return False

    campaign.is_deleted = True
    await db.commit()
    return True


# Campaign Stats
async def create_campaign_stat(
    db: AsyncSession, stat_data: AdCampaignStatCreate
) -> AdCampaignStat:
    """Create campaign stat"""
    stat = AdCampaignStat(**stat_data.model_dump())
    db.add(stat)
    await db.commit()
    await db.refresh(stat)
    return stat


async def get_campaign_stats(
    db: AsyncSession, campaign_id: UUID, limit: int = 30
) -> List[AdCampaignStat]:
    """Get campaign stats"""
    query = (
        select(AdCampaignStat)
        .where(AdCampaignStat.campaign_id == campaign_id)
        .order_by(desc(AdCampaignStat.stat_date))
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


# Activities
async def create_activity(
    db: AsyncSession, activity_data: ActivityCreate
) -> MonetizationActivity:
    """Create activity log"""
    activity = MonetizationActivity(**activity_data.model_dump())
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


async def get_activities(
    db: AsyncSession, limit: int = 50
) -> List[MonetizationActivity]:
    """Get recent activities"""
    query = (
        select(MonetizationActivity)
        .order_by(desc(MonetizationActivity.created_at))
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


# Performance Analytics
async def get_performance_summary(db: AsyncSession) -> dict:
    """Get performance summary"""
    # Get total metrics from campaigns
    query = select(
        func.sum(AdCampaign.revenue).label("total_revenue"),
        func.sum(AdCampaign.impressions).label("total_impressions"),
        func.sum(AdCampaign.clicks).label("total_clicks"),
    ).where(AdCampaign.is_deleted == False)

    result = await db.execute(query)
    row = result.first()

    total_revenue = row.total_revenue or 0.0
    total_impressions = row.total_impressions or 0
    total_clicks = row.total_clicks or 0

    # Calculate CTR and eCPM
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
    ecpm = (total_revenue / total_impressions * 1000) if total_impressions > 0 else 0.0

    return {
        "total_revenue": total_revenue,
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "ctr": round(ctr, 2),
        "ecpm": round(ecpm, 2),
    }


async def get_performance_trends(db: AsyncSession, months: int = 6) -> List[dict]:
    """Get performance trends over time"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=months * 30)

    # Create the date_trunc expression once and reuse it
    month_trunc = func.date_trunc("month", AdCampaignStat.stat_date)

    query = (
        select(
            month_trunc.label("month"),
            func.sum(AdCampaignStat.revenue).label("revenue"),
            func.sum(AdCampaignStat.impressions).label("impressions"),
        )
        .where(
            and_(
                AdCampaignStat.stat_date >= start_date,
                AdCampaignStat.stat_date <= end_date,
            )
        )
        .group_by(month_trunc)
        .order_by(month_trunc)
    )

    result = await db.execute(query)
    rows = result.fetchall()

    trends = []
    for row in rows:
        trends.append(
            {
                "month": row.month.strftime("%Y-%m"),
                "revenue": float(row.revenue or 0),
                "impressions": int(row.impressions or 0),
            }
        )

    return trends


async def get_engagement_by_ad_type(db: AsyncSession) -> List[dict]:
    """Get engagement metrics by ad type"""
    query = (
        select(
            AdCampaign.ad_type,
            func.sum(AdCampaign.impressions).label("impressions"),
            func.sum(AdCampaign.clicks).label("clicks"),
            func.sum(AdCampaign.revenue).label("revenue"),
        )
        .where(AdCampaign.is_deleted == False)
        .group_by(AdCampaign.ad_type)
    )

    result = await db.execute(query)
    rows = result.fetchall()

    engagement = []
    for row in rows:
        ctr = (row.clicks / row.impressions * 100) if row.impressions > 0 else 0.0
        engagement.append(
            {
                "ad_type": row.ad_type,
                "impressions": int(row.impressions or 0),
                "clicks": int(row.clicks or 0),
                "revenue": float(row.revenue or 0),
                "ctr": round(ctr, 2),
            }
        )

    return engagement


async def get_subscriber_segmentation(db: AsyncSession) -> dict:
    """Get subscriber segmentation data"""
    try:
        from sqlalchemy import text

        result = await db.execute(
            text("SELECT plan, COUNT(*) as cnt FROM subscriptions GROUP BY plan")
        )
        data = {row["plan"]: row["cnt"] for row in result}
        return data
    except Exception:
        return {
            "Free Tier": 0,
            "Basic Plan": 0,
            "Premium Access": 0,
            "VIP Elite": 0,
        }
