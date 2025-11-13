from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.food import Restaurant
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.restaurant import (
    NearbyRestaurantRequest,
    RestaurantOut,
)
from app.utils.pagination import paginate
from app.utils.query_filters import haversine_distance_expr

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


async def get_restaurant_or_404(session: AsyncSession, restaurant_id: uuid.UUID) -> Restaurant:
    result = await session.execute(
        select(Restaurant).where(Restaurant.id == restaurant_id, Restaurant.is_deleted.is_(False))
    )
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.get("/", response_model=PaginatedResponse[RestaurantOut])
async def list_restaurants(
    params: PaginationParams = Depends(),
    city: Optional[str] = Query(default=None, description="Filter by city"),
    min_rating: Optional[float] = Query(default=None, ge=0, le=5),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[RestaurantOut]:
    stmt = select(Restaurant).where(Restaurant.is_deleted.is_(False))
    if city:
        stmt = stmt.where(func.lower(Restaurant.city) == city.lower())
    if min_rating is not None:
        stmt = stmt.where(Restaurant.rating.isnot(None), Restaurant.rating >= min_rating)

    stmt = stmt.order_by(Restaurant.rating.desc().nullslast(), Restaurant.name.asc())

    return await paginate(
        session,
        stmt,
        params,
        mapper=lambda obj: RestaurantOut.model_validate(obj),
    )


@router.get("/{restaurant_id}", response_model=RestaurantOut)
async def get_restaurant(
    restaurant_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> RestaurantOut:
    restaurant = await get_restaurant_or_404(session, restaurant_id)
    return RestaurantOut.model_validate(restaurant)


@router.get("/top-rated", response_model=List[RestaurantOut])
async def top_rated_restaurants(
    limit: int = Query(default=10, gt=0, le=50),
    session: AsyncSession = Depends(get_db),
) -> List[RestaurantOut]:
    stmt = (
        select(Restaurant)
        .where(Restaurant.is_deleted.is_(False), Restaurant.rating.isnot(None))
        .order_by(Restaurant.rating.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    restaurants = result.scalars().all()
    return [RestaurantOut.model_validate(r) for r in restaurants]


@router.get("/nearby", response_model=List[RestaurantOut])
async def nearby_restaurants(
    request: NearbyRestaurantRequest = Depends(),
    session: AsyncSession = Depends(get_db),
) -> List[RestaurantOut]:
    distance_expr = haversine_distance_expr(
        request.latitude,
        request.longitude,
        Restaurant.latitude,
        Restaurant.longitude,
    )
    stmt = (
        select(Restaurant)
        .where(
            Restaurant.is_deleted.is_(False),
            Restaurant.latitude.isnot(None),
            Restaurant.longitude.isnot(None),
            distance_expr <= request.radius_km,
        )
        .order_by(distance_expr.asc())
        .limit(request.limit)
    )
    result = await session.execute(stmt)
    restaurants = result.scalars().all()
    return [RestaurantOut.model_validate(r) for r in restaurants]
