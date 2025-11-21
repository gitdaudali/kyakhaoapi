from typing import List, Optional
from pydantic import BaseModel, Field, validator


class AllergyBase(BaseModel):
    """Base schema for allergy."""
    id: str = Field(..., description="Allergy ID (UUID)")
    name: str = Field(..., description="Allergy name")
    type: Optional[str] = Field(default="food", description="Allergy type")
    identifier: Optional[str] = Field(None, description="String identifier (e.g., 'wheat', 'peanut')")


class AllergyResponse(AllergyBase):
    """Response schema for allergy."""
    
    class Config:
        from_attributes = True


class AllergyListResponse(BaseModel):
    """Response schema for list of allergies."""
    allergies: List[AllergyResponse] = Field(default_factory=list)


class AllergyCreate(BaseModel):
    """Schema for creating a new allergy (admin only)."""
    id: Optional[str] = Field(None, min_length=1, max_length=50, description="Allergy identifier (optional, e.g., 'wheat', 'peanut')")
    name: str = Field(..., min_length=1, max_length=100, description="Allergy name")
    type: Optional[str] = Field(default="food", max_length=50, description="Allergy type")
    
    @validator("id")
    def validate_id(cls, v):
        """Validate allergy identifier format if provided."""
        if v is None:
            return v
        if not v.islower() or " " in v:
            raise ValueError("Allergy identifier must be lowercase with no spaces")
        return v


class UserAllergyUpdate(BaseModel):
    """Schema for updating user allergies."""
    allergies: List[str] = Field(
        ...,
        description="List of allergy IDs selected by user",
        example=["wheat", "milk", "nuts"]
    )
    
    @validator("allergies")
    def validate_allergies(cls, v):
        """Validate that allergies list is not empty if provided."""
        if not isinstance(v, list):
            raise ValueError("Allergies must be a list")
        return v


class UserAllergyResponse(BaseModel):
    """Response schema for user allergies update."""
    userId: str = Field(..., description="User ID")
    allergies: List[str] = Field(default_factory=list, description="List of allergy IDs")
    updatedAt: str = Field(..., description="Update timestamp in ISO format")
    
    class Config:
        from_attributes = True

