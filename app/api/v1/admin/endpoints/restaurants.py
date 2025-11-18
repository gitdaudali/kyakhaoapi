from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Restaurant
from app.schemas.restaurant import RestaurantCreate, RestaurantOut, RestaurantUpdate
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.utils.pagination import paginate
from app.api.v1.endpoints.restaurants import get_restaurant_or_404

router = APIRouter(prefix="/restaurants", tags=["Admin"])


@router.get("/")
async def list_restaurants(
    params: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """List all restaurants (admin view)."""
    try:
        stmt = select(Restaurant).where(Restaurant.is_deleted.is_(False))
        stmt = stmt.order_by(Restaurant.name.asc())
        
        result = await paginate(
            session,
            stmt,
            params,
            mapper=lambda obj: RestaurantOut.model_validate(obj),
        )
        
        return success_response(
            message="Restaurants retrieved successfully",
            data=result.model_dump()
        )
    except Exception as e:
        return error_response(
            message=f"Error retrieving restaurants: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{restaurant_id}")
async def get_restaurant(
    restaurant_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Get a specific restaurant by ID."""
    try:
        restaurant = await get_restaurant_or_404(session, restaurant_id)
        restaurant_out = RestaurantOut.model_validate(restaurant)
        return success_response(
            message="Restaurant retrieved successfully",
            data=restaurant_out.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Error retrieving restaurant: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    payload: RestaurantCreate,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        restaurant = Restaurant(**payload.dict())
        session.add(restaurant)
        await session.commit()
        await session.refresh(restaurant)
        
        restaurant_out = RestaurantOut.model_validate(restaurant)
        return success_response(
            message="Restaurant created successfully",
            data=restaurant_out.model_dump(),
            status_code=status.HTTP_201_CREATED
        )
    except IntegrityError as e:
        await session.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            return error_response(
                message=f"Restaurant with name '{payload.name}' already exists",
                status_code=status.HTTP_409_CONFLICT
            )
        return error_response(
            message="Database integrity error occurred",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error creating restaurant: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/{restaurant_id}")
async def update_restaurant(
    restaurant_id: uuid.UUID,
    payload: RestaurantUpdate,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        restaurant = await get_restaurant_or_404(session, restaurant_id)
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(restaurant, field, value)
        await session.commit()
        await session.refresh(restaurant)
        
        restaurant_out = RestaurantOut.model_validate(restaurant)
        return success_response(
            message="Restaurant updated successfully",
            data=restaurant_out.model_dump()
        )
    except IntegrityError as e:
        await session.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            name = payload.name if hasattr(payload, 'name') and payload.name else "this name"
            return error_response(
                message=f"Restaurant with name '{name}' already exists",
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
            message=f"Error updating restaurant: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{restaurant_id}")
async def delete_restaurant(
    restaurant_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        restaurant = await get_restaurant_or_404(session, restaurant_id)
        restaurant.is_deleted = True
        await session.commit()
        return success_response(
            message="Restaurant deleted successfully",
            data={"id": str(restaurant.id), "name": restaurant.name}
        )
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error deleting restaurant: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

