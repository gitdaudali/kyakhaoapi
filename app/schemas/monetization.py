# app/schemas/monetization.py
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# --- Campaign ---
class AdCampaignBase(BaseModel):
    title: str
    target_platform: str
    ad_type: str
    budget: float = 0.0
    status: Optional[str] = "draft"
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class AdCampaignCreate(AdCampaignBase):
    pass


class AdCampaignUpdate(BaseModel):
    title: Optional[str] = None
    target_platform: Optional[str] = None
    ad_type: Optional[str] = None
    budget: Optional[float] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class AdCampaignOut(AdCampaignBase):
    id: int
    spend: float
    impressions: int
    clicks: int
    revenue: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# --- Stats ---
class AdCampaignStatCreate(BaseModel):
    campaign_id: int
    date: date
    impressions: int = 0
    clicks: int = 0
    revenue: float = 0.0


class AdCampaignStatOut(BaseModel):
    id: int
    campaign_id: int
    date: date
    impressions: int
    clicks: int
    revenue: float

    class Config:
        orm_mode = True


# --- Activity ---
class ActivityCreate(BaseModel):
    campaign_id: Optional[int] = None
    action: str
    note: Optional[str] = None
    meta: Optional[str] = None


class ActivityOut(BaseModel):
    id: int
    campaign_id: Optional[int]
    action: str
    note: Optional[str]
    meta: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


# --- Performance outputs ---
class PerformanceSummary(BaseModel):
    total_revenue: float = 0.0
    total_impressions: int = 0
    total_clicks: int = 0
    ctr: float = 0.0  # percent
    ecpm: float = 0.0  # dollars per 1000 impressions


class TrendPoint(BaseModel):
    month: str  # "2025-06"
    revenue: float
    impressions: int
