from typing import List, Optional
from pydantic import BaseModel, Field, validator
import uuid


class SpiceLevelPreference(BaseModel):
    """Schema for spice level preference."""
    spice_level: Optional[str] = Field(
        None,
        description="Preferred spice level: Mild, Spicy, Extra Spicy"
    )
    
    @validator("spice_level")
    def validate_spice_level(cls, v):
        """Validate spice level if provided."""
        if v is None:
            return v
        valid_levels = ["Mild", "Spicy", "Extra Spicy"]
        if v not in valid_levels:
            raise ValueError(f"Spice level must be one of: {', '.join(valid_levels)}")
        return v


class PersonalizationUpdate(BaseModel):
    """Schema for updating user personalization preferences."""
    spice_level: Optional[str] = Field(
        None,
        description="Preferred spice level: Mild, Spicy, Extra Spicy"
    )
    favorite_cuisine_ids: Optional[List[uuid.UUID]] = Field(
        None,
        description="List of favorite cuisine IDs"
    )
    preferred_restaurant_ids: Optional[List[uuid.UUID]] = Field(
        None,
        description="List of preferred restaurant IDs"
    )
    
    @validator("spice_level")
    def validate_spice_level(cls, v):
        """Validate spice level if provided."""
        if v is None:
            return v
        valid_levels = ["Mild", "Spicy", "Extra Spicy"]
        if v not in valid_levels:
            raise ValueError(f"Spice level must be one of: {', '.join(valid_levels)}")
        return v


class PersonalizationResponse(BaseModel):
    """Response schema for user personalization."""
    userId: str = Field(..., description="User ID")
    spice_level: Optional[str] = Field(None, description="Preferred spice level")
    favorite_cuisines: List[dict] = Field(default_factory=list, description="List of favorite cuisines")
    preferred_restaurants: List[dict] = Field(default_factory=list, description="List of preferred restaurants")
    updatedAt: str = Field(..., description="Update timestamp in ISO format")
    
    class Config:
        from_attributes = True

