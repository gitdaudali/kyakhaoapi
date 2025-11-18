"""User favorites endpoints."""
from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Dish, Favorite, Restaurant
from app.schemas.favorite import FavoriteCreate, FavoriteListItem, FavoriteOut
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/favorites", tags=["Favorites"])


async def get_item_name(session: AsyncSession, item_id: uuid.UUID, item_type: str) -> str:
    """Get the name of an item (dish or restaurant) by ID."""
    if item_type == "dish":
        result = await session.execute(select(Dish).where(Dish.id == item_id, Dish.is_deleted.is_(False)))
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")
        return item.name
    elif item_type == "restaurant":
        result = await session.execute(select(Restaurant).where(Restaurant.id == item_id, Restaurant.is_deleted.is_(False)))
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
        return item.name
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item_type. Must be 'dish' or 'restaurant'")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_to_favorites(
    payload: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Add an item to the authenticated user's favorites."""
    try:
        # Verify item exists
        await get_item_name(session, payload.item_id, payload.item_type)

        # Check if already favorited
        result = await session.execute(
            select(Favorite).where(
                Favorite.user_id == current_user.id,
                Favorite.item_id == payload.item_id,
                Favorite.item_type == payload.item_type,
                Favorite.is_deleted.is_(False)
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return error_response(
                message="Item is already in favorites",
                status_code=status.HTTP_409_CONFLICT
            )

        favorite = Favorite(
            user_id=current_user.id,
            item_id=payload.item_id,
            item_type=payload.item_type
        )
        session.add(favorite)
        await session.commit()
        await session.refresh(favorite)

        favorite_out = FavoriteOut(
            id=favorite.id,
            item_id=favorite.item_id,
            item_type=favorite.item_type,
            added_at=favorite.created_at
        )

        return success_response(
            message="Added to favorites",
            data=favorite_out.model_dump(),
            status_code=status.HTTP_201_CREATED
        )
    except IntegrityError:
        await session.rollback()
        return error_response(
            message="Item is already in favorites",
            status_code=status.HTTP_409_CONFLICT
        )
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error adding to favorites: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/")
async def remove_from_favorites(
    payload: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Remove an item from the authenticated user's favorites."""
    try:
        result = await session.execute(
            select(Favorite).where(
                Favorite.user_id == current_user.id,
                Favorite.item_id == payload.item_id,
                Favorite.item_type == payload.item_type,
                Favorite.is_deleted.is_(False)
            )
        )
        favorite = result.scalar_one_or_none()
        if not favorite:
            return error_response(
                message="Item not found in favorites",
                status_code=status.HTTP_404_NOT_FOUND
            )

        favorite.is_deleted = True
        await session.commit()

        return success_response(
            message="Removed from favorites",
            data=None
        )
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error removing from favorites: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/")
async def get_user_favorites(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Retrieve the list of favorites for the authenticated user."""
    try:
        result = await session.execute(
            select(Favorite).where(
                Favorite.user_id == current_user.id,
                Favorite.is_deleted.is_(False)
            ).order_by(Favorite.created_at.desc())
        )
        favorites = result.scalars().all()

        favorites_data = []
        for fav in favorites:
            try:
                item_name = await get_item_name(session, fav.item_id, fav.item_type)
                favorites_data.append(
                    FavoriteListItem(
                        item_id=fav.item_id,
                        name=item_name,
                        added_at=fav.created_at
                    ).model_dump()
                )
            except HTTPException:
                # Skip items that no longer exist
                continue

        return success_response(
            message="Favorites retrieved successfully",
            data=favorites_data
        )
    except Exception as e:
        return error_response(
            message=f"Error retrieving favorites: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

