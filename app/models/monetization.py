import uuid
from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class PlatformType(str, Enum):
    """Platform types for ad campaigns"""

    WEB = "web"
    ANDROID = "android"
    IOS = "ios"
    SMART_TV = "smart_tv"
    OTHER = "other"


class AdType(str, Enum):
    """Ad types for campaigns"""

    BANNER = "banner"
    VIDEO = "video"
    NATIVE = "native"
    INTERSTITIAL = "interstitial"
    OTHER = "other"


class CampaignStatus(str, Enum):
    """Campaign status options"""

    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    DRAFT = "draft"


class AdCampaign(BaseModel, TimestampMixin, table=True):
    """Ad campaign model for monetization"""

    __tablename__ = "ad_campaigns"

    title: str = Field(sa_type=String(255), nullable=False, index=True)
    target_platform: PlatformType = Field(default=PlatformType.WEB, index=True)
    ad_type: AdType = Field(default=AdType.BANNER, index=True)
    budget: float = Field(sa_type=Float, default=0.0, nullable=False)
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT, index=True)

    start_date: Optional[date] = Field(sa_type=Date, default=None)
    end_date: Optional[date] = Field(sa_type=Date, default=None)

    # Aggregated counters for quick reads
    spend: float = Field(sa_type=Float, default=0.0, nullable=False)
    impressions: int = Field(sa_type=Integer, default=0, nullable=False)
    clicks: int = Field(sa_type=Integer, default=0, nullable=False)
    revenue: float = Field(sa_type=Float, default=0.0, nullable=False)

    # Relationships
    stats: List["AdCampaignStat"] = Relationship(
        back_populates="campaign",
        cascade_delete=True,
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    activities: List["MonetizationActivity"] = Relationship(
        back_populates="campaign",
        cascade_delete=True,
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class AdCampaignStat(BaseModel, TimestampMixin, table=True):
    """Daily aggregated stats for campaigns"""

    __tablename__ = "ad_campaign_stats"

    campaign_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="ad_campaigns.id",
        nullable=False,
        index=True,
    )
    stat_date: date = Field(sa_type=Date, nullable=False, index=True)
    impressions: int = Field(sa_type=Integer, default=0, nullable=False)
    clicks: int = Field(sa_type=Integer, default=0, nullable=False)
    revenue: float = Field(sa_type=Float, default=0.0, nullable=False)

    # Relationships
    campaign: Optional["AdCampaign"] = Relationship(back_populates="stats")


class MonetizationActivity(BaseModel, TimestampMixin, table=True):
    """Activity log for monetization events"""

    __tablename__ = "monetization_activity"

    campaign_id: Optional[uuid.UUID] = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="ad_campaigns.id",
        nullable=True,
        index=True,
    )
    action: str = Field(sa_type=String(255), nullable=False, index=True)
    note: Optional[str] = Field(sa_type=Text, default=None)
    meta: Optional[str] = Field(sa_type=Text, default=None)  # JSON string

    # Relationships
    campaign: Optional["AdCampaign"] = Relationship(back_populates="activities")
