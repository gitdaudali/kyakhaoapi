from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.policy import PolicyType


class UserPolicyResponse(BaseModel):
    """User response schema for policy details"""
    
    id: UUID = Field(..., description="Policy ID")
    title: str = Field(..., description="Policy title")
    description: str = Field(..., description="Policy description")
    content: str = Field(..., description="Policy content")
    status: str = Field(..., description="Policy status")
    policy_type: str = Field(..., description="Policy type")
    version: str = Field(..., description="Policy version")
    effective_date: Optional[datetime] = Field(None, description="Effective date")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserPolicyItem(BaseModel):
    """Single policy item - only 3 fields"""
    
    id: UUID = Field(..., description="Policy ID")
    title: str = Field(..., description="Policy title")
    description: str = Field(..., description="Policy description")
    status: str = Field(..., description="Policy status")


class UserPolicyListResponse(BaseModel):
    """Simple response - just list of all policies"""
    
    policies: List[UserPolicyItem] = Field(..., description="List of all policies")


# No query parameters needed - just get all policies
