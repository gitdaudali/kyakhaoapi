"""
Authentication utility functions for user management and validation.
"""

import random
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.messages import (
    EMAIL_EXISTS,
    OTP_EXPIRED,
    OTP_INVALID,
    PASSWORDS_DO_NOT_MATCH,
    USER_NOT_FOUND,
    USERNAME_EXISTS,
)
from app.models.user import User as UserModel
from app.models.verification import EmailVerificationOTP, PasswordResetOTP


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


async def check_user_exists(session: AsyncSession, email: str) -> None:
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

    # # Check username
    # username_user = await get_user_by_username(session, username)
    # if username_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail=USERNAME_EXISTS
    #     )


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


def generate_otp() -> str:
    """
    Generate a 6-digit OTP code.

    Returns:
        6-digit OTP code as string
    """
    # return str(random.randint(100000, 999999)) static for now as Design is not updated yet for mobile
    return "888888"


async def create_email_verification_otp(
    session: AsyncSession, user_id: str, email: str
) -> EmailVerificationOTP:
    """
    Create a new email verification OTP for a user.

    Args:
        session: Database session
        user_id: User ID
        email: User email address

    Returns:
        EmailVerificationOTP object
    """
    # Invalidate any existing OTPs for this user
    await session.execute(
        select(EmailVerificationOTP).where(
            EmailVerificationOTP.user_id == user_id,
            EmailVerificationOTP.is_used == False,
        )
    )
    existing_otps = await session.execute(
        select(EmailVerificationOTP).where(
            EmailVerificationOTP.user_id == user_id,
            EmailVerificationOTP.is_used == False,
        )
    )
    for otp in existing_otps.scalars().all():
        otp.is_used = True
        otp.used_at = datetime.now(timezone.utc)

    # Create new OTP
    otp_code = generate_otp()
    otp = EmailVerificationOTP(
        otp_code=otp_code,
        user_id=user_id,
        email=email,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    session.add(otp)
    await session.commit()
    await session.refresh(otp)

    return otp


async def validate_email_verification_otp(
    session: AsyncSession, otp_code: str, email: str
) -> Optional[EmailVerificationOTP]:
    """
    Validate email verification OTP.

    Args:
        session: Database session
        otp_code: OTP code to validate
        email: User email address

    Returns:
        EmailVerificationOTP object if valid, None otherwise
    """
    result = await session.execute(
        select(EmailVerificationOTP).where(
            EmailVerificationOTP.otp_code == otp_code,
            EmailVerificationOTP.email == email,
            EmailVerificationOTP.is_used == False,
            EmailVerificationOTP.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.scalar_one_or_none()


async def mark_email_verification_otp_used(
    session: AsyncSession, otp_code: str, email: str
) -> bool:
    """
    Mark email verification OTP as used.

    Args:
        session: Database session
        otp_code: OTP code to mark as used
        email: User email address

    Returns:
        True if OTP was marked as used, False otherwise
    """
    result = await session.execute(
        select(EmailVerificationOTP).where(
            EmailVerificationOTP.otp_code == otp_code,
            EmailVerificationOTP.email == email,
            EmailVerificationOTP.is_used == False,
        )
    )
    otp = result.scalar_one_or_none()

    if otp:
        otp.is_used = True
        otp.used_at = datetime.now(timezone.utc)
        await session.commit()
        return True

    return False


async def increment_otp_attempts(
    session: AsyncSession, otp_code: str, email: str
) -> bool:
    """
    Increment OTP verification attempts.

    Args:
        session: Database session
        otp_code: OTP code
        email: User email address

    Returns:
        True if attempts were incremented, False otherwise
    """
    result = await session.execute(
        select(EmailVerificationOTP).where(
            EmailVerificationOTP.otp_code == otp_code,
            EmailVerificationOTP.email == email,
        )
    )
    otp = result.scalar_one_or_none()

    if otp:
        otp.attempts += 1
        await session.commit()
        return True

    return False


async def create_password_reset_otp(
    session: AsyncSession, user_id: str, email: str
) -> PasswordResetOTP:
    """
    Create a new password reset OTP for a user.

    Args:
        session: Database session
        user_id: User ID
        email: User email address

    Returns:
        PasswordResetOTP object
    """
    # Invalidate any existing OTPs for this user
    await session.execute(
        select(PasswordResetOTP).where(
            PasswordResetOTP.user_id == user_id,
            PasswordResetOTP.is_used == False,
        )
    )
    existing_otps = await session.execute(
        select(PasswordResetOTP).where(
            PasswordResetOTP.user_id == user_id,
            PasswordResetOTP.is_used == False,
        )
    )
    for otp in existing_otps.scalars().all():
        otp.is_used = True
        otp.used_at = datetime.now(timezone.utc)

    # Create new OTP
    otp_code = generate_otp()
    otp = PasswordResetOTP(
        otp_code=otp_code,
        user_id=user_id,
        email=email,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    session.add(otp)
    await session.commit()
    await session.refresh(otp)

    return otp


async def validate_password_reset_otp(
    session: AsyncSession, otp_code: str, email: str
) -> Optional[PasswordResetOTP]:
    """
    Validate password reset OTP.

    Args:
        session: Database session
        otp_code: OTP code to validate
        email: User email address

    Returns:
        PasswordResetOTP object if valid, None otherwise
    """
    result = await session.execute(
        select(PasswordResetOTP).where(
            PasswordResetOTP.otp_code == otp_code,
            PasswordResetOTP.email == email,
            PasswordResetOTP.is_used == False,
            PasswordResetOTP.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.scalar_one_or_none()


async def mark_password_reset_otp_used(
    session: AsyncSession, otp_code: str, email: str
) -> bool:
    """
    Mark password reset OTP as used.

    Args:
        session: Database session
        otp_code: OTP code to mark as used
        email: User email address

    Returns:
        True if OTP was marked as used, False otherwise
    """
    result = await session.execute(
        select(PasswordResetOTP).where(
            PasswordResetOTP.otp_code == otp_code,
            PasswordResetOTP.email == email,
            PasswordResetOTP.is_used == False,
        )
    )
    otp = result.scalar_one_or_none()

    if otp:
        otp.is_used = True
        otp.used_at = datetime.now(timezone.utc)
        await session.commit()
        return True

    return False


async def increment_password_reset_otp_attempts(
    session: AsyncSession, otp_code: str, email: str
) -> bool:
    """
    Increment password reset OTP verification attempts.

    Args:
        session: Database session
        otp_code: OTP code
        email: User email address

    Returns:
        True if attempts were incremented, False otherwise
    """
    result = await session.execute(
        select(PasswordResetOTP).where(
            PasswordResetOTP.otp_code == otp_code,
            PasswordResetOTP.email == email,
        )
    )
    otp = result.scalar_one_or_none()

    if otp:
        otp.attempts += 1
        await session.commit()
        return True

    return False
