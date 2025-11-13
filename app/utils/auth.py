from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.core.admin_deps import get_admin_user
from app.core.deps import get_current_user as core_get_current_user
from app.models.user import User


async def get_current_user(
    current_user: Annotated[User, Depends(core_get_current_user)],
) -> User:
    """Placeholder dependency for retrieving the current authenticated user."""
    return current_user


async def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Placeholder dependency for retrieving an authenticated admin user."""
    return await get_admin_user(current_user=current_user)


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]

