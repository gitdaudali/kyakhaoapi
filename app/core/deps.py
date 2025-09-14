from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.models.token import TokenBlacklist
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
    blacklist_query = select(TokenBlacklist).where(
        TokenBlacklist.token == token,
        TokenBlacklist.expires_at > datetime.now(timezone.utc),
    )
    blacklisted_token = await db.execute(blacklist_query)
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


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current active user (additional check for active status)

    Args:
        current_user: Current user from get_current_user

    Returns:
        User: Current active user

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current superuser

    Args:
        current_user: Current user from get_current_user

    Returns:
        User: Current superuser

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


async def get_optional_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None

    Args:
        credentials: Optional HTTP Bearer token credentials
        db: Database session

    Returns:
        Optional[User]: Current user if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


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


def require_permissions(required_permissions: list[str]):
    """
    Dependency factory for permission-based access control

    Args:
        required_permissions: List of required permissions

    Returns:
        Dependency function that checks permissions
    """

    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        # For now, only check if user is superuser
        # In the future, implement role-based permissions
        if not current_user.is_superuser:
            # Check if user has any of the required permissions
            # This is a placeholder - implement actual permission checking
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return permission_checker


def require_roles(required_roles: list[str]):
    """
    Dependency factory for role-based access control

    Args:
        required_roles: List of required roles

    Returns:
        Dependency function that checks roles
    """

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        # For now, only check if user is superuser
        # In the future, implement role-based access control
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions",
            )
        return current_user

    return role_checker


# Common dependency aliases
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentSuperUser = Annotated[User, Depends(get_current_superuser)]
OptionalCurrentUser = Annotated[Optional[User], Depends(get_optional_current_user)]
