from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Cuisine
from app.schemas.cuisine import CuisineOut
from app.schemas.pagination import PaginationParams
from app.utils.pagination import paginate

router = APIRouter(prefix="/cuisines", tags=["Cuisines"])


async def get_cuisine_or_404(session: AsyncSession, cuisine_id: uuid.UUID) -> Cuisine:
    result = await session.execute(
        select(Cuisine).where(Cuisine.id == cuisine_id, Cuisine.is_deleted.is_(False))
    )
    cuisine = result.scalar_one_or_none()
    if not cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")
    return cuisine


@router.get("/")
async def list_cuisines(
    params: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        stmt = select(Cuisine).where(Cuisine.is_deleted.is_(False))
        stmt = stmt.order_by(Cuisine.name.asc())

        result = await paginate(
            session,
            stmt,
            params,
            mapper=lambda obj: CuisineOut.model_validate(obj),
        )
        
        return success_response(
            message="Cuisines retrieved successfully",
            data=result.model_dump()
        )
    except Exception as e:
        return error_response(
            message=f"Error retrieving cuisines: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{cuisine_id}")
async def get_cuisine(cuisine_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> Any:
    try:
        cuisine = await get_cuisine_or_404(session, cuisine_id)
        cuisine_out = CuisineOut.model_validate(cuisine)
        return success_response(
            message="Cuisine retrieved successfully",
            data=cuisine_out.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Error retrieving cuisine: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
