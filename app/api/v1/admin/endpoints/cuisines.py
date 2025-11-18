from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Cuisine
from app.schemas.cuisine import CuisineCreate, CuisineOut, CuisineUpdate
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.utils.pagination import paginate
from app.api.v1.endpoints.cuisines import get_cuisine_or_404

router = APIRouter(prefix="/cuisines", tags=["Admin"])


@router.get("/")
async def list_cuisines(
    params: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """List all cuisines (including soft-deleted for admin view)."""
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
async def get_cuisine(
    cuisine_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Get a specific cuisine by ID."""
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


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_cuisine(
    payload: CuisineCreate,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        cuisine = Cuisine(**payload.dict())
        session.add(cuisine)
        await session.commit()
        await session.refresh(cuisine)
        
        cuisine_out = CuisineOut.model_validate(cuisine)
        return success_response(
            message="Cuisine created successfully",
            data=cuisine_out.model_dump(),
            status_code=status.HTTP_201_CREATED
        )
    except IntegrityError as e:
        await session.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            return error_response(
                message=f"Cuisine with name '{payload.name}' already exists",
                status_code=status.HTTP_409_CONFLICT
            )
        return error_response(
            message="Database integrity error occurred",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error creating cuisine: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/{cuisine_id}")
async def update_cuisine(
    cuisine_id: uuid.UUID,
    payload: CuisineUpdate,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        cuisine = await get_cuisine_or_404(session, cuisine_id)
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(cuisine, field, value)
        await session.commit()
        await session.refresh(cuisine)
        
        cuisine_out = CuisineOut.model_validate(cuisine)
        return success_response(
            message="Cuisine updated successfully",
            data=cuisine_out.model_dump()
        )
    except IntegrityError as e:
        await session.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            name = payload.name if hasattr(payload, 'name') and payload.name else "this name"
            return error_response(
                message=f"Cuisine with name '{name}' already exists",
                status_code=status.HTTP_409_CONFLICT
            )
        return error_response(
            message="Database integrity error occurred",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error updating cuisine: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{cuisine_id}")
async def delete_cuisine(
    cuisine_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        cuisine = await get_cuisine_or_404(session, cuisine_id)
        cuisine.is_deleted = True
        await session.commit()
        return success_response(
            message="Cuisine deleted successfully",
            data={"id": str(cuisine.id), "name": cuisine.name}
        )
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error deleting cuisine: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

