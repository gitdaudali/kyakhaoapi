from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core import monetization_service as monetization
from app.schemas import monetization as schemas


router = APIRouter()


# Campaign endpoints
@router.post("/ads/", response_model=schemas.AdCampaignOut)
async def create_ad_campaign(
    payload: schemas.AdCampaignCreate, 
    db: AsyncSession = Depends(get_db)
):
    return await monetization.create_campaign(db=db, payload=payload)


@router.get("/ads/", response_model=List[schemas.AdCampaignOut])
async def list_ad_campaigns(
    skip: int = 0, 
    limit: int = 50, 
    db: AsyncSession = Depends(get_db)
):
    return await monetization.list_campaigns(db=db, skip=skip, limit=limit)


@router.get("/ads/{campaign_id}", response_model=schemas.AdCampaignOut)
async def get_ad_campaign(
    campaign_id: int, 
    db: AsyncSession = Depends(get_db)
):
    item = await monetization.get_campaign(db=db, campaign_id=campaign_id)
    if not item:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return item


@router.put("/ads/{campaign_id}", response_model=schemas.AdCampaignOut)
async def update_ad_campaign(
    campaign_id: int, 
    payload: schemas.AdCampaignUpdate, 
    db: AsyncSession = Depends(get_db)
):
    updated = await monetization.update_campaign(
        db=db, campaign_id=campaign_id, payload=payload
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Log activity
    await monetization.create_activity(
        db=db,
        payload=schemas.ActivityCreate(
            campaign_id=campaign_id,
            action="updated_campaign",
            note=str(payload.dict(exclude_unset=True))
        )
    )
    return updated


@router.delete("/ads/{campaign_id}")
async def delete_ad_campaign(
    campaign_id: int, 
    db: AsyncSession = Depends(get_db)
):
    ok = await monetization.delete_campaign(db=db, campaign_id=campaign_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    await monetization.create_activity(
        db=db,
        payload=schemas.ActivityCreate(
            campaign_id=campaign_id,
            action="deleted_campaign"
        )
    )
    return {"ok": True}


# Stats ingestion (add daily stat)
@router.post("/ads/stats", response_model=schemas.AdCampaignStatOut)
async def add_campaign_stat(
    payload: schemas.AdCampaignStatCreate, 
    db: AsyncSession = Depends(get_db)
):
    return await monetization.create_stat(db=db, payload=payload)


# Activities
@router.get("/ads/activity", response_model=List[schemas.ActivityOut])
async def get_activities(
    limit: int = Query(50, le=200), 
    db: AsyncSession = Depends(get_db)
):
    return await monetization.list_activities(db=db, limit=limit)


@router.post("/ads/activity", response_model=schemas.ActivityOut)
async def add_activity(
    payload: schemas.ActivityCreate, 
    db: AsyncSession = Depends(get_db)
):
    return await monetization.create_activity(db=db, payload=payload)


# Performance & Analytics
@router.get("/ads/performance/summary", response_model=schemas.PerformanceSummary)
async def performance_summary(db: AsyncSession = Depends(get_db)):
    summary = await monetization.performance_summary(db=db)
    return schemas.PerformanceSummary(**summary)


@router.get("/ads/performance/trends", response_model=List[schemas.TrendPoint])
async def performance_trends(
    months: int = 6, 
    db: AsyncSession = Depends(get_db)
):
    rows = await monetization.performance_trends(db=db, months=months)
    return [
        schemas.TrendPoint(
            month=r["month"], 
            revenue=r["revenue"], 
            impressions=r["impressions"]
        ) for r in rows
    ]


@router.get("/ads/performance/types")
async def engagement_by_type(db: AsyncSession = Depends(get_db)):
    rows = await monetization.engagement_by_ad_type(db=db)
    return {"by_type": rows}


@router.get("/ads/performance/subscriber-segmentation")
async def subscriber_segmentation(db: AsyncSession = Depends(get_db)):
    try:
        from sqlalchemy import text
        result = await db.execute(
            text("SELECT plan, COUNT(*) as cnt FROM subscriptions GROUP BY plan")
        )
        data = {row["plan"]: row["cnt"] for row in result}
        return {"segments": data}
    except Exception:
        return {
            "segments": {
                "Free Tier": 0,
                "Basic Plan": 0,
                "Premium Access": 0,
                "VIP Elite": 0,
            }
        }