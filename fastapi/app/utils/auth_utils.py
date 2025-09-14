"""
Authentication utility functions for user management and validation.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.messages import (
    EMAIL_EXISTS,
    PASSWORDS_DO_NOT_MATCH,
    USER_NOT_FOUND,
    USERNAME_EXISTS,
)
from app.models.user import User as UserModel
from fastapi import HTTPException, status


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[UserModel]:
    """
    Get user by email address.

    Args:
        session: Database session
        email: User email address

    Returns:
        User object if found, None otherwise
    """
    result = await session.execute(
        select(UserModel).where(UserModel.email == email, UserModel.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def get_user_by_username(
    session: AsyncSession, username: str
) -> Optional[UserModel]:
    """
    Get user by username.

    Args:
        session: Database session
        username: Username

    Returns:
        User object if found, None otherwise
    """
    result = await session.execute(
        select(UserModel).where(
            UserModel.username == username, UserModel.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: str) -> Optional[UserModel]:
    """
    Get user by ID.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        User object if found, None otherwise
    """
    result = await session.execute(
        select(UserModel).where(UserModel.id == user_id, UserModel.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def get_user_by_id_or_404(session: AsyncSession, user_id: str) -> UserModel:
    """
    Get user by ID or raise 404 error if not found.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        User object if found

    Raises:
        HTTPException: If user not found
    """
    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )
    return user


def validate_password_match(password: str, password_confirm: str) -> None:
    """
    Validate that passwords match.

    Args:
        password: Password
        password_confirm: Password confirmation

    Raises:
        HTTPException: If passwords don't match
    """
    if password != password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=PASSWORDS_DO_NOT_MATCH
        )


async def check_user_exists(session: AsyncSession, email: str, username: str) -> None:
    """
    Check if user with email or username already exists.
    Raises HTTPException if user exists.

    Args:
        session: Database session
        email: User email address
        username: Username

    Raises:
        HTTPException: If email or username already exists
    """
    # Check email
    email_user = await get_user_by_email(session, email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=EMAIL_EXISTS
        )

    # Check username
    username_user = await get_user_by_username(session, username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=USERNAME_EXISTS
        )


def get_device_info(request) -> dict:
    """
    Extract device information from request.

    Args:
        request: FastAPI request object

    Returns:
        Dictionary containing device information
    """
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "device_id": request.headers.get("x-device-id"),
        "device_name": request.headers.get("x-device-name"),
    }


def calculate_token_expiration(
    access_minutes: int, refresh_days: int, remember_me: bool = False
) -> tuple[int, int]:
    """
    Calculate token expiration times.

    Args:
        access_minutes: Access token expiration in minutes
        refresh_days: Refresh token expiration in days
        remember_me: Whether to extend refresh token expiration

    Returns:
        Tuple of (access_expires_in, refresh_expires_in) in seconds
    """
    access_expires_in = access_minutes * 60
    refresh_expires_in = refresh_days * 24 * 60 * 60

    if remember_me:
        refresh_expires_in *= 7

    return access_expires_in, refresh_expires_in
