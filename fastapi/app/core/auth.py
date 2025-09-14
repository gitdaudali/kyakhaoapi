import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.token import RefreshToken, Token, TokenBlacklist
from app.models.user import User
from fastapi import HTTPException, status

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4()),  # JWT ID for token tracking
    }

    if additional_claims:
        to_encode.update(additional_claims)

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create JWT refresh token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4()),  # JWT ID for token tracking
    }

    if additional_claims:
        to_encode.update(additional_claims)

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def get_current_user_id(token: str) -> uuid.UUID:
    """Get user ID from JWT token"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
        )

    try:
        return uuid.UUID(payload.get("sub"))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID in token"
        )


async def authenticate_user(
    email: str, password: str, db: AsyncSession
) -> Optional[User]:
    """Authenticate user with email and password"""
    result = await db.execute(
        select(User).where(User.email == email, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()

    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


async def create_token_pair(
    user: User,
    db: AsyncSession,
    device_info: Optional[Dict[str, str]] = None,
    remember_me: bool = False,
) -> tuple[str, str]:
    """
    Create access and refresh token pair for user

    Args:
        user: User object
        db: Database session
        device_info: Optional device information
        remember_me: Whether to extend token expiration

    Returns:
        Tuple of (access_token, refresh_token)
    """
    # Calculate token expiration
    access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expires = timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS * (7 if remember_me else 1)
    )

    # Create token family for refresh token rotation
    token_family = uuid.uuid4()

    # Create access token
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_expires,
        additional_claims={
            "email": user.email,
            "username": user.username,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active,
        },
    )

    # Create refresh token
    refresh_token = create_refresh_token(
        subject=user.id,
        expires_delta=refresh_expires,
        additional_claims={"token_family": str(token_family)},
    )

    # Store tokens in database
    now = datetime.now(timezone.utc)

    # Store access token
    access_token_obj = Token(
        token=access_token,
        token_type="bearer",
        expires_at=now + access_expires,
        user_id=user.id,
        token_family=token_family,
        device_id=device_info.get("device_id") if device_info else None,
        device_name=device_info.get("device_name") if device_info else None,
        ip_address=device_info.get("ip_address") if device_info else None,
        user_agent=device_info.get("user_agent") if device_info else None,
        scope="read write",
    )
    db.add(access_token_obj)

    # Store refresh token
    refresh_token_obj = RefreshToken(
        token=refresh_token,
        expires_at=now + refresh_expires,
        user_id=user.id,
        token_family=token_family,
        device_id=device_info.get("device_id") if device_info else None,
        device_name=device_info.get("device_name") if device_info else None,
        ip_address=device_info.get("ip_address") if device_info else None,
        user_agent=device_info.get("user_agent") if device_info else None,
        parent_token_id=access_token_obj.id,
    )
    db.add(refresh_token_obj)

    await db.commit()

    return access_token, refresh_token


async def revoke_token(
    token: str,
    db: AsyncSession,
    reason: str = "user_logout",
    revoked_by: Optional[uuid.UUID] = None,
) -> bool:
    """
    Revoke a token by adding it to blacklist

    Args:
        token: Token to revoke
        db: Database session
        reason: Reason for revocation
        revoked_by: User ID who revoked the token

    Returns:
        True if token was revoked successfully
    """
    try:
        # Decode token to get expiration
        payload = verify_token(token)
        if not payload:
            return False

        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        user_id = uuid.UUID(payload["sub"]) if payload.get("sub") else None

        # Add to blacklist
        blacklist_entry = TokenBlacklist(
            token=token,
            token_type=payload.get("type", "unknown"),
            expires_at=expires_at,
            user_id=user_id,
            reason=reason,
            revoked_by=revoked_by,
        )
        db.add(blacklist_entry)

        # Mark token as revoked in database
        if payload.get("type") == "access":
            result = await db.execute(select(Token).where(Token.token == token))
            token_obj = result.scalar_one_or_none()
            if token_obj:
                token_obj.is_revoked = True
        elif payload.get("type") == "refresh":
            result = await db.execute(
                select(RefreshToken).where(RefreshToken.token == token)
            )
            refresh_token_obj = result.scalar_one_or_none()
            if refresh_token_obj:
                refresh_token_obj.is_revoked = True

        await db.commit()
        return True

    except Exception:
        await db.rollback()
        return False


async def revoke_user_tokens(
    user_id: uuid.UUID,
    db: AsyncSession,
    reason: str = "user_logout_all",
    revoked_by: Optional[uuid.UUID] = None,
) -> int:
    """
    Revoke all tokens for a user

    Args:
        user_id: User ID
        db: Database session
        reason: Reason for revocation
        revoked_by: User ID who revoked the tokens

    Returns:
        Number of tokens revoked
    """
    try:
        # Get all active tokens for user
        access_tokens = await db.execute(
            select(Token).where(
                Token.user_id == user_id,
                Token.is_revoked is False,
                Token.expires_at > datetime.now(timezone.utc),
            )
        )
        refresh_tokens = await db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked is False,
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )

        revoked_count = 0

        # Revoke access tokens
        for token_obj in access_tokens.scalars():
            token_obj.is_revoked = True
            revoked_count += 1

            # Add to blacklist
            blacklist_entry = TokenBlacklist(
                token=token_obj.token,
                token_type="access",
                expires_at=token_obj.expires_at,
                user_id=user_id,
                reason=reason,
                revoked_by=revoked_by,
            )
            db.add(blacklist_entry)

        # Revoke refresh tokens
        for refresh_token_obj in refresh_tokens.scalars():
            refresh_token_obj.is_revoked = True
            revoked_count += 1

            # Add to blacklist
            blacklist_entry = TokenBlacklist(
                token=refresh_token_obj.token,
                token_type="refresh",
                expires_at=refresh_token_obj.expires_at,
                user_id=user_id,
                reason=reason,
                revoked_by=revoked_by,
            )
            db.add(blacklist_entry)

        await db.commit()
        return revoked_count

    except Exception:
        await db.rollback()
        return 0


async def cleanup_expired_tokens(db: AsyncSession) -> int:
    """
    Clean up expired tokens from database

    Args:
        db: Database session

    Returns:
        Number of tokens cleaned up
    """
    try:
        now = datetime.now(timezone.utc)

        # Delete expired access tokens
        expired_access = await db.execute(select(Token).where(Token.expires_at < now))
        access_count = len(expired_access.scalars().all())

        # Delete expired refresh tokens
        expired_refresh = await db.execute(
            select(RefreshToken).where(RefreshToken.expires_at < now)
        )
        refresh_count = len(expired_refresh.scalars().all())

        # Delete expired blacklist entries
        expired_blacklist = await db.execute(
            select(TokenBlacklist).where(TokenBlacklist.expires_at < now)
        )
        blacklist_count = len(expired_blacklist.scalars().all())

        # Execute deletions
        await db.execute(select(Token).where(Token.expires_at < now).delete())
        await db.execute(
            select(RefreshToken).where(RefreshToken.expires_at < now).delete()
        )
        await db.execute(
            select(TokenBlacklist).where(TokenBlacklist.expires_at < now).delete()
        )

        await db.commit()
        return access_count + refresh_count + blacklist_count

    except Exception:
        await db.rollback()
        return 0
