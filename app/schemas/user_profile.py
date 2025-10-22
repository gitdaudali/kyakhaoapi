from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class ProfileType(str, Enum):
    ADULT = "ADULT"
    CHILD = "CHILD"
    TEEN = "TEEN"


def get_profile_metadata(profile_type: str) -> dict:
    """Get profile metadata based on profile type"""
    profile_info = {
        "ADULT": {"is_kids": False, "default_age_limit": 18},
        "TEEN": {"is_kids": False, "default_age_limit": 16},
        "CHILD": {"is_kids": True, "default_age_limit": 10}
    }
    return profile_info.get(profile_type, {"is_kids": False, "default_age_limit": 18})


def is_kids_profile(profile_type: str) -> bool:
    """Check if profile type is for kids"""
    return profile_type == "CHILD"


# Removed ProfileStatus enum - using boolean is_active instead


class ParentalControls(BaseModel):
    enabled: bool = False
    content_restrictions: Optional[str] = None
    viewing_time_limit: Optional[int] = None  # Minutes per day
    bedtime_start: Optional[str] = None  # HH:MM format
    bedtime_end: Optional[str] = None  # HH:MM format


class UserProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Profile name")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Profile avatar URL")
    profile_type: str = Field("ADULT", description="Profile type")
    age_rating_limit: int = Field(18, description="Age rating limit for content")
    language_preference: str = Field("en", max_length=10, description="Preferred language")
    subtitle_preference: str = Field("en", max_length=10, description="Preferred subtitle language")
    parental_controls: Optional[ParentalControls] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    profile_type: Optional[str] = None
    age_rating_limit: Optional[int] = None
    language_preference: Optional[str] = Field(None, max_length=10)
    subtitle_preference: Optional[str] = Field(None, max_length=10)
    parental_controls: Optional[ParentalControls] = None


class UserProfileResponse(UserProfileBase):
    id: UUID
    user_id: UUID
    is_primary: bool
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None
    
    @property
    def is_kids_profile(self) -> bool:
        """Derive is_kids_profile from profile_type"""
        return self.profile_type == "CHILD"
    
    class Config:
        from_attributes = True


class UserProfileListData(BaseModel):
    profiles: List[UserProfileResponse]
    total: int
    primary_profile_id: Optional[UUID] = None


class UserProfileListResponse(BaseModel):
    success: bool = True
    message: str = "Profiles retrieved successfully"
    data: UserProfileListData


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
