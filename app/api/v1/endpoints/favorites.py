"""User favorites endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.core.response_handler import success_response
from app.models.favorites import UserFavorite
from app.models.food import Dish
from app.schemas.favorites import (
    FavoriteCreate,
    FavoriteListResponse,
    FavoriteResponse,
)
from app.utils.favorites_utils import (
    check_favorite_exists,
    get_user_favorites,
    soft_delete_favorite,
    verify_dish_exists,
)

router = APIRouter(tags=["Favorites"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite_data: FavoriteCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Add a dish to user favorites."""
    try:
        # Verify dish exists
        await verify_dish_exists(db, favorite_data.dish_id)

        # Check if already favorited
        if await check_favorite_exists(db, current_user.id, favorite_data.dish_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dish is already in favorites",
            )

        # Create favorite
        db_favorite = UserFavorite(
            user_id=current_user.id,
            dish_id=favorite_data.dish_id,
        )
        db.add(db_favorite)
        await db.commit()
        await db.refresh(db_favorite)

        # Load dish relationship with moods
        query = (
            select(UserFavorite)
            .options(selectinload(UserFavorite.dish).selectinload(Dish.moods))
            .where(UserFavorite.id == db_favorite.id)
        )
        result = await db.execute(query)
        favorite = result.scalar_one()

        favorite_response = FavoriteResponse.model_validate(favorite)
        return success_response(
            message="Dish added to favorites successfully",
            data=favorite_response.model_dump(),
            status_code=status.HTTP_201_CREATED
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding favorite: {str(e)}",
        )


@router.get("/", status_code=status.HTTP_200_OK)
async def get_favorites(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Get all user favorites."""
    try:
        favorites, total = await get_user_favorites(
            db, current_user.id, skip=skip, limit=limit
        )

        favorite_list = FavoriteListResponse(
            favorites=[FavoriteResponse.model_validate(fav) for fav in favorites],
            total=total,
        )
        return success_response(
            message="Favorites retrieved successfully",
            data=favorite_list.model_dump()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving favorites: {str(e)}",
        )


@router.delete("/{dish_id}", status_code=status.HTTP_200_OK)
async def remove_favorite(
    dish_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Remove a dish from user favorites."""
    try:
        favorite = await soft_delete_favorite(db, current_user.id, dish_id)
        await db.commit()

        return success_response(
            message="Favorite removed successfully",
            data={"dish_id": str(dish_id)}
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing favorite: {str(e)}",
        )


@router.get("/check/{dish_id}", status_code=status.HTTP_200_OK)
async def check_favorite(
    dish_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Check if a dish is in user favorites."""
    try:
        is_favorited = await check_favorite_exists(db, current_user.id, dish_id)

        return success_response(
            message="Favorite status retrieved successfully",
            data={"dish_id": str(dish_id), "is_favorited": is_favorited}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking favorite: {str(e)}",
        )

