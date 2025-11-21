"""User personalization endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response
from app.models.food import Cuisine, Restaurant, UserCuisineAssociation, UserRestaurantAssociation
from app.models.user import User
from app.schemas.personalization import PersonalizationResponse, PersonalizationUpdate
from app.utils.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Personalization"])


async def get_user_or_404(
    user_id: uuid.UUID,
    db: AsyncSession,
    current_user: User,
) -> User:
    """Get user by ID or raise 404. Also checks authorization."""
    # Only allow users to access their own data, or admins to access any user
    if str(current_user.id) != str(user_id) and not (current_user.is_staff or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own personalization settings"
        )
    
    from sqlalchemy import select
    stmt = select(User).where(User.id == user_id, User.is_deleted.is_(False))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}/personalization")
async def update_personalization(
    user_id: uuid.UUID,
    payload: PersonalizationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update user's personalization preferences.
    Includes: spice level, favorite cuisines, preferred restaurants.
    Used when user completes personalization onboarding.
    """
    try:
        # Get and verify user
        user = await get_user_or_404(user_id, db, current_user)
        
        # Update spice level if provided
        if payload.spice_level is not None:
            user.spice_level_preference = payload.spice_level
        
        # Validate and update favorite cuisines
        if payload.favorite_cuisine_ids is not None:
            # Validate that all cuisine IDs exist
            stmt = select(Cuisine).where(
                Cuisine.id.in_(payload.favorite_cuisine_ids),
                Cuisine.is_deleted.is_(False)
            )
            result = await db.execute(stmt)
            existing_cuisines = {cuisine.id for cuisine in result.scalars().all()}
            
            invalid_cuisines = set(payload.favorite_cuisine_ids) - existing_cuisines
            if invalid_cuisines:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid cuisine IDs: {', '.join(str(cid) for cid in invalid_cuisines)}"
                )
            
            # Delete existing user cuisines
            from sqlalchemy import delete as sql_delete
            delete_stmt = sql_delete(UserCuisineAssociation).where(
                UserCuisineAssociation.c.user_id == user_id
            )
            await db.execute(delete_stmt)
            
            # Add new cuisines
            if payload.favorite_cuisine_ids:
                from sqlalchemy import insert
                insert_values = [
                    {"user_id": user_id, "cuisine_id": cuisine_id}
                    for cuisine_id in payload.favorite_cuisine_ids
                ]
                if insert_values:
                    insert_stmt = insert(UserCuisineAssociation).values(insert_values)
                    await db.execute(insert_stmt)
        
        # Validate and update preferred restaurants
        if payload.preferred_restaurant_ids is not None:
            # Validate that all restaurant IDs exist
            stmt = select(Restaurant).where(
                Restaurant.id.in_(payload.preferred_restaurant_ids),
                Restaurant.is_deleted.is_(False)
            )
            result = await db.execute(stmt)
            existing_restaurants = {restaurant.id for restaurant in result.scalars().all()}
            
            invalid_restaurants = set(payload.preferred_restaurant_ids) - existing_restaurants
            if invalid_restaurants:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid restaurant IDs: {', '.join(str(rid) for rid in invalid_restaurants)}"
                )
            
            # Delete existing user restaurants
            from sqlalchemy import delete as sql_delete
            delete_stmt = sql_delete(UserRestaurantAssociation).where(
                UserRestaurantAssociation.c.user_id == user_id
            )
            await db.execute(delete_stmt)
            
            # Add new restaurants
            if payload.preferred_restaurant_ids:
                from sqlalchemy import insert
                insert_values = [
                    {"user_id": user_id, "restaurant_id": restaurant_id}
                    for restaurant_id in payload.preferred_restaurant_ids
                ]
                if insert_values:
                    insert_stmt = insert(UserRestaurantAssociation).values(insert_values)
                    await db.execute(insert_stmt)
        
        await db.commit()
        await db.refresh(user)
        
        # Get updated cuisines
        stmt = select(Cuisine).join(
            UserCuisineAssociation,
            Cuisine.id == UserCuisineAssociation.c.cuisine_id
        ).where(
            UserCuisineAssociation.c.user_id == user_id,
            Cuisine.is_deleted.is_(False)
        )
        result = await db.execute(stmt)
        favorite_cuisines = [
            {"id": str(cuisine.id), "name": cuisine.name}
            for cuisine in result.scalars().all()
        ]
        
        # Get updated restaurants
        stmt = select(Restaurant).join(
            UserRestaurantAssociation,
            Restaurant.id == UserRestaurantAssociation.c.restaurant_id
        ).where(
            UserRestaurantAssociation.c.user_id == user_id,
            Restaurant.is_deleted.is_(False)
        )
        result = await db.execute(stmt)
        preferred_restaurants = [
            {"id": str(restaurant.id), "name": restaurant.name}
            for restaurant in result.scalars().all()
        ]
        
        return {
            "userId": str(user_id),
            "spice_level": user.spice_level_preference,
            "favorite_cuisines": favorite_cuisines,
            "preferred_restaurants": preferred_restaurants,
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        return error_response(
            message=f"Error updating personalization: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{user_id}/personalization")
async def get_personalization(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get user's personalization preferences.
    """
    try:
        # Get and verify user
        user = await get_user_or_404(user_id, db, current_user)
        
        # Get favorite cuisines
        stmt = select(Cuisine).join(
            UserCuisineAssociation,
            Cuisine.id == UserCuisineAssociation.c.cuisine_id
        ).where(
            UserCuisineAssociation.c.user_id == user_id,
            Cuisine.is_deleted.is_(False)
        )
        result = await db.execute(stmt)
        favorite_cuisines = [
            {"id": str(cuisine.id), "name": cuisine.name}
            for cuisine in result.scalars().all()
        ]
        
        # Get preferred restaurants
        stmt = select(Restaurant).join(
            UserRestaurantAssociation,
            Restaurant.id == UserRestaurantAssociation.c.restaurant_id
        ).where(
            UserRestaurantAssociation.c.user_id == user_id,
            Restaurant.is_deleted.is_(False)
        )
        result = await db.execute(stmt)
        preferred_restaurants = [
            {"id": str(restaurant.id), "name": restaurant.name}
            for restaurant in result.scalars().all()
        ]
        
        return {
            "userId": str(user_id),
            "spice_level": user.spice_level_preference,
            "favorite_cuisines": favorite_cuisines,
            "preferred_restaurants": preferred_restaurants
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Error retrieving personalization: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

