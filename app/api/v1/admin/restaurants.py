from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.food import Restaurant
from app.schemas.restaurant import RestaurantCreate, RestaurantOut, RestaurantUpdate
from app.api.v1.user.restaurants import get_restaurant_or_404

router = APIRouter(prefix="/restaurants", tags=["Admin Restaurants"])


@router.post("/", response_model=RestaurantOut, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    payload: RestaurantCreate,
    session: AsyncSession = Depends(get_db),
) -> RestaurantOut:
    restaurant = Restaurant(**payload.dict())
    session.add(restaurant)
    await session.commit()
    await session.refresh(restaurant)
    return RestaurantOut.model_validate(restaurant)


@router.put("/{restaurant_id}", response_model=RestaurantOut)
async def update_restaurant(
    restaurant_id: uuid.UUID,
    payload: RestaurantUpdate,
    session: AsyncSession = Depends(get_db),
) -> RestaurantOut:
    restaurant = await get_restaurant_or_404(session, restaurant_id)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(restaurant, field, value)
    await session.commit()
    await session.refresh(restaurant)
    return RestaurantOut.model_validate(restaurant)


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant(
    restaurant_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Response:
    restaurant = await get_restaurant_or_404(session, restaurant_id)
    restaurant.is_deleted = True
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

