from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Cuisine, Dish, Mood, Restaurant
from app.schemas.dish import DishCreate, DishOut, DishUpdate
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.utils.pagination import paginate
from app.api.v1.endpoints.dishes import get_dish_or_404, serialize_dish

router = APIRouter(prefix="/dishes", tags=["Admin"])


@router.get("/")
async def list_dishes(
    params: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """List all dishes (admin view)."""
    try:
        stmt = select(Dish).where(Dish.is_deleted.is_(False))
        stmt = stmt.options(selectinload(Dish.moods))
        stmt = stmt.order_by(Dish.name.asc())
        
        result = await paginate(
            session,
            stmt,
            params,
            mapper=serialize_dish,
        )
        
        return success_response(
            message="Dishes retrieved successfully",
            data=result.model_dump()
        )
    except Exception as e:
        return error_response(
            message=f"Error retrieving dishes: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{dish_id}")
async def get_dish(
    dish_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Get a specific dish by ID."""
    try:
        result = await session.execute(
            select(Dish)
            .options(selectinload(Dish.moods))
            .where(Dish.id == dish_id, Dish.is_deleted.is_(False))
        )
        dish = result.scalar_one_or_none()
        if not dish:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")
        
        dish_out = serialize_dish(dish)
        return success_response(
            message="Dish retrieved successfully",
            data=dish_out
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Error retrieving dish: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def ensure_related_entities(
    session: AsyncSession,
    *,
    restaurant_id: uuid.UUID,
    cuisine_id: uuid.UUID,
) -> None:
    restaurant = await session.get(Restaurant, restaurant_id)
    if not restaurant or restaurant.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    cuisine = await session.get(Cuisine, cuisine_id)
    if not cuisine or cuisine.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuisine not found")


async def get_moods_by_ids(session: AsyncSession, mood_ids: list[uuid.UUID]) -> list[Mood]:
    if not mood_ids:
        return []
    result = await session.execute(
        select(Mood).where(Mood.id.in_(mood_ids), Mood.is_deleted.is_(False))
    )
    moods = result.scalars().all()
    if len(moods) != len(set(mood_ids)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more moods not found")
    return moods


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_dish(
    payload: DishCreate,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        await ensure_related_entities(
            session, restaurant_id=payload.restaurant_id, cuisine_id=payload.cuisine_id
        )
        dish = Dish(**payload.dict(exclude={"mood_ids"}))
        if payload.mood_ids:
            dish.moods = await get_moods_by_ids(session, payload.mood_ids)
        session.add(dish)
        await session.commit()
        await session.refresh(dish)
        
        # Reload dish with moods relationship eagerly loaded
        result = await session.execute(
            select(Dish)
            .options(selectinload(Dish.moods))
            .where(Dish.id == dish.id)
        )
        dish = result.scalar_one()
        
        dish_out = serialize_dish(dish)
        return success_response(
            message="Dish created successfully",
            data=dish_out,
            status_code=status.HTTP_201_CREATED
        )
    except IntegrityError as e:
        await session.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            return error_response(
                message=f"Dish with name '{payload.name}' already exists for this restaurant",
                status_code=status.HTTP_409_CONFLICT
            )
        return error_response(
            message="Database integrity error occurred",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        error_message = str(e)
        # Handle Pydantic validation errors
        if "validation error" in error_message.lower() or "MissingGreenlet" in error_message:
            return error_response(
                message="Error serializing dish data. Please try again.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return error_response(
            message=f"Error creating dish: {error_message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/{dish_id}")
async def update_dish(
    dish_id: uuid.UUID,
    payload: DishUpdate,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        dish = await get_dish_or_404(session, dish_id)
        update_data = payload.dict(exclude_unset=True, exclude={"mood_ids"})

        if "restaurant_id" in update_data or "cuisine_id" in update_data:
            await ensure_related_entities(
                session,
                restaurant_id=update_data.get("restaurant_id", dish.restaurant_id),
                cuisine_id=update_data.get("cuisine_id", dish.cuisine_id),
            )
        for field, value in update_data.items():
            setattr(dish, field, value)

        if payload.mood_ids is not None:
            dish.moods = await get_moods_by_ids(session, payload.mood_ids)

        await session.commit()
        await session.refresh(dish)
        
        # Reload dish with moods relationship eagerly loaded
        result = await session.execute(
            select(Dish)
            .options(selectinload(Dish.moods))
            .where(Dish.id == dish.id)
        )
        dish = result.scalar_one()
        
        dish_out = serialize_dish(dish)
        return success_response(
            message="Dish updated successfully",
            data=dish_out
        )
    except IntegrityError as e:
        await session.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            name = payload.name if hasattr(payload, 'name') and payload.name else "this name"
            return error_response(
                message=f"Dish with name '{name}' already exists for this restaurant",
                status_code=status.HTTP_409_CONFLICT
            )
        return error_response(
            message="Database integrity error occurred",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        error_message = str(e)
        # Handle Pydantic validation errors
        if "validation error" in error_message.lower() or "MissingGreenlet" in error_message:
            return error_response(
                message="Error serializing dish data. Please try again.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return error_response(
            message=f"Error updating dish: {error_message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{dish_id}")
async def delete_dish(
    dish_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        dish = await get_dish_or_404(session, dish_id)
        dish.is_deleted = True
        await session.commit()
        return success_response(
            message="Dish deleted successfully",
            data={"id": str(dish.id), "name": dish.name}
        )
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error deleting dish: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

