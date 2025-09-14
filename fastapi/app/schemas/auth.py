from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator
from pydantic.types import constr

from .user import User as UserSchema


class UserRegisterRequest(BaseModel):
    """User registration request schema"""

    email: EmailStr = Field(..., description="User email address")
    # username: constr(min_length=3, max_length=50) = Field(
    #     ..., description="Username (3-50 characters)", pattern=r"^[a-zA-Z0-9_-]+$"
    # )
    password: constr(min_length=8, max_length=128) = Field(
        ..., description="Password (8-128 characters)"
    )
    password_confirm: constr(min_length=8, max_length=128) = Field(
        ..., description="Password confirmation"
    )

    @validator("password_confirm")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

    @validator("password")
    def validate_password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "Securepassword123",
                "password_confirm": "Securepassword123",
            }
        }


class UserLoginRequest(BaseModel):
    """User login request schema"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(
        default=False, description="Remember user for longer session"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "remember_me": False,
            }
        }


class TokenResponse(BaseModel):
    """Token response schema"""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    refresh_expires_in: int = Field(
        ..., description="Refresh token expiration time in seconds"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "refresh_expires_in": 86400,
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""

    refresh_token: str = Field(..., description="Valid refresh token")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {"refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
        }


class AuthResponse(BaseModel):
    """Authentication response schema"""

    user: UserSchema = Field(..., description="User information")
    tokens: TokenResponse = Field(..., description="Authentication tokens")

    class Config:
        from_attributes = True


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""

    email: EmailStr = Field(..., description="User email address")

    class Config:
        from_attributes = True
        json_schema_extra = {"example": {"email": "user@example.com"}}


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""

    token: str = Field(..., description="Password reset token")
    password: constr(min_length=8, max_length=128) = Field(
        ..., description="New password (8-128 characters)"
    )
    password_confirm: constr(min_length=8, max_length=128) = Field(
        ..., description="Password confirmation"
    )

    @validator("password_confirm")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

    @validator("password")
    def validate_password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "token": "reset_token_here",
                "password": "newpassword123",
                "password_confirm": "newpassword123",
            }
        }


class PasswordChangeRequest(BaseModel):
    """Password change request schema"""

    current_password: str = Field(..., description="Current password")
    new_password: constr(min_length=8, max_length=128) = Field(
        ..., description="New password (8-128 characters)"
    )
    new_password_confirm: constr(min_length=8, max_length=128) = Field(
        ..., description="New password confirmation"
    )

    @validator("new_password_confirm")
    def passwords_match(cls, v, values, **kwargs):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v

    @validator("new_password")
    def validate_password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword123",
                "new_password_confirm": "newpassword123",
            }
        }


class LogoutRequest(BaseModel):
    """Logout request schema"""

    refresh_token: Optional[str] = Field(None, description="Refresh token to revoke")
    logout_all_devices: bool = Field(
        default=False, description="Logout from all devices"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "logout_all_devices": False,
            }
        }


class LogoutResponse(BaseModel):
    """Logout response schema"""

    message: str = Field(..., description="Logout message")
    logged_out_devices: int = Field(..., description="Number of devices logged out")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {"message": "Successfully logged out", "logged_out_devices": 1}
        }


class TokenInfo(BaseModel):
    """Token information schema"""

    token_type: str = Field(..., description="Token type")
    expires_at: datetime = Field(..., description="Token expiration time")
    is_valid: bool = Field(..., description="Token validity status")
    user_id: Optional[str] = Field(None, description="User ID associated with token")
    scope: Optional[str] = Field(None, description="Token scope")

    class Config:
        from_attributes = True


class DeviceInfo(BaseModel):
    """Device information schema"""

    device_id: Optional[str] = Field(None, description="Device identifier")
    device_name: Optional[str] = Field(None, description="Device name")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    last_used: Optional[datetime] = Field(None, description="Last used timestamp")

    class Config:
        from_attributes = True


# Password Reset Schemas
class PasswordResetRequest(BaseModel):
    """Request schema for password reset"""

    email: str = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Request schema for password reset confirmation"""

    reset_token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    new_password_confirm: str = Field(..., description="Confirm new password")


# Email Verification Schemas
class EmailVerificationRequest(BaseModel):
    """Request schema for email verification"""

    verification_token: str = Field(..., description="Email verification token")


# Response Schemas
class StandardResponse(BaseModel):
    """Standard API response schema"""

    code: int = Field(200, description="Response code")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")
