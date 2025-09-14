import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin class for adding timestamp fields to models"""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=TIMESTAMP(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=TIMESTAMP(timezone=True),
        sa_column_kwargs={"onupdate": func.now()},
        nullable=False,
    )
    is_deleted: bool = Field(default=False, index=True)


class BaseModel(SQLModel):
    """Base model class with common fields and functionality"""

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_type=UUID(as_uuid=True),
        nullable=False,
    )

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
