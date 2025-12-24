from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.schemas.dish import DishCreate, DishUpdate
from app.schemas.pagination import PaginationParams
from app.services.dish_service import DishService
from app.api.v1.endpoints.dishes import serialize_dish
from app.utils.pagination import paginate
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.food import Dish

router = APIRouter(prefix="/dishes", tags=["Admin"])


@router.get("/")
async def list_dishes(
    admin_user: AdminUser,
    params: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """List all dishes (admin view)."""
    try:
        # Use service layer for business logic
        service = DishService(session)
        dishes = await service.list_dishes(
            limit=params.limit,
            offset=params.offset,
        )
        
        # Paginate results
        stmt = select(Dish).where(Dish.is_deleted.is_(False))
        stmt = stmt.options(selectinload(Dish.moods))
        stmt = stmt.order_by(Dish.name.asc())
        
        result = await paginate(
            session,
            stmt,
            params,
            mapper=serialize_dish,
        )
        
        return success_response(
            message="Dishes retrieved successfully",
            data=result.model_dump()
        )
    except Exception as e:
        return error_response(
            message=f"Error retrieving dishes: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{dish_id}")
async def get_dish(
    dish_id: uuid.UUID,
    admin_user: AdminUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Get a specific dish by ID."""
    try:
        # Use service layer - thin controller
        service = DishService(session)
        dish = await service.get_dish(dish_id)
        
        dish_out = serialize_dish(dish)
        return success_response(
            message="Dish retrieved successfully",
            data=dish_out
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Error retrieving dish: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_dish(
    payload: DishCreate,
    admin_user: AdminUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new dish (admin only)."""
    try:
        # Thin controller - business logic in service layer
        service = DishService(session)
        dish = await service.create_dish(payload)
        
        dish_out = serialize_dish(dish)
        return success_response(
            message="Dish created successfully",
            data=dish_out,
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Error creating dish: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/{dish_id}")
async def update_dish(
    dish_id: uuid.UUID,
    payload: DishUpdate,
    admin_user: AdminUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Update an existing dish (admin only)."""
    try:
        # Thin controller - business logic in service layer
        service = DishService(session)
        dish = await service.update_dish(dish_id, payload)
        
        dish_out = serialize_dish(dish)
        return success_response(
            message="Dish updated successfully",
            data=dish_out
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Error updating dish: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{dish_id}")
async def delete_dish(
    dish_id: uuid.UUID,
    admin_user: AdminUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Soft delete a dish (admin only)."""
    try:
        # Get dish first to include name in response
        service = DishService(session)
        dish = await service.get_dish(dish_id)
        
        # Soft delete
        deleted = await service.delete_dish(dish_id)
        
        if deleted:
            return success_response(
                message="Dish deleted successfully",
                data={"id": str(dish.id), "name": dish.name}
            )
        else:
            return error_response(
                message="Dish not found or already deleted",
                status_code=status.HTTP_404_NOT_FOUND
            )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Error deleting dish: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

