from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Text
from sqlmodel import Field

from app.models.base import BaseModel, TimestampMixin


class User(BaseModel, TimestampMixin, table=True):
    __tablename__ = "users_user"

    username: str = Field(max_length=150, unique=True, index=True)
    email: str = Field(max_length=254, unique=True, index=True)
    first_name: Optional[str] = Field(max_length=150, default=None)
    last_name: Optional[str] = Field(max_length=150, default=None)
    password: str = Field(max_length=128)
    is_active: bool = Field(default=True, index=True)
    is_staff: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    last_login: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    role: str = Field(max_length=20, default="user")
    bio: Optional[str] = Field(default=None, sa_type=Text)
    avatar_url: Optional[str] = Field(max_length=500, default=None)

    # Relationships will be handled separately

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
