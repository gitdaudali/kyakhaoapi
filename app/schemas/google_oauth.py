from typing import Optional

from pydantic import BaseModel, Field, validator


class GoogleOAuthRequest(BaseModel):
    """Request schema for Google OAuth authentication"""

    access_token: str = Field(..., min_length=1, description="Google access token")

    @validator("access_token")
    def validate_access_token(cls, v):
        """Validate access token is not empty"""
        if not v or not v.strip():
            raise ValueError("Access token cannot be empty")
        return v.strip()


class GoogleUserInfo(BaseModel):
    """Google user information from OAuth"""

    id: str = Field(..., description="Google user ID")
    email: str = Field(..., description="User email")
    verified_email: bool = Field(..., description="Email verification status")
    name: Optional[str] = Field(None, description="User full name")
    given_name: Optional[str] = Field(None, description="User first name")
    family_name: Optional[str] = Field(None, description="User last name")
    picture: Optional[str] = Field(None, description="User profile picture URL")
    locale: Optional[str] = Field(None, description="User locale")


class GoogleOAuthResponse(BaseModel):
    """Response schema for Google OAuth authentication"""

    user: dict = Field(..., description="User information")
    tokens: dict = Field(..., description="Access and refresh tokens")
    is_new_user: bool = Field(
        ..., description="Whether this is a new user registration"
    )
    message: str = Field(..., description="Response message")
