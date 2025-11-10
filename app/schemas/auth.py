from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator
from pydantic.types import constr

from .user import User as UserSchema


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: constr(min_length=8, max_length=128) = Field(...)
    password_confirm: constr(min_length=8, max_length=128) = Field(...)

    @validator("password_confirm")
    def passwords_match(cls, value, values):
        if value != values.get("password"):
            raise ValueError("Password confirmation must match password")
        return value

    @validator("password")
    def validate_password_strength(cls, value: str) -> str:
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        return value

    @validator("email")
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=1, max_length=128)
    remember_me: bool = Field(default=False)

    @validator("email")
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int

    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseModel):
    user: UserSchema
    tokens: TokenResponse


class PasswordResetRequest(BaseModel):
    email: EmailStr

    @validator("email")
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    otp_code: constr(min_length=6, max_length=6)
    new_password: constr(min_length=8, max_length=128)
    new_password_confirm: constr(min_length=8, max_length=128)
    logout_all_devices: bool = Field(default=True)

    @validator("email")
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @validator("new_password_confirm")
    def passwords_match(cls, value: str, values):
        if value != values.get("new_password"):
            raise ValueError("Passwords do not match")
        return value


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: constr(min_length=8, max_length=128)
    new_password_confirm: constr(min_length=8, max_length=128)

    @validator("new_password_confirm")
    def passwords_match(cls, value: str, values):
        if value != values.get("new_password"):
            raise ValueError("Passwords do not match")
        return value

    @validator("new_password")
    def validate_password_strength(cls, value: str) -> str:
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        return value


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None
    logout_all_devices: bool = Field(default=False)


class LogoutResponse(BaseModel):
    message: str
    logged_out_devices: int

    class Config:
        from_attributes = True


class TokenInfo(BaseModel):
    token_type: str
    expires_at: datetime
    is_valid: bool
    user_id: Optional[str] = None
    scope: Optional[str] = None


class OTPVerificationRequest(BaseModel):
    email: EmailStr
    otp_code: constr(min_length=6, max_length=6)

    @validator("email")
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @validator("otp_code")
    def validate_otp(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("OTP code must contain only digits")
        return value


class MessageResponse(BaseModel):
    message: str
