from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.core.response_handler import (
    HeaderValidationException,
    InvalidDeviceTypeException,
    InvalidAppVersionException
)
from app.models.token import Token, TokenBlacklist
from app.models.user import User

# OAuth2 scheme
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Check if token is blacklisted
    try:
        blacklist_query = select(TokenBlacklist).where(
            TokenBlacklist.token == token,
            TokenBlacklist.expires_at > datetime.now(timezone.utc),
        )
        blacklisted_token = await db.execute(blacklist_query)
    except Exception as db_error:
        # If database connection fails, log and raise proper error
        from app.core.database import logger
        logger.error(f"Database connection error in get_current_user: {str(db_error)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection error. Please try again.",
        )
    if blacklisted_token.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token and get user ID
    try:
        user_id = get_current_user_id(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if token exists in database and is not revoked
    token_query = select(Token).where(
        Token.token == token,
        Token.user_id == user_id,
        Token.is_revoked == False,
        Token.expires_at > datetime.now(timezone.utc),
    )
    token_result = await db.execute(token_query)
    token_obj = token_result.scalar_one_or_none()

    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user_query = select(User).where(User.id == user_id, User.is_deleted == False)
    result = await db.execute(user_query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def verify_refresh_token(
    refresh_token: str, db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Verify refresh token and return user

    Args:
        refresh_token: Refresh token string
        db: Database session

    Returns:
        User: User associated with refresh token

    Raises:
        HTTPException: If refresh token is invalid
    """
    from app.models.token import RefreshToken

    # Check if token is blacklisted
    blacklist_query = select(TokenBlacklist).where(
        TokenBlacklist.token == refresh_token,
        TokenBlacklist.expires_at > datetime.now(timezone.utc),
    )
    blacklisted_token = await db.execute(blacklist_query)
    if blacklisted_token.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    # Get refresh token from database
    token_query = select(RefreshToken).where(
        RefreshToken.token == refresh_token,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.now(timezone.utc),
    )
    result = await db.execute(token_query)
    refresh_token_obj = result.scalar_one_or_none()

    if not refresh_token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # Get user
    user_query = select(User).where(
        User.id == refresh_token_obj.user_id,
        User.is_deleted == False,
        User.is_active == True,
    )
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


# Common dependency alias
CurrentUser = Annotated[User, Depends(get_current_user)]


# ============================================================================
# HEADER VALIDATION DEPENDENCY
# ============================================================================
async def validate_client_headers(request: Request) -> None:
    """Header validation disabled (legacy dependency placeholder)."""
    return
