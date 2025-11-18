from __future__ import annotations

import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
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


@router.get("/")
async def list_restaurants(
    params: PaginationParams = Depends(),
    city: Optional[str] = Query(default=None, description="Filter by city"),
    min_rating: Optional[float] = Query(default=None, ge=0, le=5),
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        stmt = select(Restaurant).where(Restaurant.is_deleted.is_(False))
        if city:
            stmt = stmt.where(func.lower(Restaurant.city) == city.lower())
        if min_rating is not None:
            stmt = stmt.where(Restaurant.rating.isnot(None), Restaurant.rating >= min_rating)

        stmt = stmt.order_by(Restaurant.rating.desc().nullslast(), Restaurant.name.asc())

        result = await paginate(
            session,
            stmt,
            params,
            mapper=lambda obj: RestaurantOut.model_validate(obj),
        )
        
        return success_response(
            message="Restaurants retrieved successfully",
            data=result.model_dump()
        )
    except Exception as e:
        return error_response(
            message=f"Error retrieving restaurants: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# IMPORTANT: Specific routes must come BEFORE parameterized routes like /{restaurant_id}
# Otherwise FastAPI will try to match "top-rated" and "nearby" as UUIDs
@router.get("/top-rated")
async def top_rated_restaurants(
    limit: int = Query(default=10, gt=0, le=50),
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        stmt = (
            select(Restaurant)
            .where(Restaurant.is_deleted.is_(False), Restaurant.rating.isnot(None))
            .order_by(Restaurant.rating.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        restaurants = result.scalars().all()
        restaurants_data = [RestaurantOut.model_validate(r).model_dump() for r in restaurants]
        
        return success_response(
            message="Top rated restaurants retrieved successfully",
            data=restaurants_data
        )
    except Exception as e:
        return error_response(
            message=f"Error retrieving top rated restaurants: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/nearby")
async def nearby_restaurants(
    request: NearbyRestaurantRequest = Depends(),
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
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
        restaurants_data = [RestaurantOut.model_validate(r).model_dump() for r in restaurants]
        
        return success_response(
            message="Nearby restaurants retrieved successfully",
            data=restaurants_data
        )
    except Exception as e:
        return error_response(
            message=f"Error retrieving nearby restaurants: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{restaurant_id}")
async def get_restaurant(
    restaurant_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        restaurant = await get_restaurant_or_404(session, restaurant_id)
        restaurant_out = RestaurantOut.model_validate(restaurant)
        return success_response(
            message="Restaurant retrieved successfully",
            data=restaurant_out.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Error retrieving restaurant: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
