"""Admin favorites endpoints."""
from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.core.admin_deps import AdminUser
from app.models.food import Dish, Favorite, Restaurant
from app.schemas.favorite import FavoriteAdminOut

router = APIRouter(prefix="/favorites", tags=["Admin"])


async def get_item_name(session: AsyncSession, item_id: uuid.UUID, item_type: str) -> str:
    """Get the name of an item (dish or restaurant) by ID."""
    if item_type == "dish":
        result = await session.execute(select(Dish).where(Dish.id == item_id, Dish.is_deleted.is_(False)))
        item = result.scalar_one_or_none()
        if not item:
            return "Unknown Dish"
        return item.name
    elif item_type == "restaurant":
        result = await session.execute(select(Restaurant).where(Restaurant.id == item_id, Restaurant.is_deleted.is_(False)))
        item = result.scalar_one_or_none()
        if not item:
            return "Unknown Restaurant"
        return item.name
    else:
        return "Unknown Item"


@router.get("/")
async def get_all_favorites(
    current_user: AdminUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Allows admins to view all favorites across users for analytics."""
    try:
        result = await session.execute(
            select(Favorite).where(
                Favorite.is_deleted.is_(False)
            ).order_by(Favorite.created_at.desc())
        )
        favorites = result.scalars().all()

        favorites_data = []
        for fav in favorites:
            item_name = await get_item_name(session, fav.item_id, fav.item_type)
            favorites_data.append(
                FavoriteAdminOut(
                    user_id=fav.user_id,
                    item_id=fav.item_id,
                    item_name=item_name,
                    item_type=fav.item_type,
                    added_at=fav.created_at
                ).model_dump()
            )

        return success_response(
            message="All favorites retrieved successfully",
            data=favorites_data
        )
    except Exception as e:
        return error_response(
            message=f"Error retrieving favorites: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

