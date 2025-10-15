from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, Text, Boolean, Integer
from sqlmodel import Field, SQLModel

from app.models.base import BaseModel, TimestampMixin


class FAQ(BaseModel, TimestampMixin, table=True):
    """FAQ model for storing frequently asked questions"""

    __tablename__ = "faqs"

    question: str = Field(
        ...,
        max_length=500,
        description="The FAQ question",
        sa_column=Column(String(500), nullable=False),
    )
    answer: str = Field(
        ...,
        description="The FAQ answer",
        sa_column=Column(Text, nullable=False),
    )
    category: Optional[str] = Field(
        None,
        max_length=100,
        description="FAQ category for organization",
        sa_column=Column(String(100), nullable=True),
    )
    is_active: bool = Field(
        True,
        description="Whether the FAQ is active and visible to users",
        sa_column=Column(Boolean, nullable=False, default=True),
    )
    is_featured: bool = Field(
        False,
        description="Whether the FAQ is featured and should be shown prominently",
        sa_column=Column(Boolean, nullable=False, default=False),
    )
    sort_order: int = Field(
        0,
        description="Sort order for displaying FAQs",
        sa_column=Column(Integer, nullable=False, default=0),
    )
    view_count: int = Field(
        0,
        description="Number of times this FAQ has been viewed",
        sa_column=Column(Integer, nullable=False, default=0),
    )

    class Config:
        from_attributes = True
