from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, EmailStr, Field

from app.models.user import ProfileStatus, SignupType, UserRole


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserInDB(UserBase):
    id: UUID4
    is_active: bool
    is_staff: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    last_login: Optional[datetime] = None
    role: UserRole
    profile_status: ProfileStatus
    signup_type: SignupType
    google_id: Optional[str] = None
    apple_id: Optional[str] = None

    class Config:
        from_attributes = True


class User(UserInDB):
    pass


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class ProfileResponse(BaseModel):
    """Response schema for user profile."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


# Search History Schemas
class SearchHistoryCreate(BaseModel):
    """Schema for creating a search history entry"""

    search_query: str = Field(
        ..., min_length=1, max_length=255, description="Search query text"
    )


class SearchHistoryResponse(BaseModel):
    """Schema for search history response"""

    id: UUID4 = Field(..., description="Search history ID")
    search_query: str = Field(..., description="Search query text")
    search_count: int = Field(
        ..., description="Number of times this search was performed"
    )
    last_searched_at: datetime = Field(
        ..., description="Last time this search was performed"
    )
    created_at: datetime = Field(..., description="When this search was first created")

    class Config:
        from_attributes = True


class SearchHistoryListResponse(BaseModel):
    """Schema for search history list response"""

    items: List[SearchHistoryResponse] = Field(
        ..., description="List of search history entries"
    )
    total: int = Field(..., description="Total number of search history entries")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class SearchHistoryDeleteResponse(BaseModel):
    """Schema for search history deletion response"""

    message: str = Field(..., description="Success message")
    deleted_count: int = Field(..., description="Number of entries deleted")
