"""
Unified response and exception handling for the application.
Combines response formatting and exception definitions in one file.
"""

from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.core.messages import *
from app.utils.serialization_utils import safe_json_response


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
        "data": safe_json_response(data) if data is not None else None
    }
    return JSONResponse(
        status_code=status_code,
        content=response
    )


def error_response(
    message: str,
    status_code: int = 400,
    data: Any = None,
    error_code: str = None
) -> JSONResponse:
    """Create a simple error response."""
    response = {
        "success": False,
        "message": message,
        "data": safe_json_response(data) if data is not None else None
    }
    if error_code:
        response["error_code"] = error_code
    
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
# MODULE-SPECIFIC EXCEPTIONS
# ============================================================================

# Favorites Exceptions
class FavoritesException(BaseAPIException):
    """Base exception for favorites operations."""
    pass

class FavoritesNotFoundError(FavoritesException):
    """Exception when favorites are not found."""
    def __init__(self, detail: str = FAVORITES_NOT_FOUND):
        super().__init__(detail=detail, status_code=404, error_code="FAVORITES_NOT_FOUND")

class FavoritesAlreadyExistsError(FavoritesException):
    """Exception when content is already in favorites."""
    def __init__(self, detail: str = FAVORITES_ALREADY_EXISTS):
        super().__init__(detail=detail, status_code=409, error_code="FAVORITES_ALREADY_EXISTS")

# Statistics Exceptions
class StatisticsException(BaseAPIException):
    """Base exception for statistics operations."""
    pass

class StatisticsNotFoundError(StatisticsException):
    """Exception when statistics are not found."""
    def __init__(self, detail: str = STATS_NOT_FOUND):
        super().__init__(detail=detail, status_code=404, error_code="STATS_NOT_FOUND")

class StatisticsCalculationError(StatisticsException):
    """Exception when statistics calculation fails."""
    def __init__(self, detail: str = STATS_CALCULATION_ERROR):
        super().__init__(detail=detail, status_code=500, error_code="STATS_CALCULATION_ERROR")

# Recommendations Exceptions
class RecommendationsException(BaseAPIException):
    """Base exception for recommendations operations."""
    pass

class RecommendationsNotFoundError(RecommendationsException):
    """Exception when recommendations are not found."""
    def __init__(self, detail: str = RECOMMENDATIONS_NOT_FOUND):
        super().__init__(detail=detail, status_code=404, error_code="RECOMMENDATIONS_NOT_FOUND")

class RecommendationsGenerationError(RecommendationsException):
    """Exception when recommendation generation fails."""
    def __init__(self, detail: str = RECOMMENDATIONS_GENERATION_ERROR):
        super().__init__(detail=detail, status_code=500, error_code="RECOMMENDATIONS_GENERATION_ERROR")

class RecommendationsAlgorithmUnavailableError(RecommendationsException):
    """Exception when recommendation algorithm is unavailable."""
    def __init__(self, detail: str = RECOMMENDATIONS_ALGORITHM_UNAVAILABLE):
        super().__init__(detail=detail, status_code=503, error_code="RECOMMENDATIONS_ALGORITHM_UNAVAILABLE")

# ============================================================================
# ADMIN-SPECIFIC EXCEPTIONS
# ============================================================================

# Admin Base Exceptions
class AdminException(BaseAPIException):
    """Base exception for admin operations."""
    pass

class AdminAccessDeniedError(AdminException):
    """Exception when admin access is denied."""
    def __init__(self, detail: str = ADMIN_ACCESS_DENIED):
        super().__init__(detail=detail, status_code=403, error_code="ADMIN_ACCESS_DENIED")

class AdminInsufficientPermissionsError(AdminException):
    """Exception when admin has insufficient permissions."""
    def __init__(self, detail: str = ADMIN_INSUFFICIENT_PERMISSIONS):
        super().__init__(detail=detail, status_code=403, error_code="ADMIN_INSUFFICIENT_PERMISSIONS")

# Content Admin Exceptions
class ContentAdminException(AdminException):
    """Base exception for content admin operations."""
    pass

class ContentAdminNotFoundError(ContentAdminException):
    """Exception when content is not found in admin operations."""
    def __init__(self, detail: str = CONTENT_NOT_FOUND):
        super().__init__(detail=detail, status_code=404, error_code="CONTENT_ADMIN_NOT_FOUND")

class ContentAdminAlreadyExistsError(ContentAdminException):
    """Exception when content already exists in admin operations."""
    def __init__(self, detail: str = CONTENT_ALREADY_EXISTS):
        super().__init__(detail=detail, status_code=409, error_code="CONTENT_ADMIN_ALREADY_EXISTS")

# Genre Admin Exceptions
class GenreAdminException(AdminException):
    """Base exception for genre admin operations."""
    pass

class GenreAdminNotFoundError(GenreAdminException):
    """Exception when genre is not found in admin operations."""
    def __init__(self, detail: str = GENRE_NOT_FOUND):
        super().__init__(detail=detail, status_code=404, error_code="GENRE_ADMIN_NOT_FOUND")

class GenreAdminAlreadyExistsError(GenreAdminException):
    """Exception when genre already exists in admin operations."""
    def __init__(self, detail: str = GENRE_ALREADY_EXISTS):
        super().__init__(detail=detail, status_code=409, error_code="GENRE_ADMIN_ALREADY_EXISTS")

# User Admin Exceptions
class UserAdminException(AdminException):
    """Base exception for user admin operations."""
    pass

class UserAdminNotFoundError(UserAdminException):
    """Exception when user is not found in admin operations."""
    def __init__(self, detail: str = USER_NOT_FOUND):
        super().__init__(detail=detail, status_code=404, error_code="USER_ADMIN_NOT_FOUND")

class UserAdminAlreadyExistsError(UserAdminException):
    """Exception when user already exists in admin operations."""
    def __init__(self, detail: str = USER_ALREADY_EXISTS):
        super().__init__(detail=detail, status_code=409, error_code="USER_ADMIN_ALREADY_EXISTS")

# People Admin Exceptions
class PersonAdminException(AdminException):
    """Base exception for person admin operations."""
    pass

class PersonAdminNotFoundError(PersonAdminException):
    """Exception when person is not found in admin operations."""
    def __init__(self, detail: str = PERSON_NOT_FOUND):
        super().__init__(detail=detail, status_code=404, error_code="PERSON_ADMIN_NOT_FOUND")

class PersonAdminAlreadyExistsError(PersonAdminException):
    """Exception when person already exists in admin operations."""
    def __init__(self, detail: str = PERSON_ALREADY_EXISTS):
        super().__init__(detail=detail, status_code=409, error_code="PERSON_ADMIN_ALREADY_EXISTS")

# Streaming Channel Admin Exceptions
class StreamingChannelAdminException(AdminException):
    """Base exception for streaming channel admin operations."""
    pass

class StreamingChannelAdminNotFoundError(StreamingChannelAdminException):
    """Exception when streaming channel is not found in admin operations."""
    def __init__(self, detail: str = STREAMING_CHANNEL_NOT_FOUND):
        super().__init__(detail=detail, status_code=404, error_code="STREAMING_CHANNEL_ADMIN_NOT_FOUND")

class StreamingChannelAdminAlreadyExistsError(StreamingChannelAdminException):
    """Exception when streaming channel already exists in admin operations."""
    def __init__(self, detail: str = STREAMING_CHANNEL_ALREADY_EXISTS):
        super().__init__(detail=detail, status_code=409, error_code="STREAMING_CHANNEL_ADMIN_ALREADY_EXISTS")

# Policy Admin Exceptions
class PolicyAdminException(AdminException):
    """Base exception for policy admin operations."""
    pass

class PolicyAdminNotFoundError(PolicyAdminException):
    """Exception when policy is not found in admin operations."""
    def __init__(self, detail: str = POLICY_NOT_FOUND):
        super().__init__(detail=detail, status_code=404, error_code="POLICY_ADMIN_NOT_FOUND")

class PolicyAdminAlreadyExistsError(PolicyAdminException):
    """Exception when policy already exists in admin operations."""
    def __init__(self, detail: str = POLICY_ALREADY_EXISTS):
        super().__init__(detail=detail, status_code=409, error_code="POLICY_ADMIN_ALREADY_EXISTS")


# ============================================================================
# UNIFIED RESPONSE FORMAT
# ============================================================================

def create_response(
    success: bool = True,
    message: str = "Success",
    data: Any = None,
    status_code: int = 200,
    error_code: str = None
) -> JSONResponse:
    """Create a unified response format for all API endpoints."""
    response = {
        "success": success,
        "message": message,
        "data": safe_json_response(data) if data is not None else None
    }
    
    if error_code:
        response["error_code"] = error_code
    
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
    data: Any = None,
    error_code: str = None
) -> JSONResponse:
    """Create an error response with unified format."""
    return create_response(
        success=False,
        message=message,
        data=data,
        status_code=status_code,
        error_code=error_code
    )


# ============================================================================
# RESPONSE UTILITIES
# ============================================================================

def create_success_response(
    message: str = "Success",
    data: Any = None,
    status_code: int = 200
) -> JSONResponse:
    """Create a standardized success response."""
    return create_response(
        success=True,
        message=message,
        data=data,
        status_code=status_code
    )


def create_error_response(
    message: str = "Error",
    status_code: int = 400,
    data: Any = None,
    error_code: str = None
) -> JSONResponse:
    """Create a standardized error response."""
    return create_response(
        success=False,
        message=message,
        data=data,
        status_code=status_code,
        error_code=error_code
    )


# ============================================================================
# MODULE-SPECIFIC RESPONSE FUNCTIONS
# ============================================================================

# Favorites Response Functions
def favorites_retrieved_response(data: Any = None) -> JSONResponse:
    """Response for successfully retrieved favorites."""
    return success_response(
        message=FAVORITES_RETRIEVED_SUCCESS,
        data=data,
        status_code=200
    )

def favorites_added_response(data: Any = None) -> JSONResponse:
    """Response for successfully added to favorites."""
    return success_response(
        message=FAVORITES_ADDED_SUCCESS,
        data=data,
        status_code=201
    )

def favorites_removed_response(data: Any = None) -> JSONResponse:
    """Response for successfully removed from favorites."""
    return success_response(
        message=FAVORITES_REMOVED_SUCCESS,
        data=data,
        status_code=200
    )

def favorites_already_exists_response(data: Any = None) -> JSONResponse:
    """Response for content already in favorites."""
    return success_response(
        message=FAVORITES_ALREADY_EXISTS,
        data=data,
        status_code=200
    )

# Statistics Response Functions
def stats_hours_watched_response(data: Any = None) -> JSONResponse:
    """Response for hours watched statistics."""
    return success_response(
        message=STATS_HOURS_WATCHED_SUCCESS,
        data=data,
        status_code=200
    )

def stats_movies_completed_response(data: Any = None) -> JSONResponse:
    """Response for movies completed statistics."""
    return success_response(
        message=STATS_MOVIES_COMPLETED_SUCCESS,
        data=data,
        status_code=200
    )

def stats_tv_episodes_response(data: Any = None) -> JSONResponse:
    """Response for TV episodes watched statistics."""
    return success_response(
        message=STATS_TV_EPISODES_SUCCESS,
        data=data,
        status_code=200
    )

def stats_favorites_count_response(data: Any = None) -> JSONResponse:
    """Response for favorites count statistics."""
    return success_response(
        message=STATS_FAVORITES_COUNT_SUCCESS,
        data=data,
        status_code=200
    )

# Recommendations Response Functions
def recommendations_generated_response(data: Any = None) -> JSONResponse:
    """Response for successfully generated recommendations."""
    return success_response(
        message=RECOMMENDATIONS_GENERATED_SUCCESS,
        data=data,
        status_code=200
    )

def recommendations_personalized_response(data: Any = None) -> JSONResponse:
    """Response for personalized recommendations."""
    return success_response(
        message=RECOMMENDATIONS_PERSONALIZED_SUCCESS,
        data=data,
        status_code=200
    )

def recommendations_trending_response(data: Any = None) -> JSONResponse:
    """Response for trending recommendations."""
    return success_response(
        message=RECOMMENDATIONS_TRENDING_SUCCESS,
        data=data,
        status_code=200
    )

def recommendations_similar_response(data: Any = None) -> JSONResponse:
    """Response for similar content recommendations."""
    return success_response(
        message=RECOMMENDATIONS_SIMILAR_SUCCESS,
        data=data,
        status_code=200
    )

def recommendations_genre_response(data: Any = None) -> JSONResponse:
    """Response for genre-based recommendations."""
    return success_response(
        message=RECOMMENDATIONS_GENRE_SUCCESS,
        data=data,
        status_code=200
    )

def recommendations_new_releases_response(data: Any = None) -> JSONResponse:
    """Response for new release recommendations."""
    return success_response(
        message=RECOMMENDATIONS_NEW_RELEASES_SUCCESS,
        data=data,
        status_code=200
    )

def recommendations_not_found_response(data: Any = None) -> JSONResponse:
    """Response for no recommendations found."""
    return error_response(
        message=RECOMMENDATIONS_NOT_FOUND,
        data=data,
        status_code=404,
        error_code="RECOMMENDATIONS_NOT_FOUND"
    )

def recommendations_generation_error_response(data: Any = None) -> JSONResponse:
    """Response for recommendation generation error."""
    return error_response(
        message=RECOMMENDATIONS_GENERATION_ERROR,
        data=data,
        status_code=500,
        error_code="RECOMMENDATIONS_GENERATION_ERROR"
    )

# ============================================================================
# ADMIN-SPECIFIC RESPONSE FUNCTIONS
# ============================================================================

# General Admin Response Functions
def admin_operation_success_response(data: Any = None) -> JSONResponse:
    """Response for successful admin operations."""
    return success_response(
        message=ADMIN_OPERATION_SUCCESS,
        data=data,
        status_code=200
    )

def admin_bulk_operation_success_response(data: Any = None) -> JSONResponse:
    """Response for successful admin bulk operations."""
    return success_response(
        message=ADMIN_BULK_OPERATION_SUCCESS,
        data=data,
        status_code=200
    )

def admin_access_denied_response(data: Any = None) -> JSONResponse:
    """Response for admin access denied."""
    return error_response(
        message=ADMIN_ACCESS_DENIED,
        data=data,
        status_code=403,
        error_code="ADMIN_ACCESS_DENIED"
    )

def admin_insufficient_permissions_response(data: Any = None) -> JSONResponse:
    """Response for insufficient admin permissions."""
    return error_response(
        message=ADMIN_INSUFFICIENT_PERMISSIONS,
        data=data,
        status_code=403,
        error_code="ADMIN_INSUFFICIENT_PERMISSIONS"
    )

# Content Admin Response Functions
def content_admin_created_response(data: Any = None) -> JSONResponse:
    """Response for successfully created content."""
    return success_response(
        message=CONTENT_CREATED,
        data=data,
        status_code=201
    )

def content_admin_updated_response(data: Any = None) -> JSONResponse:
    """Response for successfully updated content."""
    return success_response(
        message=CONTENT_UPDATED,
        data=data,
        status_code=200
    )

def content_admin_deleted_response(data: Any = None) -> JSONResponse:
    """Response for successfully deleted content."""
    return success_response(
        message=CONTENT_DELETED,
        data=data,
        status_code=200
    )

def content_admin_published_response(data: Any = None) -> JSONResponse:
    """Response for successfully published content."""
    return success_response(
        message=CONTENT_PUBLISHED,
        data=data,
        status_code=200
    )

def content_admin_featured_response(data: Any = None) -> JSONResponse:
    """Response for successfully featured content."""
    return success_response(
        message=CONTENT_FEATURED,
        data=data,
        status_code=200
    )

def content_admin_trending_response(data: Any = None) -> JSONResponse:
    """Response for successfully updated trending content."""
    return success_response(
        message=CONTENT_TRENDING,
        data=data,
        status_code=200
    )

# Genre Admin Response Functions
def genre_admin_created_response(data: Any = None) -> JSONResponse:
    """Response for successfully created genre."""
    return success_response(
        message=GENRE_CREATED,
        data=data,
        status_code=201
    )

def genre_admin_updated_response(data: Any = None) -> JSONResponse:
    """Response for successfully updated genre."""
    return success_response(
        message=GENRE_UPDATED,
        data=data,
        status_code=200
    )

def genre_admin_deleted_response(data: Any = None) -> JSONResponse:
    """Response for successfully deleted genre."""
    return success_response(
        message=GENRE_DELETED,
        data=data,
        status_code=200
    )

def genre_admin_featured_response(data: Any = None) -> JSONResponse:
    """Response for successfully featured genre."""
    return success_response(
        message=GENRE_FEATURED,
        data=data,
        status_code=200
    )

# User Admin Response Functions
def user_admin_created_response(data: Any = None) -> JSONResponse:
    """Response for successfully created user."""
    return success_response(
        message=USER_CREATED,
        data=data,
        status_code=201
    )

def user_admin_updated_response(data: Any = None) -> JSONResponse:
    """Response for successfully updated user."""
    return success_response(
        message=USER_UPDATED,
        data=data,
        status_code=200
    )

def user_admin_deleted_response(data: Any = None) -> JSONResponse:
    """Response for successfully deleted user."""
    return success_response(
        message=USER_DELETED,
        data=data,
        status_code=200
    )

def user_admin_suspended_response(data: Any = None) -> JSONResponse:
    """Response for successfully suspended user."""
    return success_response(
        message=USER_SUSPENDED,
        data=data,
        status_code=200
    )

def user_admin_activated_response(data: Any = None) -> JSONResponse:
    """Response for successfully activated user."""
    return success_response(
        message=USER_ACTIVATED,
        data=data,
        status_code=200
    )

def user_admin_banned_response(data: Any = None) -> JSONResponse:
    """Response for successfully banned user."""
    return success_response(
        message=USER_BANNED,
        data=data,
        status_code=200
    )

def user_admin_role_updated_response(data: Any = None) -> JSONResponse:
    """Response for successfully updated user role."""
    return success_response(
        message=USER_ROLE_UPDATED,
        data=data,
        status_code=200
    )

# People Admin Response Functions
def person_admin_created_response(data: Any = None) -> JSONResponse:
    """Response for successfully created person."""
    return success_response(
        message=PERSON_CREATED,
        data=data,
        status_code=201
    )

def person_admin_updated_response(data: Any = None) -> JSONResponse:
    """Response for successfully updated person."""
    return success_response(
        message=PERSON_UPDATED,
        data=data,
        status_code=200
    )

def person_admin_deleted_response(data: Any = None) -> JSONResponse:
    """Response for successfully deleted person."""
    return success_response(
        message=PERSON_DELETED,
        data=data,
        status_code=200
    )

def person_admin_featured_response(data: Any = None) -> JSONResponse:
    """Response for successfully featured person."""
    return success_response(
        message=PERSON_FEATURED,
        data=data,
        status_code=200
    )

def person_admin_verified_response(data: Any = None) -> JSONResponse:
    """Response for successfully verified person."""
    return success_response(
        message=PERSON_VERIFIED,
        data=data,
        status_code=200
    )

# Streaming Channel Admin Response Functions
def streaming_channel_admin_created_response(data: Any = None) -> JSONResponse:
    """Response for successfully created streaming channel."""
    return success_response(
        message=STREAMING_CHANNEL_CREATED,
        data=data,
        status_code=201
    )

def streaming_channel_admin_updated_response(data: Any = None) -> JSONResponse:
    """Response for successfully updated streaming channel."""
    return success_response(
        message=STREAMING_CHANNEL_UPDATED,
        data=data,
        status_code=200
    )

def streaming_channel_admin_deleted_response(data: Any = None) -> JSONResponse:
    """Response for successfully deleted streaming channel."""
    return success_response(
        message=STREAMING_CHANNEL_DELETED,
        data=data,
        status_code=200
    )

def streaming_channel_admin_test_success_response(data: Any = None) -> JSONResponse:
    """Response for successful streaming channel test."""
    return success_response(
        message=STREAMING_CHANNEL_TEST_SUCCESS,
        data=data,
        status_code=200
    )

# Policy Admin Response Functions
def policy_admin_created_response(data: Any = None) -> JSONResponse:
    """Response for successfully created policy."""
    return success_response(
        message=POLICY_CREATED,
        data=data,
        status_code=201
    )

def policy_admin_updated_response(data: Any = None) -> JSONResponse:
    """Response for successfully updated policy."""
    return success_response(
        message=POLICY_UPDATED,
        data=data,
        status_code=200
    )

def policy_admin_deleted_response(data: Any = None) -> JSONResponse:
    """Response for successfully deleted policy."""
    return success_response(
        message=POLICY_DELETED,
        data=data,
        status_code=200
    )

def policy_admin_acceptance_required_response(data: Any = None) -> JSONResponse:
    """Response for policy acceptance required."""
    return error_response(
        message=POLICY_ACCEPTANCE_REQUIRED,
        data=data,
        status_code=400,
        error_code="POLICY_ACCEPTANCE_REQUIRED"
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
            status_code=exc.status_code,
            error_code=getattr(exc, 'error_code', None)
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
        status_code=500,
        error_code="INTERNAL_ERROR"
    )
