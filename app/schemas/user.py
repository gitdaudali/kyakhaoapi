from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import UUID4, BaseModel, EmailStr, Field, field_serializer

from app.models.user import ProfileStatus, SignupType, UserRole


class UserBase(BaseModel):
    email: EmailStr
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

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)

    @field_serializer("created_at", "updated_at", "last_login")
    def serialize_datetime(self, value: datetime) -> Optional[str]:
        return value.isoformat() if value else None

    class Config:
        from_attributes = True


class User(UserInDB):
    pass
