from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.food import Cuisine
from app.schemas.cuisine import CuisineCreate, CuisineOut, CuisineUpdate
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.utils.pagination import paginate

router = APIRouter(prefix="/cuisines", tags=["Cuisines"])


async def get_cuisine_or_404(session: AsyncSession, cuisine_id: uuid.UUID) -> Cuisine:
    result = await session.execute(
        select(Cuisine).where(Cuisine.id == cuisine_id, Cuisine.is_deleted.is_(False))
    )
    cuisine = result.scalar_one_or_none()
    if not cuisine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuisine not found")
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


@router.post("/", response_model=CuisineOut, status_code=status.HTTP_201_CREATED)
async def create_cuisine(
    payload: CuisineCreate,
    session: AsyncSession = Depends(get_db),
) -> CuisineOut:
    cuisine = Cuisine(**payload.dict())
    session.add(cuisine)
    await session.commit()
    await session.refresh(cuisine)
    return CuisineOut.model_validate(cuisine)


@router.get("/{cuisine_id}", response_model=CuisineOut)
async def get_cuisine(cuisine_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> CuisineOut:
    cuisine = await get_cuisine_or_404(session, cuisine_id)
    return CuisineOut.model_validate(cuisine)


@router.put("/{cuisine_id}", response_model=CuisineOut)
async def update_cuisine(
    cuisine_id: uuid.UUID,
    payload: CuisineUpdate,
    session: AsyncSession = Depends(get_db),
) -> CuisineOut:
    cuisine = await get_cuisine_or_404(session, cuisine_id)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(cuisine, field, value)
    await session.commit()
    await session.refresh(cuisine)
    return CuisineOut.model_validate(cuisine)


@router.delete("/{cuisine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cuisine(cuisine_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> Response:
    cuisine = await get_cuisine_or_404(session, cuisine_id)
    cuisine.is_deleted = True
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
