from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_user
from app.models.user import User
from app.schemas.user import ProfileResponse
from app.schemas.user import User as UserSchema
from app.schemas.user import UserUpdate
from app.utils.s3_utils import delete_file_from_s3, upload_file_to_s3

router = APIRouter()


@router.get("/", response_model=list[UserSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get list of users (admin only)."""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get user by ID."""
    if not current_user.is_staff and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update user information."""
    if not current_user.is_staff and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update only provided fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete user (admin only)."""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


@router.patch("/profile", response_model=ProfileResponse)
async def update_profile_with_avatar(
    first_name: str = Form(None),
    last_name: str = Form(None),
    avatar: UploadFile = File(None),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """
    Update user profile with optional avatar upload in a single request.
    """
    try:
        update_data = {}
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name

        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)

        if avatar:
            avatar_url = await upload_file_to_s3(
                file=avatar,
                folder="avatars",
                allowed_extensions=settings.AVATAR_ALLOWED_FILE_TYPES,
                max_size_mb=5,
            )

            if current_user.avatar_url:
                delete_file_from_s3(current_user.avatar_url)

            current_user.avatar_url = avatar_url

        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)

        return ProfileResponse(
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            email=current_user.email,
            avatar_url=current_user.avatar_url,
            is_email_verified=current_user.profile_status != "pending_verification",
            profile_complete=bool(current_user.first_name and current_user.last_name),
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}",
        )
