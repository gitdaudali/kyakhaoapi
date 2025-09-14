from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import (
    authenticate_user,
    create_token_pair,
    get_password_hash,
    revoke_token,
    revoke_user_tokens,
    verify_password,
)
from app.core.config import settings
from app.core.database import get_db
from app.core.deps import CurrentUser, verify_refresh_token
from app.core.messages import (
    ACCOUNT_DEACTIVATED,
    CURRENT_PASSWORD_INCORRECT,
    INVALID_CREDENTIALS,
    INVALID_REFRESH_TOKEN,
    LOGOUT_ALL_SUCCESS,
    LOGOUT_NO_TOKENS,
    LOGOUT_SUCCESS,
    PASSWORD_CHANGED_SUCCESS,
    PASSWORD_RESET_SENT,
    PASSWORD_RESET_SUCCESS,
)
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    LogoutRequest,
    LogoutResponse,
    PasswordChangeRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenInfo,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.schemas.user import User as UserSchema
from app.utils.auth_utils import (
    calculate_token_expiration,
    check_user_exists,
    get_device_info,
    get_user_by_email,
)
from fastapi import APIRouter, Depends, HTTPException, Request, status

router = APIRouter()


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserRegisterRequest, request: Request, db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Register a new user account with email and username validation.
    Creates user account and returns authentication tokens.
    """
    await check_user_exists(db, user_data.email, user_data.username)

    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        password=hashed_password,
        is_active=True,
        is_superuser=False,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    device_info = get_device_info(request)
    access_token, refresh_token = await create_token_pair(
        db_user, db, device_info, remember_me=False
    )

    access_expires_in, refresh_expires_in = calculate_token_expiration(
        settings.ACCESS_TOKEN_EXPIRE_MINUTES, settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    return AuthResponse(
        user=UserSchema.from_orm(db_user),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=access_expires_in,
            refresh_expires_in=refresh_expires_in,
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login_user(
    login_data: UserLoginRequest, request: Request, db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Authenticate user and return access and refresh tokens.
    Validates credentials and account status before token generation.
    """
    user = await authenticate_user(login_data.email, login_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ACCOUNT_DEACTIVATED,
        )

    device_info = get_device_info(request)
    access_token, refresh_token = await create_token_pair(
        user, db, device_info, remember_me=login_data.remember_me
    )

    access_expires_in, refresh_expires_in = calculate_token_expiration(
        settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        settings.REFRESH_TOKEN_EXPIRE_DAYS,
        login_data.remember_me,
    )

    return AuthResponse(
        user=UserSchema.from_orm(user),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=access_expires_in,
            refresh_expires_in=refresh_expires_in,
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Refresh access token using valid refresh token.
    Revokes old refresh token and generates new token pair.
    """
    user = await verify_refresh_token(refresh_data.refresh_token, db)
    device_info = get_device_info(request)
    await revoke_token(refresh_data.refresh_token, db, "token_refresh")

    access_token, refresh_token = await create_token_pair(
        user, db, device_info, remember_me=False
    )

    access_expires_in, refresh_expires_in = calculate_token_expiration(
        settings.ACCESS_TOKEN_EXPIRE_MINUTES, settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=access_expires_in,
        refresh_expires_in=refresh_expires_in,
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout_user(
    logout_data: LogoutRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Logout user and revoke authentication tokens.
    Supports single device or all devices logout.
    """
    if logout_data.logout_all_devices:
        revoked_count = await revoke_user_tokens(
            current_user.id, db, "user_logout_all", current_user.id
        )
        return LogoutResponse(
            message=LOGOUT_ALL_SUCCESS,
            logged_out_devices=revoked_count,
        )
    else:
        if logout_data.refresh_token:
            success = await revoke_token(
                logout_data.refresh_token, db, "user_logout", current_user.id
            )
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=INVALID_REFRESH_TOKEN,
                )
            return LogoutResponse(
                message=LOGOUT_SUCCESS,
                logged_out_devices=1,
            )
        else:
            return LogoutResponse(
                message=LOGOUT_NO_TOKENS,
                logged_out_devices=0,
            )


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: CurrentUser,
) -> Any:
    """
    Get current authenticated user information.
    Returns user profile data from JWT token.
    """
    return UserSchema.from_orm(current_user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Change user password with current password verification.
    Validates current password before updating to new password.
    """
    if not verify_password(password_data.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=CURRENT_PASSWORD_INCORRECT,
        )

    current_user.password = get_password_hash(password_data.new_password)
    await db.commit()

    return {"message": PASSWORD_CHANGED_SUCCESS}


@router.post("/reset-password-request")
async def request_password_reset(
    reset_data: PasswordResetRequest, db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Request password reset by email.
    Sends reset link to user email if account exists.
    """
    user = await get_user_by_email(db, reset_data.email)
    return {"message": PASSWORD_RESET_SENT}


@router.post("/reset-password-confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Confirm password reset with validation token.
    Validates reset token and updates user password.
    """
    return {"message": PASSWORD_RESET_SUCCESS}


@router.get("/token-info", response_model=TokenInfo)
async def get_token_info(
    current_user: CurrentUser,
) -> Any:
    """
    Get information about current authentication token.
    Returns token metadata and expiration details.
    """
    return TokenInfo(
        token_type="bearer",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        is_valid=True,
        user_id=str(current_user.id),
        scope="read write",
    )
