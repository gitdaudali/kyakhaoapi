from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.food import Cuisine, Dish, Restaurant
from app.schemas.cuisine import CuisineOut
from app.schemas.dish import DishOut
from app.schemas.restaurant import RestaurantOut
from app.schemas.search import SearchResponse

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/", response_model=SearchResponse)
async def global_search(
    q: str = Query(..., min_length=2, description="Search keyword"),
    limit: int = Query(default=10, gt=0, le=50),
    session: AsyncSession = Depends(get_db),
) -> SearchResponse:
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
    dishes = [DishOut.model_validate(item) for item in dish_result.scalars().all()]

    restaurant_result = await session.execute(restaurant_stmt)
    restaurants = [RestaurantOut.model_validate(item) for item in restaurant_result.scalars().all()]

    cuisine_result = await session.execute(cuisine_stmt)
    cuisines = [CuisineOut.model_validate(item) for item in cuisine_result.scalars().all()]

    return SearchResponse(query=q, dishes=dishes, restaurants=restaurants, cuisines=cuisines)
