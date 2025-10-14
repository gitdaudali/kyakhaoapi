"""
Standardized API response schemas for consistent API responses.
"""

from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

# Generic type for data field
T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """Base response model with success, message, and data fields."""
    
    success: bool = Field(..., description="Indicates if the request was successful")
    message: str = Field(..., description="Human-readable message describing the result")
    data: Optional[T] = Field(None, description="Response data payload")


class SuccessResponse(BaseResponse[T]):
    """Success response model."""
    
    success: bool = Field(True, description="Always true for success responses")
    message: str = Field(..., description="Success message")
    data: Optional[T] = Field(None, description="Success data payload")


class ErrorResponse(BaseResponse[None]):
    """Error response model."""
    
    success: bool = Field(False, description="Always false for error responses")
    message: str = Field(..., description="Error message")
    data: Optional[None] = Field(None, description="No data for error responses")
    error_code: Optional[str] = Field(None, description="Optional error code for debugging")


class PaginationInfo(BaseModel):
    """Pagination information model."""
    
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""
    
    items: list[T] = Field(..., description="List of items in current page")
    pagination: PaginationInfo = Field(..., description="Pagination information")


class MessageResponse(BaseModel):
    """Simple message response model."""
    
    success: bool = Field(True, description="Always true for message responses")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Optional data payload")


# Common response types
class AuthResponse(SuccessResponse[dict]):
    """Authentication response model."""
    pass


class TokenResponse(SuccessResponse[dict]):
    """Token response model."""
    pass


class UserResponse(SuccessResponse[dict]):
    """User response model."""
    pass


class ContentResponse(SuccessResponse[dict]):
    """Content response model."""
    pass


class GenreResponse(SuccessResponse[dict]):
    """Genre response model."""
    pass


class StreamingResponse(SuccessResponse[dict]):
    """Streaming response model."""
    pass


class AdminResponse(SuccessResponse[dict]):
    """Admin response model."""
    pass


# List response types
class GenreListResponse(SuccessResponse[PaginatedResponse[dict]]):
    """Genre list response model."""
    pass


class ContentListResponse(SuccessResponse[PaginatedResponse[dict]]):
    """Content list response model."""
    pass


class UserListResponse(SuccessResponse[PaginatedResponse[dict]]):
    """User list response model."""
    pass


class StreamingListResponse(SuccessResponse[PaginatedResponse[dict]]):
    """Streaming channel list response model."""
    pass


# Admin list response types
class GenreWithMoviesListResponse(SuccessResponse[PaginatedResponse[dict]]):
    """Genre with movies list response model."""
    pass


class AdCampaignListResponse(SuccessResponse[PaginatedResponse[dict]]):
    """Ad campaign list response model."""
    pass


class UserAdminListResponse(SuccessResponse[PaginatedResponse[dict]]):
    """User admin list response model."""
    pass


# Specific response models
class ProfileResponse(SuccessResponse[dict]):
    """Profile response model."""
    pass


class SearchHistoryResponse(SuccessResponse[dict]):
    """Search history response model."""
    pass


class ReviewResponse(SuccessResponse[dict]):
    """Review response model."""
    pass


class CastCrewResponse(SuccessResponse[dict]):
    """Cast and crew response model."""
    pass


class PerformanceResponse(SuccessResponse[dict]):
    """Performance analytics response model."""
    pass


class MonetizationResponse(SuccessResponse[dict]):
    """Monetization response model."""
    pass
