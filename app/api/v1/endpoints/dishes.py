from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.food import Cuisine, Dish, Mood, Restaurant
from app.schemas.dish import DishCreate, DishFilterParams, DishOut, DishUpdate
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.utils.pagination import paginate

router = APIRouter(prefix="/dishes", tags=["Dishes"])


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


async def get_moods_by_ids(session: AsyncSession, mood_ids: List[uuid.UUID]) -> List[Mood]:
    if not mood_ids:
        return []
    result = await session.execute(
        select(Mood).where(Mood.id.in_(mood_ids), Mood.is_deleted.is_(False))
    )
    moods = result.scalars().all()
    if len(moods) != len(set(mood_ids)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more moods not found")
    return moods


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


@router.post("/", response_model=DishOut, status_code=status.HTTP_201_CREATED)
async def create_dish(payload: DishCreate, session: AsyncSession = Depends(get_db)) -> DishOut:
    await ensure_related_entities(session, restaurant_id=payload.restaurant_id, cuisine_id=payload.cuisine_id)
    dish = Dish(**payload.dict(exclude={"mood_ids"}))
    if payload.mood_ids:
        dish.moods = await get_moods_by_ids(session, payload.mood_ids)
    session.add(dish)
    await session.commit()
    await session.refresh(dish)
    return serialize_dish(dish)


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
async def delete_dish(dish_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> Response:
    dish = await get_dish_or_404(session, dish_id)
    dish.is_deleted = True
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
