from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.food import Dish
from app.schemas.dish import DishOut

router = APIRouter(prefix="/featured", tags=["User Featured"])


@router.get("/", response_model=List[DishOut])
async def featured_dish_of_the_week(
    week: Optional[date] = Query(default=None, description="ISO week date to filter on"),
    limit: int = Query(default=10, gt=0, le=50),
    session: AsyncSession = Depends(get_db),
) -> List[DishOut]:
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
    return [DishOut.model_validate(dish) for dish in dishes]
