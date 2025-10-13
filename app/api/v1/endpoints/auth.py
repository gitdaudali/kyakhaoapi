from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
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
    ACCOUNT_NOT_FOUND,
    CURRENT_PASSWORD_INCORRECT,
    EMAIL_ALREADY_VERIFIED,
    EMAIL_EXISTS,
    EMAIL_NOT_VERIFIED,
    EMAIL_VERIFICATION_TOKEN_INVALID,
    GOOGLE_OAUTH_ACCOUNT_CREATED,
    GOOGLE_OAUTH_ACCOUNT_EXISTS,
    GOOGLE_OAUTH_ACCOUNT_LINKED,
    GOOGLE_OAUTH_SUCCESS,
    INVALID_CREDENTIALS,
    INVALID_REFRESH_TOKEN,
    LOGOUT_ALL_SUCCESS,
    LOGOUT_NO_TOKENS,
    LOGOUT_SUCCESS,
    OTP_INVALID_OR_EXPIRED,
    OTP_RESEND_SUCCESS,
    OTP_VERIFICATION_SUCCESS,
    PASSWORD_CHANGED_SUCCESS,
    PASSWORD_RESET_OTP_SENT,
    PASSWORD_RESET_SENT,
    PASSWORD_RESET_SUCCESS,
    REGISTRATION_SUCCESS,
)
from app.models.user import ProfileStatus, User, UserRole
from app.schemas.auth import (
    AuthResponse,
    EmailVerificationRequest,
    LogoutRequest,
    LogoutResponse,
    MessageResponse,
    OTPVerificationRequest,
    PasswordChangeRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenInfo,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.schemas.google_oauth import GoogleOAuthRequest, GoogleOAuthResponse
from app.schemas.user import User as UserSchema
from app.tasks.email_tasks import (
    send_email_verification_task,
    send_password_reset_email_task,
    send_password_reset_otp_email_task,
    send_registration_otp_email_task,
)
from app.utils.auth_utils import (
    calculate_token_expiration,
    check_user_account_exists,
    check_user_exists,
    create_email_verification_otp,
    create_password_reset_otp,
    get_device_info,
    get_user_by_email,
    get_user_by_id_or_404,
    increment_otp_attempts,
    increment_password_reset_otp_attempts,
    mark_email_verification_otp_used,
    mark_password_reset_otp_used,
    update_last_login,
    validate_email_verification_otp,
    validate_password_match,
    validate_password_reset_otp,
)
from app.utils.google_oauth_utils import create_google_user
from app.utils.google_oauth_utils import get_user_by_email as get_user_by_email_oauth
from app.utils.google_oauth_utils import (
    get_user_by_google_id,
    link_google_account,
    verify_google_token,
)

router = APIRouter()


@router.post(
    "/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserRegisterRequest, request: Request, db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Register a new user account with email validation.
    Creates user account and sends OTP for email verification.
    """
    try:
        existing_user = await get_user_by_email(db, user_data.email)

        if existing_user:
            if existing_user.profile_status == ProfileStatus.PENDING_VERIFICATION:
                existing_user.password = get_password_hash(user_data.password)
                await db.commit()

                otp = await create_email_verification_otp(
                    db, existing_user.id, existing_user.email
                )
                
                # Only send email if emails are enabled
                if settings.EMAILS_ENABLED:
                    send_registration_otp_email_task.delay(
                        email_to=existing_user.email, otp_code=otp.otp_code
                    )

                return MessageResponse(message=OTP_RESEND_SUCCESS)
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=EMAIL_EXISTS,
                )

        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            password=hashed_password,
            is_active=True,
            is_superuser=False,
            role=UserRole.USER,
            profile_status=ProfileStatus.PENDING_VERIFICATION,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        # Create email verification OTP and send email
        otp = await create_email_verification_otp(db, db_user.id, db_user.email)
        
        # Only send email if emails are enabled
        if settings.EMAILS_ENABLED:
            send_registration_otp_email_task.delay(
                email_to=db_user.email, otp_code=otp.otp_code
            )

        return MessageResponse(message=REGISTRATION_SUCCESS)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}",
        )


@router.post("/login", response_model=AuthResponse)
async def login_user(
    login_data: UserLoginRequest, request: Request, db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Authenticate user and return access and refresh tokens.
    Validates credentials and account status before token generation.
    """
    try:
        await check_user_account_exists(db, login_data.email)
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

        if user.profile_status == ProfileStatus.PENDING_VERIFICATION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=EMAIL_NOT_VERIFIED,
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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}",
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
    try:
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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing token: {str(e)}",
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
    try:
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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during logout: {str(e)}",
        )


@router.get("/me", response_model=UserSchema, dependencies=[Depends(HTTPBearer())])
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """
    Returns user profile data from JWT token.
    **Authentication Required**: Bearer token in Authorization header
    """
    try:
        return UserSchema.model_validate(current_user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user info: {str(e)}",
        )


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
    try:
        if not verify_password(password_data.current_password, current_user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=CURRENT_PASSWORD_INCORRECT,
            )

        current_user.password = get_password_hash(password_data.new_password)
        await db.commit()

        return MessageResponse(message=PASSWORD_CHANGED_SUCCESS)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error changing password: {str(e)}",
        )


@router.post("/password/reset", response_model=MessageResponse)
async def request_password_reset(
    reset_data: PasswordResetRequest, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Request password reset by email.
    Sends reset OTP to user email if account exists.
    """
    try:
        user = await get_user_by_email(db, reset_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ACCOUNT_NOT_FOUND,
            )

        otp = await create_password_reset_otp(db, user.id, user.email)

        # Only send email if emails are enabled
        if settings.EMAILS_ENABLED:
            send_password_reset_otp_email_task.delay(
                email_to=user.email,
                otp_code=otp.otp_code,
                user_name=user.first_name or user.email.split("@")[0],
            )

        return MessageResponse(message=PASSWORD_RESET_OTP_SENT)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error requesting password reset: {str(e)}",
        )


@router.post("/password/reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Confirm password reset with OTP validation.
    Validates OTP and updates user password.
    """
    try:
        validate_password_match(
            reset_data.new_password, reset_data.new_password_confirm
        )

        otp = await validate_password_reset_otp(
            db, reset_data.otp_code, reset_data.email
        )
        if not otp:
            await increment_password_reset_otp_attempts(
                db, reset_data.otp_code, reset_data.email
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=OTP_INVALID_OR_EXPIRED,
            )

        user = await get_user_by_id_or_404(db, otp.user_id)

        user.password = get_password_hash(reset_data.new_password)

        await mark_password_reset_otp_used(db, reset_data.otp_code, reset_data.email)

        if reset_data.logout_all_devices:
            await revoke_user_tokens(user.id, db, "password_reset", user.id)

        await db.commit()

        return MessageResponse(message=PASSWORD_RESET_SUCCESS)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error confirming password reset: {str(e)}",
        )


@router.post("/verify-otp", response_model=MessageResponse)
async def verify_otp(
    verification_data: OTPVerificationRequest, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Verify email address using OTP code.
    Validates OTP and marks email as verified.
    """
    try:
        user = await get_user_by_email(db, verification_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ACCOUNT_NOT_FOUND,
            )

        if user.profile_status == ProfileStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=EMAIL_ALREADY_VERIFIED,
            )

        otp = await validate_email_verification_otp(
            db, verification_data.otp_code, verification_data.email
        )
        if not otp:
            await increment_otp_attempts(
                db, verification_data.otp_code, verification_data.email
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=OTP_INVALID_OR_EXPIRED,
            )

        user.profile_status = ProfileStatus.ACTIVE

        await mark_email_verification_otp_used(
            db, verification_data.otp_code, verification_data.email
        )

        await db.commit()

        return MessageResponse(message=OTP_VERIFICATION_SUCCESS)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying OTP: {str(e)}",
        )


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
    try:
        return TokenInfo(
            token_type="bearer",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
            is_valid=True,
            user_id=str(current_user.id),
            scope="read write",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving token info: {str(e)}",
        )


@router.post("/social/google", response_model=GoogleOAuthResponse)
async def google_oauth_auth(
    oauth_data: GoogleOAuthRequest, request: Request, db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Google OAuth authentication Handles both signup and signin for Google users.
    """
    try:
        google_user_info = await verify_google_token(oauth_data.access_token)

        existing_google_user = await get_user_by_google_id(db, google_user_info.id)

        if existing_google_user:
            if not existing_google_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ACCOUNT_DEACTIVATED,
                )

            await update_last_login(db, existing_google_user.id)

            await db.refresh(existing_google_user)

            device_info = get_device_info(request)
            access_token, refresh_token = await create_token_pair(
                existing_google_user, db, device_info, remember_me=False
            )

            access_expires_in, refresh_expires_in = calculate_token_expiration(
                settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                settings.REFRESH_TOKEN_EXPIRE_DAYS,
                False,
            )

            # Convert user to dict safely
            user_dict = {
                "id": str(existing_google_user.id),
                "email": existing_google_user.email,
                "first_name": existing_google_user.first_name,
                "last_name": existing_google_user.last_name,
                "is_active": existing_google_user.is_active,
                "is_staff": existing_google_user.is_staff,
                "is_superuser": existing_google_user.is_superuser,
                "role": existing_google_user.role,
                "profile_status": existing_google_user.profile_status,
                "avatar_url": existing_google_user.avatar_url,
                "signup_type": existing_google_user.signup_type,
                "google_id": existing_google_user.google_id,
                "apple_id": existing_google_user.apple_id,
                "created_at": existing_google_user.created_at,
                "updated_at": existing_google_user.updated_at,
                "last_login": existing_google_user.last_login,
            }

            return GoogleOAuthResponse(
                user=user_dict,
                tokens={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": access_expires_in,
                    "refresh_expires_in": refresh_expires_in,
                },
                is_new_user=False,
            )

        existing_email_user = await get_user_by_email_oauth(db, google_user_info.email)

        if existing_email_user:
            if not existing_email_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ACCOUNT_DEACTIVATED,
                )

            updated_user = await link_google_account(
                db, existing_email_user, google_user_info
            )

            await update_last_login(db, updated_user.id)

            await db.refresh(updated_user)

            device_info = get_device_info(request)
            access_token, refresh_token = await create_token_pair(
                updated_user, db, device_info, remember_me=False
            )

            access_expires_in, refresh_expires_in = calculate_token_expiration(
                settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                settings.REFRESH_TOKEN_EXPIRE_DAYS,
                False,
            )

            user_dict = {
                "id": str(updated_user.id),
                "email": updated_user.email,
                "first_name": updated_user.first_name,
                "last_name": updated_user.last_name,
                "is_active": updated_user.is_active,
                "is_staff": updated_user.is_staff,
                "is_superuser": updated_user.is_superuser,
                "role": updated_user.role,
                "profile_status": updated_user.profile_status,
                "avatar_url": updated_user.avatar_url,
                "signup_type": updated_user.signup_type,
                "google_id": updated_user.google_id,
                "apple_id": updated_user.apple_id,
                "created_at": updated_user.created_at,
                "updated_at": updated_user.updated_at,
                "last_login": updated_user.last_login,
            }

            return GoogleOAuthResponse(
                user=user_dict,
                tokens={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": access_expires_in,
                    "refresh_expires_in": refresh_expires_in,
                },
                is_new_user=False,
            )

        new_user = await create_google_user(db, google_user_info)

        await update_last_login(db, new_user.id)

        await db.refresh(new_user)

        device_info = get_device_info(request)
        access_token, refresh_token = await create_token_pair(
            new_user, db, device_info, remember_me=False
        )

        access_expires_in, refresh_expires_in = calculate_token_expiration(
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            settings.REFRESH_TOKEN_EXPIRE_DAYS,
            False,
        )

        user_dict = {
            "id": str(new_user.id),
            "email": new_user.email,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "is_active": new_user.is_active,
            "is_staff": new_user.is_staff,
            "is_superuser": new_user.is_superuser,
            "role": new_user.role,
            "profile_status": new_user.profile_status,
            "avatar_url": new_user.avatar_url,
            "signup_type": new_user.signup_type,
            "google_id": new_user.google_id,
            "apple_id": new_user.apple_id,
            "created_at": new_user.created_at,
            "updated_at": new_user.updated_at,
            "last_login": new_user.last_login,
        }

        return GoogleOAuthResponse(
            user=user_dict,
            tokens={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": access_expires_in,
                "refresh_expires_in": refresh_expires_in,
            },
            is_new_user=True,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during Google OAuth authentication: {str(e)}",
        )
