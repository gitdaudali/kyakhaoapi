"""
Unified response and exception handling for the application.
Combines response formatting and exception definitions in one file.
"""

from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.core.messages import *


# ============================================================================
# RESPONSE FORMATTING FUNCTIONS
# ============================================================================

def success_response(
    message: str,
    data: Any = None,
    status_code: int = 200
) -> JSONResponse:
    """Create a simple success response."""
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return JSONResponse(
        status_code=status_code,
        content=response
    )


def error_response(
    message: str,
    status_code: int = 400,
    data: Any = None
) -> JSONResponse:
    """Create a simple error response."""
    response = {
        "message": message,
        "status_code": status_code,
        "data": data
    }
    return JSONResponse(
        status_code=status_code,
        content=response
    )


# ============================================================================
# EXCEPTION CLASSES
# ============================================================================

class BaseAPIException(HTTPException):
    """Base API exception class with error codes."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class ValidationException(BaseAPIException):
    """Validation error exception."""
    
    def __init__(
        self,
        detail: str = "Validation failed",
        field_errors: Optional[Dict[str, List[str]]] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            headers=headers,
            error_code="VALIDATION_ERROR"
        )
        self.field_errors = field_errors or {}


class AuthenticationException(BaseAPIException):
    """Authentication error exception."""
    
    def __init__(
        self,
        detail: str = INVALID_CREDENTIALS,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers or {"WWW-Authenticate": "Bearer"},
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationException(BaseAPIException):
    """Authorization error exception."""
    
    def __init__(
        self,
        detail: str = FORBIDDEN,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers=headers,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundException(BaseAPIException):
    """Not found error exception."""
    
    def __init__(
        self,
        detail: str = NOT_FOUND,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers,
            error_code="NOT_FOUND_ERROR"
        )


class ConflictException(BaseAPIException):
    """Conflict error exception."""
    
    def __init__(
        self,
        detail: str = "Resource conflict",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            headers=headers,
            error_code="CONFLICT_ERROR"
        )


class SecurityException(BaseAPIException):
    """Security error exception."""
    
    def __init__(
        self,
        detail: str = "Security error",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers=headers,
            error_code="SECURITY_ERROR"
        )


class DatabaseException(BaseAPIException):
    """Database error exception."""
    
    def __init__(
        self,
        detail: str = "Database operation failed",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers,
            error_code="DATABASE_ERROR"
        )


class RateLimitException(BaseAPIException):
    """Rate limit error exception."""
    
    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        retry_after: int = 60,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers=headers or {"Retry-After": str(retry_after)},
            error_code="RATE_LIMIT_ERROR"
        )


class InternalServerException(BaseAPIException):
    """Internal server error exception."""
    
    def __init__(
        self,
        detail: str = INTERNAL_SERVER_ERROR,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers,
            error_code="INTERNAL_ERROR"
        )


# ============================================================================
# SPECIFIC BUSINESS LOGIC EXCEPTIONS
# ============================================================================

class UserNotFoundException(NotFoundException):
    """User not found exception."""
    
    def __init__(self, detail: str = USER_NOT_FOUND):
        super().__init__(detail=detail)


class EmailExistsException(ConflictException):
    """Email already exists exception."""
    
    def __init__(self, detail: str = EMAIL_EXISTS):
        super().__init__(detail=detail)


class InvalidCredentialsException(AuthenticationException):
    """Invalid credentials exception."""
    
    def __init__(self, detail: str = INVALID_CREDENTIALS):
        super().__init__(detail=detail)


class AccountDeactivatedException(AuthenticationException):
    """Account deactivated exception."""
    
    def __init__(self, detail: str = ACCOUNT_DEACTIVATED):
        super().__init__(detail=detail)


class EmailNotVerifiedException(AuthenticationException):
    """Email not verified exception."""
    
    def __init__(self, detail: str = EMAIL_NOT_VERIFIED):
        super().__init__(detail=detail)


class InvalidTokenException(AuthenticationException):
    """Invalid token exception."""
    
    def __init__(self, detail: str = INVALID_REFRESH_TOKEN):
        super().__init__(detail=detail)


class HeaderValidationException(SecurityException):
    """Header validation exception."""
    
    def __init__(self, detail: str = SECURITY_ERROR_MISSING_HEADERS):
        super().__init__(detail=detail)


class InvalidDeviceTypeException(SecurityException):
    """Invalid device type exception."""
    
    def __init__(self, detail: str = SECURITY_ERROR_INVALID_DEVICE_TYPE):
        super().__init__(detail=detail)


class InvalidAppVersionException(SecurityException):
    """Invalid app version exception."""
    
    def __init__(self, detail: str = SECURITY_ERROR_INVALID_APP_VERSION):
        super().__init__(detail=detail)


class ContentNotFoundException(NotFoundException):
    """Content not found exception."""
    
    def __init__(self, detail: str = CONTENT_NOT_FOUND):
        super().__init__(detail=detail)


class GenreNotFoundException(NotFoundException):
    """Genre not found exception."""
    
    def __init__(self, detail: str = GENRE_NOT_FOUND):
        super().__init__(detail=detail)


class GenreExistsException(ConflictException):
    """Genre already exists exception."""
    
    def __init__(self, detail: str = GENRE_ALREADY_EXISTS):
        super().__init__(detail=detail)


class AdminAccessDeniedException(AuthorizationException):
    """Admin access denied exception."""
    
    def __init__(self, detail: str = "Admin access required"):
        super().__init__(detail=detail)


class PasswordMismatchException(ValidationException):
    """Password mismatch exception."""
    
    def __init__(self, detail: str = PASSWORDS_DO_NOT_MATCH):
        super().__init__(detail=detail)


class InvalidEmailFormatException(ValidationException):
    """Invalid email format exception."""
    
    def __init__(self, detail: str = INVALID_EMAIL_FORMAT):
        super().__init__(detail=detail)


class PasswordStrengthException(ValidationException):
    """Password strength exception."""
    
    def __init__(self, detail: str = INVALID_PASSWORD_STRENGTH):
        super().__init__(detail=detail)


# ============================================================================
# ADDITIONAL API-SPECIFIC EXCEPTIONS
# ============================================================================

class ReviewNotFoundException(NotFoundException):
    """Review not found exception."""
    
    def __init__(self, detail: str = REVIEW_NOT_FOUND):
        super().__init__(detail=detail)


class ReviewExistsException(ConflictException):
    """Review already exists exception."""
    
    def __init__(self, detail: str = REVIEW_ALREADY_EXISTS):
        super().__init__(detail=detail)


class ReviewPermissionDeniedException(AuthorizationException):
    """Review permission denied exception."""
    
    def __init__(self, detail: str = REVIEW_PERMISSION_DENIED):
        super().__init__(detail=detail)


class CastNotFoundException(NotFoundException):
    """Cast not found exception."""
    
    def __init__(self, detail: str = CAST_NOT_FOUND):
        super().__init__(detail=detail)


class CrewNotFoundException(NotFoundException):
    """Crew not found exception."""
    
    def __init__(self, detail: str = CREW_NOT_FOUND):
        super().__init__(detail=detail)


class StreamingChannelNotFoundException(NotFoundException):
    """Streaming channel not found exception."""
    
    def __init__(self, detail: str = STREAMING_CHANNEL_NOT_FOUND):
        super().__init__(detail=detail)


class StreamingChannelExistsException(ConflictException):
    """Streaming channel already exists exception."""
    
    def __init__(self, detail: str = STREAMING_CHANNEL_ALREADY_EXISTS):
        super().__init__(detail=detail)


class InvalidStreamingURLException(ValidationException):
    """Invalid streaming URL exception."""
    
    def __init__(self, detail: str = STREAMING_CHANNEL_INVALID_URL):
        super().__init__(detail=detail)


class FileNotFoundException(NotFoundException):
    """File not found exception."""
    
    def __init__(self, detail: str = FILE_NOT_FOUND):
        super().__init__(detail=detail)


class InvalidFileFormatException(ValidationException):
    """Invalid file format exception."""
    
    def __init__(self, detail: str = FILE_INVALID_FORMAT):
        super().__init__(detail=detail)


class FileTooLargeException(ValidationException):
    """File too large exception."""
    
    def __init__(self, detail: str = FILE_TOO_LARGE):
        super().__init__(detail=detail)


class PersonNotFoundException(NotFoundException):
    """Person not found exception."""
    
    def __init__(self, detail: str = PERSON_NOT_FOUND):
        super().__init__(detail=detail)


class PersonExistsException(ConflictException):
    """Person already exists exception."""
    
    def __init__(self, detail: str = PERSON_ALREADY_EXISTS):
        super().__init__(detail=detail)


class SeasonNotFoundException(NotFoundException):
    """Season not found exception."""
    
    def __init__(self, detail: str = SEASON_NOT_FOUND):
        super().__init__(detail=detail)


class SeasonExistsException(ConflictException):
    """Season already exists exception."""
    
    def __init__(self, detail: str = SEASON_ALREADY_EXISTS):
        super().__init__(detail=detail)


class EpisodeNotFoundException(NotFoundException):
    """Episode not found exception."""
    
    def __init__(self, detail: str = EPISODE_NOT_FOUND):
        super().__init__(detail=detail)


class EpisodeExistsException(ConflictException):
    """Episode already exists exception."""
    
    def __init__(self, detail: str = EPISODE_ALREADY_EXISTS):
        super().__init__(detail=detail)


class InvalidRatingException(ValidationException):
    """Invalid rating exception."""
    
    def __init__(self, detail: str = REVIEW_INVALID_RATING):
        super().__init__(detail=detail)


class UsernameExistsException(ConflictException):
    """Username already exists exception."""
    
    def __init__(self, detail: str = USERNAME_EXISTS):
        super().__init__(detail=detail)


class TokenExpiredException(AuthenticationException):
    """Token expired exception."""
    
    def __init__(self, detail: str = TOKEN_EXPIRED):
        super().__init__(detail=detail)


class TokenRevokedException(AuthenticationException):
    """Token revoked exception."""
    
    def __init__(self, detail: str = TOKEN_REVOKED):
        super().__init__(detail=detail)


# ============================================================================
# UNIFIED RESPONSE FORMAT
# ============================================================================

def create_response(
    success: bool = True,
    message: str = "Success",
    data: Any = None,
    status_code: int = 200
) -> JSONResponse:
    """Create a unified response format for all API endpoints."""
    response = {
        "success": success,
        "message": message,
        "data": data
    }
    
    return JSONResponse(
        status_code=status_code,
        content=response
    )


def success_response(
    message: str = "Success",
    data: Any = None,
    status_code: int = 200
) -> JSONResponse:
    """Create a success response with unified format."""
    return create_response(
        success=True,
        message=message,
        data=data,
        status_code=status_code
    )


def error_response(
    message: str = "Error",
    status_code: int = 400,
    data: Any = None
) -> JSONResponse:
    """Create an error response with unified format."""
    return create_response(
        success=False,
        message=message,
        data=data,
        status_code=status_code
    )


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

def handle_exception(request, exc: Exception) -> JSONResponse:
    """Handle different types of exceptions with appropriate responses."""
    
    # Handle custom API exceptions
    if isinstance(exc, BaseAPIException):
        return error_response(
            message=str(exc.detail),
            status_code=exc.status_code
        )
    
    # Handle FastAPI HTTP exceptions
    if isinstance(exc, HTTPException):
        return error_response(
            message=str(exc.detail),
            status_code=exc.status_code
        )
    
    # Handle unexpected errors
    return error_response(
        message="Internal server error",
        status_code=500
    )
