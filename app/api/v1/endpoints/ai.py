from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.food import Dish
from app.schemas.ai import AISuggestionsResponse
from app.schemas.dish import DishOut

router = APIRouter(prefix="/ai", tags=["AI Suggestions"])


@router.get("/suggestions", response_model=AISuggestionsResponse)
async def ai_suggestions(
    strategy: Literal["random", "top-rated"] = Query(default="random"),
    limit: int = Query(default=5, gt=0, le=20),
    session: AsyncSession = Depends(get_db),
) -> AISuggestionsResponse:
    stmt = select(Dish).options(selectinload(Dish.moods)).where(Dish.is_deleted.is_(False))

    if strategy == "random":
        stmt = stmt.order_by(func.random())
    else:
        stmt = stmt.where(Dish.rating.isnot(None)).order_by(Dish.rating.desc())

    stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    dishes = result.scalars().all()
    return AISuggestionsResponse(
        strategy=strategy,
        dishes=[DishOut.model_validate(dish) for dish in dishes],
    )
