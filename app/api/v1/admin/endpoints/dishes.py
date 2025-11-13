from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.food import Cuisine, Dish, Mood, Restaurant
from app.schemas.dish import DishCreate, DishOut, DishUpdate
from app.api.v1.endpoints.dishes import get_dish_or_404, serialize_dish

router = APIRouter(prefix="/dishes", tags=["Admin"])


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


@router.post("/", response_model=DishOut, status_code=status.HTTP_201_CREATED)
async def create_dish(
    payload: DishCreate,
    session: AsyncSession = Depends(get_db),
) -> DishOut:
    await ensure_related_entities(
        session, restaurant_id=payload.restaurant_id, cuisine_id=payload.cuisine_id
    )
    dish = Dish(**payload.dict(exclude={"mood_ids"}))
    if payload.mood_ids:
        dish.moods = await get_moods_by_ids(session, payload.mood_ids)
    session.add(dish)
    await session.commit()
    await session.refresh(dish)
    return serialize_dish(dish)


@router.put("/{dish_id}", response_model=DishOut)
async def update_dish(
    dish_id: uuid.UUID,
    payload: DishUpdate,
    session: AsyncSession = Depends(get_db),
) -> DishOut:
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
    return serialize_dish(dish)


@router.delete("/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dish(
    dish_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Response:
    dish = await get_dish_or_404(session, dish_id)
    dish.is_deleted = True
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

