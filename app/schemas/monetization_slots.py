from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator, field_serializer

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

    @validator("slot_type", pre=True)
    def convert_slot_type(cls, v):
        """Convert string to AdType enum"""
        if isinstance(v, str):
            try:
                return AdType(v)
            except ValueError:
                return AdType.BANNER  # Default fallback
        if isinstance(v, AdType):
            return v
        return v

    @validator("status", pre=True)
    def convert_status(cls, v):
        """Convert string to SlotStatus enum"""
        if isinstance(v, str):
            try:
                return SlotStatus(v)
            except ValueError:
                return SlotStatus.DRAFT  # Default fallback
        if isinstance(v, SlotStatus):
            return v
        return v

    @field_serializer("slot_type")
    def serialize_slot_type(self, value: AdType) -> str:
        """Serialize AdType enum to string"""
        if isinstance(value, Enum):
            return value.value
        return str(value) if value else None

    @field_serializer("status")
    def serialize_status(self, value: SlotStatus) -> str:
        """Serialize SlotStatus enum to string"""
        if isinstance(value, Enum):
            return value.value
        return str(value) if value else None

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
