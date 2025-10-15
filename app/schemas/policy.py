from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.policy import PolicyType


class UserPolicyResponse(BaseModel):
    """User response schema for policy (no admin fields)"""
    
    id: UUID = Field(..., description="Policy ID")
    title: str = Field(..., description="Policy title")
    slug: str = Field(..., description="Policy slug")
    description: str = Field(..., description="Policy description")
    content: str = Field(..., description="Policy content")
    policy_type: PolicyType = Field(..., description="Policy type")
    version: str = Field(..., description="Policy version")
    effective_date: Optional[datetime] = Field(None, description="Effective date")
    last_reviewed_at: Optional[datetime] = Field(None, description="Last reviewed date")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserPolicyListResponse(BaseModel):
    """Simple list response for policy names only"""
    
    id: UUID = Field(..., description="Policy ID")
    title: str = Field(..., description="Policy title")
    policy_type: PolicyType = Field(..., description="Policy type")
    version: str = Field(..., description="Policy version")


class UserPolicyListPaginatedResponse(BaseModel):
    """Response schema for user policy list"""
    
    items: List[UserPolicyListResponse] = Field(..., description="List of policies")
    total: int = Field(..., description="Total number of policies")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class UserPolicyQueryParams(BaseModel):
    """Query parameters for user policy endpoints"""
    
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")
    search: Optional[str] = Field(None, min_length=1, max_length=255, description="Search term")
    policy_type: Optional[PolicyType] = Field(None, description="Filter by policy type")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")
