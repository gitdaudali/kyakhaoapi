"""Lightweight response and exception helpers for the authentication service."""

import logging
from typing import Any, Optional

from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.core.messages import (
    ACCOUNT_DEACTIVATED,
    EMAIL_EXISTS,
    EMAIL_NOT_VERIFIED,
    INVALID_CREDENTIALS,
    SECURITY_ERROR_INVALID_APP_VERSION,
    SECURITY_ERROR_INVALID_DEVICE_TYPE,
    SECURITY_ERROR_MISSING_HEADERS,
    USER_NOT_FOUND,
)

logger = logging.getLogger(__name__)


class BaseAPIException(HTTPException):
    """Base class for custom API exceptions with structured payloads."""

    def __init__(
        self,
        *,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None,
        data: Any = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.data = data


def success_response(
    message: str, data: Any = None, status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """Return a standard success envelope."""
    payload = {
        "success": True,
        "message": message,
        "data": jsonable_encoder(data) if data is not None else None,
    }
    return JSONResponse(status_code=status_code, content=payload)


def error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    data: Any = None,
    error_code: Optional[str] = None,
) -> JSONResponse:
    """Return a standard error envelope."""
    payload = {
        "success": False,
        "message": message,
        "data": jsonable_encoder(data) if data is not None else None,
    }
    if error_code:
        payload["error_code"] = error_code
    return JSONResponse(status_code=status_code, content=payload)


def handle_exception(request: Request, exc: Exception) -> JSONResponse:
    """Normalize exceptions into a consistent API error response."""
    if isinstance(exc, BaseAPIException):
        return error_response(
            message=str(exc.detail),
            status_code=exc.status_code,
            data=exc.data,
            error_code=exc.error_code,
        )

    if isinstance(exc, HTTPException):
        return error_response(
            message=str(exc.detail),
            status_code=exc.status_code,
            data=getattr(exc, "data", None),
            error_code=getattr(exc, "error_code", None),
        )

    logger.exception("Unhandled exception while processing request %s", request.url)
    return error_response(
        message="Internal server error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class EmailExistsException(BaseAPIException):
    """Raised when attempting to register with an existing email address."""

    def __init__(self, detail: str = EMAIL_EXISTS) -> None:
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class InvalidCredentialsException(BaseAPIException):
    """Raised when login credentials are invalid."""

    def __init__(self, detail: str = INVALID_CREDENTIALS) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="invalid_credentials",
        )


class AccountDeactivatedException(BaseAPIException):
    """Raised when a user attempts to authenticate with a deactivated account."""

    def __init__(self, detail: str = ACCOUNT_DEACTIVATED) -> None:
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class EmailNotVerifiedException(BaseAPIException):
    """Raised when a user has not yet verified their email address."""

    def __init__(self, detail: str = EMAIL_NOT_VERIFIED) -> None:
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class InvalidTokenException(BaseAPIException):
    """Raised when a supplied token is invalid or expired."""

    def __init__(self, detail: str = INVALID_CREDENTIALS) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="invalid_token",
        )


class UserNotFoundException(BaseAPIException):
    """Raised when a user cannot be located."""

    def __init__(self, detail: str = USER_NOT_FOUND) -> None:
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class HeaderValidationException(BaseAPIException):
    """Raised when required client headers are missing."""

    def __init__(self, detail: str = SECURITY_ERROR_MISSING_HEADERS) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="missing_headers",
        )


class InvalidDeviceTypeException(BaseAPIException):
    """Raised when an unsupported device type header is provided."""

    def __init__(self, detail: str = SECURITY_ERROR_INVALID_DEVICE_TYPE) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="invalid_device_type",
        )


class InvalidAppVersionException(BaseAPIException):
    """Raised when the provided app version header is invalid."""

    def __init__(self, detail: str = SECURITY_ERROR_INVALID_APP_VERSION) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="invalid_app_version",
        )

