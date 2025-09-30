from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.core.deps import get_current_user
from app.models.user import User, UserRole


async def get_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current user with admin access verification.

    Args:
        current_user: Current user from get_current_user

    Returns:
        User: Current admin user

    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


async def get_super_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current user with super admin access verification.

    Args:
        current_user: Current user from get_current_user

    Returns:
        User: Current super admin user

    Raises:
        HTTPException: If user is not a super admin
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Super admin access required"
        )
    return current_user


async def get_content_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current user with content admin access verification.

    Args:
        current_user: Current user from get_current_user

    Returns:
        User: Current content admin user

    Raises:
        HTTPException: If user is not authorized for content management
    """
    if not (
        current_user.is_staff
        or current_user.is_superuser
        or current_user.role == UserRole.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Content admin access required",
        )
    return current_user


async def get_user_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current user with user admin access verification.

    Args:
        current_user: Current user from get_current_user

    Returns:
        User: Current user admin user

    Raises:
        HTTPException: If user is not authorized for user management
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User admin access required"
        )
    return current_user


# Common dependency aliases
AdminUser = Annotated[User, Depends(get_admin_user)]
SuperAdminUser = Annotated[User, Depends(get_super_admin_user)]
ContentAdminUser = Annotated[User, Depends(get_content_admin_user)]
UserAdminUser = Annotated[User, Depends(get_user_admin_user)]
