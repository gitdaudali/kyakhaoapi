# Authentication-focused schemas

from .auth import (
    AuthResponse,
    LogoutRequest,
    LogoutResponse,
    MessageResponse,
    OTPVerificationRequest,
    PasswordChangeRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenInfo,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from .google_oauth import GoogleOAuthRequest, GoogleOAuthResponse, GoogleUserInfo
from .user import User

__all__ = [
    "AuthResponse",
    "LogoutRequest",
    "LogoutResponse",
    "MessageResponse",
    "OTPVerificationRequest",
    "PasswordChangeRequest",
    "PasswordResetConfirm",
    "PasswordResetRequest",
    "RefreshTokenRequest",
    "TokenInfo",
    "TokenResponse",
    "UserLoginRequest",
    "UserRegisterRequest",
    "GoogleOAuthRequest",
    "GoogleOAuthResponse",
    "GoogleUserInfo",
    "User",
]