from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

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
from app.core.deps import CurrentUser, get_current_user, verify_refresh_token
from app.core.messages import (
    ACCOUNT_DEACTIVATED,
    CURRENT_PASSWORD_INCORRECT,
    EMAIL_VERIFICATION_SUCCESS,
    EMAIL_VERIFICATION_TOKEN_INVALID,
    INVALID_CREDENTIALS,
    INVALID_REFRESH_TOKEN,
    LOGOUT_ALL_SUCCESS,
    LOGOUT_NO_TOKENS,
    LOGOUT_SUCCESS,
    PASSWORD_CHANGED_SUCCESS,
    PASSWORD_RESET_SENT,
    PASSWORD_RESET_SUCCESS,
    PASSWORD_RESET_TOKEN_INVALID,
)
from app.models.user import ProfileStatus, User, UserRole
from app.schemas.auth import (
    AuthResponse,
    EmailVerificationRequest,
    LogoutRequest,
    LogoutResponse,
    MessageResponse,
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
from app.tasks.email_tasks import (
    send_email_verification_task,
    send_password_reset_email_task,
)
from app.utils.auth_utils import (
    calculate_token_expiration,
    check_user_exists,
    get_device_info,
    get_user_by_email,
    get_user_by_id_or_404,
    validate_password_match,
)
from app.utils.token_utils import (
    create_email_verification_token,
    create_password_reset_token,
    mark_email_verification_token_used,
    mark_password_reset_token_used,
    validate_email_verification_token,
    validate_password_reset_token,
)
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer

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
    await check_user_exists(db, user_data.email)

    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        # username=user_data.username,
        password=hashed_password,
        is_active=True,
        is_superuser=False,
        role=UserRole.USER,
        profile_status=ProfileStatus.PENDING_VERIFICATION,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Create email verification token and send email
    verification_token = await create_email_verification_token(
        db, db_user.id, db_user.email
    )
    send_email_verification_task.delay(
        email_to=db_user.email, verification_token=verification_token.token
    )

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
    current_user: Annotated[User, Depends(get_current_user)],
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


@router.get("/me", response_model=UserSchema, dependencies=[Depends(HTTPBearer())])
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """
    Get current authenticated user information.
    Returns user profile data from JWT token.

    **Authentication Required**: Bearer token in Authorization header
    """
    return UserSchema.from_orm(current_user)


@router.post(
    "/change-password",
    response_model=MessageResponse,
    dependencies=[Depends(HTTPBearer())],
)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
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

    return MessageResponse(message=PASSWORD_CHANGED_SUCCESS)


@router.post("/password/reset", response_model=MessageResponse)
async def request_password_reset(
    reset_data: PasswordResetRequest, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Request password reset by email.
    Sends reset token to user email if account exists.
    """
    user = await get_user_by_email(db, reset_data.email)
    if user:
        # Create password reset token
        reset_token = await create_password_reset_token(db, user.id)

        # Send email via Celery task
        send_password_reset_email_task.delay(
            email_to=user.email,
            reset_token=reset_token.token,
        )

    return MessageResponse(message=PASSWORD_RESET_SENT)


@router.post("/password/reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Confirm password reset with validation token.
    Validates reset token and updates user password.
    """
    validate_password_match(reset_data.new_password, reset_data.new_password_confirm)

    reset_token = await validate_password_reset_token(db, reset_data.reset_token)
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=PASSWORD_RESET_TOKEN_INVALID,
        )

    user = await get_user_by_id_or_404(db, reset_token.user_id)

    user.password = get_password_hash(reset_data.new_password)

    await mark_password_reset_token_used(db, reset_data.reset_token)

    await db.commit()

    return MessageResponse(message=PASSWORD_RESET_SUCCESS)


@router.post("/email/verify", response_model=MessageResponse)
async def verify_email(
    verification_data: EmailVerificationRequest, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Verify email address using verification token.
    Validates token and marks email as verified.
    """
    verification_token = await validate_email_verification_token(
        db, verification_data.verification_token
    )
    if not verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=EMAIL_VERIFICATION_TOKEN_INVALID,
        )

    await get_user_by_id_or_404(db, verification_token.user_id)

    await mark_email_verification_token_used(db, verification_data.verification_token)

    await db.commit()

    return MessageResponse(message=EMAIL_VERIFICATION_SUCCESS)


@router.get(
    "/token-info", response_model=TokenInfo, dependencies=[Depends(HTTPBearer())]
)
async def get_token_info(
    current_user: Annotated[User, Depends(get_current_user)],
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
