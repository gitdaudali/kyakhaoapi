# app/models/monetization.py
from datetime import datetime, date
import enum
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class PlatformEnum(str, enum.Enum):
    web = "web"
    android = "android"
    ios = "ios"
    smart_tv = "smart_tv"
    other = "other"


class AdTypeEnum(str, enum.Enum):
    banner = "banner"
    video = "video"
    native = "native"
    interstitial = "interstitial"
    other = "other"


class CampaignStatusEnum(str, enum.Enum):
    active = "active"
    paused = "paused"
    ended = "ended"
    draft = "draft"


class AdCampaign(Base):
    __tablename__ = "ad_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    target_platform = Column(Enum(PlatformEnum), nullable=False, default=PlatformEnum.web)
    ad_type = Column(Enum(AdTypeEnum), nullable=False, default=AdTypeEnum.banner)
    budget = Column(Float, nullable=False, default=0.0)
    status = Column(Enum(CampaignStatusEnum), nullable=False, default=CampaignStatusEnum.draft)

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    # aggregated counters (optional fields kept for quick reads)
    spend = Column(Float, nullable=False, default=0.0)
    impressions = Column(Integer, nullable=False, default=0)
    clicks = Column(Integer, nullable=False, default=0)
    revenue = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    stats = relationship("AdCampaignStat", back_populates="campaign", cascade="all, delete-orphan")
    activities = relationship("MonetizationActivity", back_populates="campaign", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AdCampaign(id={self.id}, title={self.title})>"


class AdCampaignStat(Base):
    """
    Daily (or periodic) aggregated stats for campaigns.
    We store date + aggregated metrics to make trends/aggregation fast.
    """
    __tablename__ = "ad_campaign_stats"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("ad_campaigns.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)  # ideally store one row per day
    impressions = Column(Integer, nullable=False, default=0)
    clicks = Column(Integer, nullable=False, default=0)
    revenue = Column(Float, nullable=False, default=0.0)

    campaign = relationship("AdCampaign", back_populates="stats")


class MonetizationActivity(Base):
    """
    Activity log for monetization events (budget updates, paused, created etc)
    """
    __tablename__ = "monetization_activity"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("ad_campaigns.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(255), nullable=False)
    note = Column(Text, nullable=True)
    meta = Column(Text, nullable=True)  # free-form JSON string if needed
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("AdCampaign", back_populates="activities")
