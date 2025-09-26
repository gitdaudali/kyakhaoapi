from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import GOOGLE_USER_INFO_API_URL
from app.core.messages import (
    GOOGLE_OAUTH_DISABLED,
    GOOGLE_OAUTH_EMAIL_NOT_VERIFIED,
    GOOGLE_OAUTH_INVALID_TOKEN,
    GOOGLE_OAUTH_TOKEN_VERIFICATION_FAILED,
)
from app.models.user import ProfileStatus, SignupType, User
from app.schemas.google_oauth import GoogleUserInfo


async def verify_google_token(access_token: str) -> GoogleUserInfo:
    """
    Verify Google access token and return user information

    Args:
        access_token: Google access token

    Returns:
        GoogleUserInfo: User information from Google

    Raises:
        HTTPException: If token verification fails
    """
    if not settings.GOOGLE_OAUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=GOOGLE_OAUTH_DISABLED,
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_USER_INFO_API_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0,
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=GOOGLE_OAUTH_INVALID_TOKEN,
                )

            user_data = response.json()

            # Validate required fields
            if not user_data.get("id") or not user_data.get("email"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=GOOGLE_OAUTH_TOKEN_VERIFICATION_FAILED,
                )

            # Check email verification
            if not user_data.get("verified_email", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=GOOGLE_OAUTH_EMAIL_NOT_VERIFIED,
                )

            return GoogleUserInfo(**user_data)

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify Google token. Please try again later.",
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=GOOGLE_OAUTH_TOKEN_VERIFICATION_FAILED,
        )


async def get_user_by_google_id(db: AsyncSession, google_id: str) -> Optional[User]:
    """
    Get user by Google ID

    Args:
        db: Database session
        google_id: Google user ID

    Returns:
        User or None if not found
    """
    query = select(User).where(User.google_id == google_id, User.is_deleted == False)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get user by email address

    Args:
        db: Database session
        email: User email

    Returns:
        User or None if not found
    """
    query = select(User).where(User.email == email, User.is_deleted == False)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_google_user(
    db: AsyncSession, google_user_info: GoogleUserInfo
) -> User:
    """
    Create a new user from Google OAuth information

    Args:
        db: Database session
        google_user_info: Google user information

    Returns:
        User: Created user
    """
    # Extract names
    first_name = google_user_info.given_name or ""
    last_name = google_user_info.family_name or ""

    # If no given_name/family_name, try to split name
    if not first_name and not last_name and google_user_info.name:
        name_parts = google_user_info.name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

    user = User(
        email=google_user_info.email,
        first_name=first_name,
        last_name=last_name,
        password=None,  # No password for OAuth users
        signup_type=SignupType.GOOGLE,
        google_id=google_user_info.id,
        avatar_url=google_user_info.picture,
        profile_status=ProfileStatus.ACTIVE,  # Google emails are pre-verified
        is_active=True,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def link_google_account(
    db: AsyncSession, user: User, google_user_info: GoogleUserInfo
) -> User:
    """
    Link Google account to existing user

    Args:
        db: Database session
        user: Existing user
        google_user_info: Google user information

    Returns:
        User: Updated user
    """
    user.google_id = google_user_info.id
    user.signup_type = SignupType.GOOGLE

    # Update avatar if not set
    if not user.avatar_url and google_user_info.picture:
        user.avatar_url = google_user_info.picture

    # Update names if not set
    if not user.first_name and google_user_info.given_name:
        user.first_name = google_user_info.given_name
    if not user.last_name and google_user_info.family_name:
        user.last_name = google_user_info.family_name

    await db.commit()
    await db.refresh(user)

    return user
