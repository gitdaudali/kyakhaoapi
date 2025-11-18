from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Dish
from app.schemas.dish import DishOut

router = APIRouter(prefix="/featured", tags=["Featured"])


@router.get("/")
async def featured_dish_of_the_week(
    week: Optional[date] = Query(default=None, description="ISO week date to filter on"),
    limit: int = Query(default=10, gt=0, le=50),
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        stmt = (
            select(Dish)
            .options(selectinload(Dish.moods))
            .where(Dish.is_deleted.is_(False), Dish.is_featured.is_(True))
        )
        if week:
            stmt = stmt.where(Dish.featured_week == week)
        stmt = stmt.order_by(Dish.featured_week.desc().nullslast(), Dish.updated_at.desc()).limit(limit)

        result = await session.execute(stmt)
        dishes = result.scalars().all()
        dishes_data = [DishOut.model_validate(dish).model_dump() for dish in dishes]
        
        return success_response(
            message="Featured dishes retrieved successfully",
            data=dishes_data
        )
    except Exception as e:
        return error_response(
            message=f"Error retrieving featured dishes: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
