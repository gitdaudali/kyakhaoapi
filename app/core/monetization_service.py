# app/core/monetization_service.py
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.models.monetization import AdCampaign, AdCampaignStat, MonetizationActivity
from app.schemas import monetization as schemas


# CRUD for AdCampaign
async def create_campaign(db: AsyncSession, payload: schemas.AdCampaignCreate):
    db_item = AdCampaign(
        title=payload.title,
        target_platform=payload.target_platform,
        ad_type=payload.ad_type,
        budget=payload.budget,
        status=payload.status,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def get_campaign(db: AsyncSession, campaign_id: int):
    result = await db.execute(
        select(AdCampaign).filter(AdCampaign.id == campaign_id)
    )
    return result.scalar_one_or_none()


async def list_campaigns(db: AsyncSession, skip: int = 0, limit: int = 50):
    result = await db.execute(
        select(AdCampaign).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_campaign(db: AsyncSession, campaign_id: int, payload: schemas.AdCampaignUpdate):
    result = await db.execute(
        select(AdCampaign).filter(AdCampaign.id == campaign_id)
    )
    db_item = result.scalar_one_or_none()
    
    if not db_item:
        return None

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(db_item, field, value)

    await db.commit()
    await db.refresh(db_item)
    return db_item


async def delete_campaign(db: AsyncSession, campaign_id: int):
    result = await db.execute(
        select(AdCampaign).filter(AdCampaign.id == campaign_id)
    )
    db_item = result.scalar_one_or_none()
    
    if not db_item:
        return False

    await db.delete(db_item)
    await db.commit()
    return True


# Stats operations
async def create_stat(db: AsyncSession, payload: schemas.AdCampaignStatCreate):
    db_stat = AdCampaignStat(
        campaign_id=payload.campaign_id,
        date=payload.date,
        impressions=payload.impressions,
        clicks=payload.clicks,
        revenue=payload.revenue,
    )
    db.add(db_stat)

    # Update campaign aggregates
    result = await db.execute(
        select(AdCampaign).filter(AdCampaign.id == payload.campaign_id)
    )
    campaign = result.scalar_one_or_none()
    
    if campaign:
        campaign.impressions += payload.impressions
        campaign.clicks += payload.clicks
        campaign.revenue += payload.revenue
        campaign.spend += payload.revenue * 0.3  # example: 30% spend rate

    await db.commit()
    await db.refresh(db_stat)
    return db_stat


# Activity log operations
async def create_activity(db: AsyncSession, payload: schemas.ActivityCreate):
    db_item = MonetizationActivity(
        campaign_id=payload.campaign_id,
        action=payload.action,
        note=payload.note,
        meta=payload.meta,
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def list_activities(db: AsyncSession, limit: int = 50):
    result = await db.execute(
        select(MonetizationActivity)
        .order_by(MonetizationActivity.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


# Analytics
async def performance_summary(db: AsyncSession):
    result = await db.execute(
        select(
            func.coalesce(func.sum(AdCampaign.revenue), 0.0),
            func.coalesce(func.sum(AdCampaign.impressions), 0),
            func.coalesce(func.sum(AdCampaign.clicks), 0),
        )
    )
    total_revenue, total_impressions, total_clicks = result.one()

    ctr = (total_clicks / total_impressions * 100.0) if total_impressions > 0 else 0.0
    ecpm = (total_revenue / total_impressions * 1000.0) if total_impressions > 0 else 0.0

    return {
        "total_revenue": float(total_revenue),
        "total_impressions": int(total_impressions),
        "total_clicks": int(total_clicks),
        "ctr": round(ctr, 2),
        "ecpm": round(ecpm, 2),
    }


async def performance_trends(db: AsyncSession, months: int = 6):
    since = date.today() - timedelta(days=months * 30)
    
    # Using SQLAlchemy core instead of text() for async compatibility
    stmt = (
        select(
            func.date_trunc('month', AdCampaignStat.date).label('month'),
            func.sum(AdCampaignStat.revenue).label('revenue'),
            func.sum(AdCampaignStat.impressions).label('impressions')
        )
        .where(AdCampaignStat.date >= since)
        .group_by(func.date_trunc('month', AdCampaignStat.date))
        .order_by(func.date_trunc('month', AdCampaignStat.date))
    )
    
    result = await db.execute(stmt)
    rows = result.fetchall()
    
    return [
        {
            "month": row.month.strftime('%Y-%m'),
            "revenue": float(row.revenue or 0.0),
            "impressions": int(row.impressions or 0)
        }
        for row in rows
    ]


async def engagement_by_ad_type(db: AsyncSession):
    result = await db.execute(
        select(
            AdCampaign.ad_type,
            func.count(AdCampaign.id).label("count"),
            func.sum(AdCampaign.revenue).label("revenue"),
        )
        .group_by(AdCampaign.ad_type)
    )
    rows = result.fetchall()
    
    return [
        {
            "ad_type": row.ad_type,
            "count": int(row.count or 0),
            "revenue": float(row.revenue or 0.0)
        }
        for row in rows
    ]