"""Contact message model."""
import uuid
from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from app.models.base import BaseModel, TimestampMixin


class ContactMessage(BaseModel, TimestampMixin, table=True):
    """Model for contact form submissions."""

    __tablename__ = "contact_messages"

    name: str = Field(sa_type=String(255), nullable=False, max_length=255)
    email: str = Field(sa_type=String(255), nullable=False, max_length=255, index=True)
    phone: Optional[str] = Field(sa_type=String(50), nullable=True, default=None, max_length=50)
    message: str = Field(sa_type=Text, nullable=False)

