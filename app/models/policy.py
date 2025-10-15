from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Text, Boolean, DateTime
from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin

class PolicyType(str, Enum):
    PRIVACY_POLICY = "privacy_policy"
    TERMS_OF_SERVICE = "terms_of_service"
    COOKIE_POLICY = "cookie_policy"
    DATA_RETENTION_POLICY = "data_retention_policy"
    ACCEPTABLE_USE_POLICY = "acceptable_use_policy"
    INCIDENT_RESPONSE_PLAN = "incident_response_plan"

class PolicyStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Policy(BaseModel, TimestampMixin, table=True):
    __tablename__ = "policies"
    
    title: str = Field(sa_type=String(255), nullable=False, index=True)
    slug: str = Field(sa_type=String(300), unique=True, index=True)
    description: str = Field(sa_type=String(4000), nullable=False, description="Policy description (3k-4k characters)")
    content: str = Field(sa_type=Text, nullable=False)
    policy_type: PolicyType = Field(sa_type=String(50), nullable=False, index=True)
    status: PolicyStatus = Field(sa_type=String(20), default=PolicyStatus.DRAFT, index=True)
    version: str = Field(sa_type=String(20), default="1.0")
    is_active: bool = Field(default=True, index=True)
    effective_date: Optional[datetime] = Field(sa_type=DateTime, default=None)
    last_reviewed_at: Optional[datetime] = Field(sa_type=DateTime, default=None)
    next_review_date: Optional[datetime] = Field(sa_type=DateTime, default=None)
    author_id: Optional[UUID] = Field(default=None, index=True)
    reviewer_id: Optional[UUID] = Field(default=None, index=True)
    notes: Optional[str] = Field(sa_type=Text, default=None)