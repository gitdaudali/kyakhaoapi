"""
User favorites utility functions.
"""

from typing import List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.favorites import UserFavorite
from app.models.food import Dish


async def get_favorite_by_user_and_dish(
    session: AsyncSession, user_id: UUID, dish_id: UUID
) -> Optional[UserFavorite]:
    """
    Get favorite by user ID and dish ID.

    Args:
        session: Database session
        user_id: User UUID
        dish_id: Dish UUID

    Returns:
        UserFavorite object if found, None otherwise
    """
    query = select(UserFavorite).where(
        UserFavorite.user_id == user_id,
        UserFavorite.dish_id == dish_id,
        UserFavorite.is_deleted == False,
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def check_favorite_exists(
    session: AsyncSession, user_id: UUID, dish_id: UUID
) -> bool:
    """
    Check if a favorite already exists.

    Args:
        session: Database session
        user_id: User UUID
        dish_id: Dish UUID

    Returns:
        True if favorite exists, False otherwise
    """
    favorite = await get_favorite_by_user_and_dish(session, user_id, dish_id)
    return favorite is not None


async def get_user_favorites(
    session: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[UserFavorite], int]:
    """
    Get all favorites for a user with pagination.

    Args:
        session: Database session
        user_id: User UUID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of favorites, total count)
    """
    # Get total count
    count_query = select(func.count()).select_from(UserFavorite).where(
        UserFavorite.user_id == user_id, UserFavorite.is_deleted == False
    )
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Get favorites with dish relationship loaded
    query = (
        select(UserFavorite)
        .options(selectinload(UserFavorite.dish).selectinload(Dish.moods))
        .where(UserFavorite.user_id == user_id, UserFavorite.is_deleted == False)
        .order_by(UserFavorite.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(query)
    favorites = result.scalars().all()

    return list(favorites), total


async def verify_dish_exists(session: AsyncSession, dish_id: UUID) -> Dish:
    """
    Verify that a dish exists and is not deleted.

    Args:
        session: Database session
        dish_id: Dish UUID

    Returns:
        Dish object

    Raises:
        HTTPException: If dish not found
    """
    query = select(Dish).where(Dish.id == dish_id, Dish.is_deleted == False)
    result = await session.execute(query)
    dish = result.scalar_one_or_none()

    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found",
        )

    return dish


async def soft_delete_favorite(
    session: AsyncSession, user_id: UUID, dish_id: UUID
) -> UserFavorite:
    """
    Soft delete a favorite.

    Args:
        session: Database session
        user_id: User UUID
        dish_id: Dish UUID

    Returns:
        Deleted UserFavorite object

    Raises:
        HTTPException: If favorite not found
    """
    favorite = await get_favorite_by_user_and_dish(session, user_id, dish_id)
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )

    favorite.is_deleted = True
    return favorite


