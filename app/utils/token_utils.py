"""
Token utility functions for password reset and email verification.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User as UserModel
from app.models.verification import EmailVerificationToken, PasswordResetToken


def generate_secure_token() -> str:
    """
    Generate a secure random token.

    Returns:
        Secure random token string
    """
    return str(uuid.uuid4())


async def create_password_reset_token(
    session: AsyncSession, user_id: uuid.UUID
) -> PasswordResetToken:
    """
    Create a password reset token for user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        PasswordResetToken instance
    """
    # Invalidate any existing tokens for this user
    await session.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.user_id == user_id, PasswordResetToken.is_used == False
        )
    )

    # Create new token
    token = generate_secure_token()
    reset_token = PasswordResetToken(
        token=token,
        user_id=user_id,
        expires_at=datetime.now(timezone.utc)
        + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS),
    )

    session.add(reset_token)
    await session.commit()
    await session.refresh(reset_token)

    return reset_token


async def create_email_verification_token(
    session: AsyncSession, user_id: uuid.UUID, email: str
) -> EmailVerificationToken:
    """
    Create an email verification token for user.

    Args:
        session: Database session
        user_id: User ID
        email: Email address to verify

    Returns:
        EmailVerificationToken instance
    """
    # Invalidate any existing tokens for this user and email
    await session.execute(
        select(EmailVerificationToken).where(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.email == email,
            EmailVerificationToken.is_used == False,
        )
    )

    # Create new token
    token = generate_secure_token()
    verification_token = EmailVerificationToken(
        token=token,
        user_id=user_id,
        email=email,
        expires_at=datetime.now(timezone.utc)
        + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS),
    )

    session.add(verification_token)
    await session.commit()
    await session.refresh(verification_token)

    return verification_token


async def validate_password_reset_token(
    session: AsyncSession, token: str
) -> Optional[PasswordResetToken]:
    """
    Validate password reset token.

    Args:
        session: Database session
        token: Password reset token

    Returns:
        PasswordResetToken if valid, None otherwise
    """
    result = await session.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.is_used == False,
            PasswordResetToken.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.scalar_one_or_none()


async def validate_email_verification_token(
    session: AsyncSession, token: str
) -> Optional[EmailVerificationToken]:
    """
    Validate email verification token.

    Args:
        session: Database session
        token: Email verification token

    Returns:
        EmailVerificationToken if valid, None otherwise
    """
    result = await session.execute(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token == token,
            EmailVerificationToken.is_used == False,
            EmailVerificationToken.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.scalar_one_or_none()


async def mark_password_reset_token_used(session: AsyncSession, token: str) -> bool:
    """
    Mark password reset token as used.

    Args:
        session: Database session
        token: Password reset token

    Returns:
        True if token was marked as used, False otherwise
    """
    result = await session.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == token, PasswordResetToken.is_used == False
        )
    )
    reset_token = result.scalar_one_or_none()

    if reset_token:
        reset_token.is_used = True
        reset_token.used_at = datetime.now(timezone.utc)
        await session.commit()
        return True

    return False


async def mark_email_verification_token_used(session: AsyncSession, token: str) -> bool:
    """
    Mark email verification token as used.

    Args:
        session: Database session
        token: Email verification token

    Returns:
        True if token was marked as used, False otherwise
    """
    result = await session.execute(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token == token,
            EmailVerificationToken.is_used == False,
        )
    )
    verification_token = result.scalar_one_or_none()

    if verification_token:
        verification_token.is_used = True
        verification_token.used_at = datetime.now(timezone.utc)
        await session.commit()
        return True

    return False
