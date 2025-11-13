from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.food import Dish, Mood
from app.schemas.dish import DishFilterParams, DishOut
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.utils.pagination import paginate

router = APIRouter(prefix="/dishes", tags=["Dishes"])


async def get_dish_or_404(session: AsyncSession, dish_id: uuid.UUID) -> Dish:
    result = await session.execute(
        select(Dish)
        .options(selectinload(Dish.moods))
        .where(Dish.id == dish_id, Dish.is_deleted.is_(False))
    )
    dish = result.scalar_one_or_none()
    if not dish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")
    return dish


def serialize_dish(dish: Dish) -> DishOut:
    return DishOut.model_validate(dish)


@router.get("/", response_model=PaginatedResponse[DishOut])
async def list_dishes(
    params: PaginationParams = Depends(),
    filters: DishFilterParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[DishOut]:
    stmt = (
        select(Dish)
        .options(selectinload(Dish.moods))
        .where(Dish.is_deleted.is_(False))
    )

    if filters.cuisine_id:
        stmt = stmt.where(Dish.cuisine_id == filters.cuisine_id)
    if filters.restaurant_id:
        stmt = stmt.where(Dish.restaurant_id == filters.restaurant_id)
    if filters.mood_id:
        stmt = stmt.join(Dish.moods).where(Mood.id == filters.mood_id)
    if filters.min_rating is not None:
        stmt = stmt.where(Dish.rating.isnot(None), Dish.rating >= filters.min_rating)
    if filters.max_price is not None:
        stmt = stmt.where(Dish.price.isnot(None), Dish.price <= filters.max_price)
    if filters.is_featured is not None:
        stmt = stmt.where(Dish.is_featured == filters.is_featured)

    if params.sort:
        for sort_field in params.sort.split(","):
            sort_field = sort_field.strip()
            if not sort_field:
                continue
            desc = sort_field.startswith("-")
            field_name = sort_field[1:] if desc else sort_field
            attr = getattr(Dish, field_name, None)
            if attr is None:
                continue
            stmt = stmt.order_by(attr.desc() if desc else attr.asc())
    else:
        stmt = stmt.order_by(Dish.rating.desc().nullslast(), Dish.name.asc())

    return await paginate(session, stmt, params, mapper=serialize_dish)


# IMPORTANT: Specific routes must come BEFORE parameterized routes like /{dish_id}
# Otherwise FastAPI will try to match "featured" and "top-rated" as UUIDs

@router.get("/featured", response_model=List[DishOut])
async def featured_dishes(
    limit: int = Query(default=10, gt=0, le=50),
    session: AsyncSession = Depends(get_db),
) -> List[DishOut]:
    stmt = (
        select(Dish)
        .options(selectinload(Dish.moods))
        .where(Dish.is_deleted.is_(False), Dish.is_featured.is_(True))
        .order_by(Dish.featured_week.desc().nullslast(), Dish.updated_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    dishes = result.scalars().all()
    return [serialize_dish(d) for d in dishes]


@router.get("/top-rated", response_model=List[DishOut])
async def top_rated_dishes(
    limit: int = Query(default=10, gt=0, le=50),
    session: AsyncSession = Depends(get_db),
) -> List[DishOut]:
    stmt = (
        select(Dish)
        .options(selectinload(Dish.moods))
        .where(Dish.is_deleted.is_(False), Dish.rating.isnot(None))
        .order_by(Dish.rating.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    dishes = result.scalars().all()
    return [serialize_dish(d) for d in dishes]


@router.get("/by-cuisine/{cuisine_id}", response_model=PaginatedResponse[DishOut])
async def dishes_by_cuisine(
    cuisine_id: uuid.UUID,
    params: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[DishOut]:
    stmt = (
        select(Dish)
        .options(selectinload(Dish.moods))
        .where(Dish.is_deleted.is_(False), Dish.cuisine_id == cuisine_id)
        .order_by(Dish.rating.desc().nullslast(), Dish.name.asc())
    )
    return await paginate(session, stmt, params, mapper=serialize_dish)


@router.get("/by-mood/{mood_id}", response_model=PaginatedResponse[DishOut])
async def dishes_by_mood(
    mood_id: uuid.UUID,
    params: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[DishOut]:
    stmt = (
        select(Dish)
        .join(Dish.moods)
        .options(selectinload(Dish.moods))
        .where(Dish.is_deleted.is_(False), Mood.id == mood_id)
        .order_by(Dish.rating.desc().nullslast(), Dish.name.asc())
    )
    return await paginate(session, stmt, params, mapper=serialize_dish)


@router.get("/{dish_id}", response_model=DishOut)
async def get_dish(dish_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> DishOut:
    dish = await get_dish_or_404(session, dish_id)
    return serialize_dish(dish)
