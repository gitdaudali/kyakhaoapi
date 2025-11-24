from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.food import Cuisine
from app.schemas.cuisine import CuisineOut
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.utils.pagination import paginate

router = APIRouter(prefix="/cuisines", tags=["User Cuisines"])


async def get_cuisine_or_404(session: AsyncSession, cuisine_id: uuid.UUID) -> Cuisine:
    result = await session.execute(
        select(Cuisine).where(Cuisine.id == cuisine_id, Cuisine.is_deleted.is_(False))
    )
    cuisine = result.scalar_one_or_none()
    if not cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")
    return cuisine


@router.get("/", response_model=PaginatedResponse[CuisineOut])
async def list_cuisines(
    params: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[CuisineOut]:
    stmt = select(Cuisine).where(Cuisine.is_deleted.is_(False))
    stmt = stmt.order_by(Cuisine.name.asc())

    return await paginate(
        session,
        stmt,
        params,
        mapper=lambda obj: CuisineOut.model_validate(obj),
    )


@router.get("/{cuisine_id}", response_model=CuisineOut)
async def get_cuisine(cuisine_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> CuisineOut:
    cuisine = await get_cuisine_or_404(session, cuisine_id)
    return CuisineOut.model_validate(cuisine)
