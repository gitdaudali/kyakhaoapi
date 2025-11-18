from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Cuisine, Dish, Restaurant
from app.schemas.cuisine import CuisineOut
from app.schemas.dish import DishOut
from app.schemas.restaurant import RestaurantOut

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
async def global_search(
    q: str = Query(..., min_length=2, description="Search keyword"),
    limit: int = Query(default=10, gt=0, le=50),
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        term = f"%{q.lower()}%"

        dish_stmt = (
            select(Dish)
            .options(selectinload(Dish.moods))
            .where(Dish.is_deleted.is_(False), func.lower(Dish.name).like(term))
            .limit(limit)
        )
        restaurant_stmt = (
            select(Restaurant)
            .where(Restaurant.is_deleted.is_(False), func.lower(Restaurant.name).like(term))
            .limit(limit)
        )
        cuisine_stmt = (
            select(Cuisine)
            .where(Cuisine.is_deleted.is_(False), func.lower(Cuisine.name).like(term))
            .limit(limit)
        )

        dish_result = await session.execute(dish_stmt)
        dishes = [DishOut.model_validate(item).model_dump() for item in dish_result.scalars().all()]

        restaurant_result = await session.execute(restaurant_stmt)
        restaurants = [RestaurantOut.model_validate(item).model_dump() for item in restaurant_result.scalars().all()]

        cuisine_result = await session.execute(cuisine_stmt)
        cuisines = [CuisineOut.model_validate(item).model_dump() for item in cuisine_result.scalars().all()]

        search_data = {
            "query": q,
            "dishes": dishes,
            "restaurants": restaurants,
            "cuisines": cuisines
        }
        
        return success_response(
            message="Search completed successfully",
            data=search_data
        )
    except Exception as e:
        return error_response(
            message=f"Error performing search: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
