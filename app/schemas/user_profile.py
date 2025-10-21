from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class ProfileType(str, Enum):
    STANDARD = "standard"


class ProfileStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class ParentalControls(BaseModel):
    enabled: bool = False
    content_restrictions: Optional[str] = None
    viewing_time_limit: Optional[int] = None  # Minutes per day
    bedtime_start: Optional[str] = None  # HH:MM format
    bedtime_end: Optional[str] = None  # HH:MM format


class UserProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Profile name")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Profile avatar URL")
    profile_type: ProfileType = Field(ProfileType.STANDARD, description="Profile type")
    language_preference: str = Field("en", max_length=10, description="Preferred language")
    subtitle_preference: str = Field("en", max_length=10, description="Preferred subtitle language")
    parental_controls: Optional[ParentalControls] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    profile_type: Optional[ProfileType] = None
    language_preference: Optional[str] = Field(None, max_length=10)
    subtitle_preference: Optional[str] = Field(None, max_length=10)
    parental_controls: Optional[ParentalControls] = None


class UserProfileResponse(UserProfileBase):
    id: UUID
    user_id: UUID
    is_primary: bool
    status: ProfileStatus
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserProfileListResponse(BaseModel):
    profiles: List[UserProfileResponse]
    total: int
    primary_profile_id: Optional[UUID] = None


class ProfileSwitchRequest(BaseModel):
    profile_id: UUID = Field(..., description="Profile ID to switch to")


class ProfileSwitchResponse(BaseModel):
    message: str
    profile: UserProfileResponse
    access_token: str  # New token with profile context


class ProfileDeleteResponse(BaseModel):
    message: str
    deleted_profile_id: UUID


class ProfileStats(BaseModel):
    total_watch_time_hours: float
    movies_watched: int
    tv_episodes_watched: int
    favorite_genres: List[str]
    last_watched_at: Optional[datetime] = None
