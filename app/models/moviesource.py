from sqlalchemy import Column, Boolean, Text, Index
from sqlmodel import Field

from app.models.base import BaseModel, TimestampMixin


class MovieSource(BaseModel, TimestampMixin, table=True):
    """Movie source model for storing source-destination mappings"""

    __tablename__ = "moviesources"

    source: str = Field(
        ...,
        max_length=500,
        description="Source URL or identifier",
        sa_column=Column(Text, nullable=False),
    )
    destination: str = Field(
        ...,
        max_length=500,
        description="Destination URL or identifier",
        sa_column=Column(Text, nullable=False),
    )
    active: bool = Field(
        True,
        description="Whether the movie source is active",
        sa_column=Column(Boolean, nullable=False, default=True),
    )

    __table_args__ = (
        Index("ix_moviesources_active", "active"),
    )

    def __repr__(self):
        return f"<MovieSource(id={self.id}, source='{self.source[:50]}...', active={self.active})>"