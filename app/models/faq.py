"""FAQ model."""
from typing import Optional

from sqlalchemy import Boolean, Text
from sqlmodel import Field

from app.models.base import BaseModel, TimestampMixin


class FAQ(BaseModel, TimestampMixin, table=True):
    """FAQ model for storing frequently asked questions."""

    __tablename__ = "faqs"

    question: str = Field(sa_type=Text, nullable=False, unique=True, index=True)
    answer: str = Field(sa_type=Text, nullable=False)
    is_published: bool = Field(default=False, sa_type=Boolean, index=True)
    order: int = Field(default=0, index=True)
    category: Optional[str] = Field(default=None, max_length=100, index=True)

