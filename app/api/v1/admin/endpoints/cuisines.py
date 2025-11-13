from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.food import Cuisine
from app.schemas.cuisine import CuisineCreate, CuisineOut, CuisineUpdate
from app.api.v1.endpoints.cuisines import get_cuisine_or_404

router = APIRouter(prefix="/cuisines", tags=["Admin"])


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
async def delete_cuisine(
    cuisine_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Response:
    cuisine = await get_cuisine_or_404(session, cuisine_id)
    cuisine.is_deleted = True
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

