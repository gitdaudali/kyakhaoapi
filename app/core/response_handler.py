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

