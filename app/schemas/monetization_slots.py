from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.monetization import AdType


class SlotStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    DRAFT = "draft"


class AdSlotBase(BaseModel):
    name: str = Field(..., description="Slot name")
    slot_type: AdType = Field(..., description="Slot type (dropdown, enum)")
    page_location: Optional[str] = Field(None, description="Page location (dropdown, e.g. homepage_top, sidebar, etc.)")
    campaign_id: Optional[UUID] = Field(None, description="Linked Campaign (for dropdown, use AdCampaign list)")
    status: SlotStatus = Field(SlotStatus.DRAFT, description="Slot status")
    dimensions: Optional[str] = Field(None, description="Ad slot dimensions WxH (string)")
    preview_image_url: Optional[str] = Field(None, description="Preview Image S3 URL")
    description: Optional[str] = Field(None, description="Slot Description")


class AdSlotCreate(AdSlotBase):
    pass


class AdSlotUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Slot name")
    slot_type: Optional[AdType] = Field(None, description="Slot type")
    page_location: Optional[str] = Field(None, description="Page location")
    campaign_id: Optional[UUID] = Field(None, description="Linked Campaign")
    status: Optional[SlotStatus] = Field(None, description="Slot status")
    dimensions: Optional[str] = Field(None, description="Ad slot dimensions WxH (string)")
    preview_image_url: Optional[str] = Field(None, description="Preview Image S3 URL")
    description: Optional[str] = Field(None, description="Slot Description")


class AdSlotResponse(AdSlotBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False

    class Config:
        from_attributes = True


class AdSlotListResponse(BaseModel):
    items: List[AdSlotResponse]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

    class Config:
        from_attributes = True
