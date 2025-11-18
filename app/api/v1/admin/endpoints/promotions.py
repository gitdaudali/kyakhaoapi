"""Admin promotions endpoints."""
from datetime import date
from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.promotion import Promotion
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.promotion import PromotionCreate, PromotionOut, PromotionUpdate
from uuid import UUID

router = APIRouter(prefix="/promotions", tags=["Admin Promotions"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_promotion(
    payload: PromotionCreate,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new promotion."""
    try:
        # Validate dates
        if payload.end_date <= payload.start_date:
            return error_response(
                message="end_date must be after start_date",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate percentage discount
        if payload.discount_type == "percentage" and payload.value > 100:
            return error_response(
                message="Percentage discount cannot exceed 100",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Convert UUIDs to strings for JSON storage
        applicable_dish_ids = None
        if payload.applicable_dish_ids:
            applicable_dish_ids = [str(dish_id) for dish_id in payload.applicable_dish_ids]
        
        # Create promotion (promo_code is already normalized to uppercase in schema)
        promotion = Promotion(
            title=payload.title,
            description=payload.description,
            promo_code=payload.promo_code,  # Already normalized to uppercase in schema
            discount_type=payload.discount_type,
            value=payload.value,
            start_date=payload.start_date,
            end_date=payload.end_date,
            minimum_order_amount=payload.minimum_order_amount,
            applicable_dish_ids=applicable_dish_ids,
        )
        session.add(promotion)
        await session.commit()
        await session.refresh(promotion)
        
        # Convert string UUIDs back to UUID objects for response
        applicable_dish_ids_out = None
        if promotion.applicable_dish_ids:
            applicable_dish_ids_out = [UUID(dish_id) for dish_id in promotion.applicable_dish_ids]
        
        promotion_out = PromotionOut(
            id=promotion.id,
            title=promotion.title,
            description=promotion.description,
            promo_code=promotion.promo_code,
            discount_type=promotion.discount_type,
            value=float(promotion.value),
            start_date=promotion.start_date,
            end_date=promotion.end_date,
            minimum_order_amount=float(promotion.minimum_order_amount),
            applicable_dish_ids=applicable_dish_ids_out,
            created_at=promotion.created_at,
            updated_at=promotion.updated_at,
        )
        
        return success_response(
            message="Promotion created successfully",
            data=promotion_out.model_dump(),
            status_code=status.HTTP_201_CREATED
        )
        
    except IntegrityError as e:
        await session.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            return error_response(
                message="Promo code already exists",
                status_code=status.HTTP_409_CONFLICT
            )
        return error_response(
            message="Database integrity error occurred",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error creating promotion: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/")
async def list_all_promotions(
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """List all promotions with pagination."""
    try:
        # Build query
        query = select(Promotion).where(Promotion.is_deleted.is_(False))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        query = query.order_by(Promotion.created_at.desc())
        query = query.offset(pagination.offset).limit(pagination.limit)
        
        # Execute query
        result = await session.execute(query)
        promotions = result.scalars().all()
        
        promotions_list = []
        for promo in promotions:
            # Convert string UUIDs back to UUID objects for response
            applicable_dish_ids_out = None
            if promo.applicable_dish_ids:
                applicable_dish_ids_out = [UUID(dish_id) for dish_id in promo.applicable_dish_ids]
            
            promotions_list.append(
                PromotionOut(
                    id=promo.id,
                    title=promo.title,
                    description=promo.description,
                    promo_code=promo.promo_code,
                    discount_type=promo.discount_type,
                    value=float(promo.value),
                    start_date=promo.start_date,
                    end_date=promo.end_date,
                    minimum_order_amount=float(promo.minimum_order_amount),
                    applicable_dish_ids=applicable_dish_ids_out,
                    created_at=promo.created_at,
                    updated_at=promo.updated_at,
                ).model_dump()
            )
        
        paginated_response = PaginatedResponse(
            items=promotions_list,
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            total_pages=(total + pagination.limit - 1) // pagination.limit if pagination.limit > 0 else 0
        )
        
        return success_response(
            message="Promotions retrieved successfully",
            data=paginated_response.model_dump()
        )
        
    except Exception as e:
        return error_response(
            message=f"Error retrieving promotions: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{promotion_id}")
async def get_promotion(
    promotion_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Get a promotion by ID."""
    try:
        result = await session.execute(
            select(Promotion).where(
                Promotion.id == promotion_id,
                Promotion.is_deleted.is_(False)
            )
        )
        promotion = result.scalar_one_or_none()
        
        if not promotion:
            return error_response(
                message="Promotion not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Convert string UUIDs back to UUID objects for response
        applicable_dish_ids_out = None
        if promotion.applicable_dish_ids:
            applicable_dish_ids_out = [UUID(dish_id) for dish_id in promotion.applicable_dish_ids]
        
        promotion_out = PromotionOut(
            id=promotion.id,
            title=promotion.title,
            description=promotion.description,
            promo_code=promotion.promo_code,
            discount_type=promotion.discount_type,
            value=float(promotion.value),
            start_date=promotion.start_date,
            end_date=promotion.end_date,
            minimum_order_amount=float(promotion.minimum_order_amount),
            applicable_dish_ids=applicable_dish_ids_out,
            created_at=promotion.created_at,
            updated_at=promotion.updated_at,
        )
        
        return success_response(
            message="Promotion retrieved successfully",
            data=promotion_out.model_dump()
        )
        
    except Exception as e:
        return error_response(
            message=f"Error retrieving promotion: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/{promotion_id}")
async def update_promotion(
    promotion_id: uuid.UUID,
    payload: PromotionUpdate,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Update a promotion."""
    try:
        # Get promotion
        result = await session.execute(
            select(Promotion).where(
                Promotion.id == promotion_id,
                Promotion.is_deleted.is_(False)
            )
        )
        promotion = result.scalar_one_or_none()
        
        if not promotion:
            return error_response(
                message="Promotion not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Get update data - only fields that were explicitly provided
        # exclude_unset=True means fields not in the request are ignored
        # exclude_none=False means None values are included (they mean "keep existing")
        update_data = payload.model_dump(exclude_unset=True, exclude_none=False)
        
        # Validate dates if dates are being updated
        if "start_date" in update_data or "end_date" in update_data:
            # Get start_date: use update value if provided and not None, otherwise use existing
            if "start_date" in update_data:
                start_date = update_data["start_date"] if update_data["start_date"] is not None else promotion.start_date
            else:
                start_date = promotion.start_date
            
            # Get end_date: use update value if provided and not None, otherwise use existing
            if "end_date" in update_data:
                end_date = update_data["end_date"] if update_data["end_date"] is not None else promotion.end_date
            else:
                end_date = promotion.end_date
            
            # Only validate if both dates are not None
            if start_date is not None and end_date is not None:
                if end_date <= start_date:
                    return error_response(
                        message="end_date must be after start_date",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
        
        # Validate percentage discount if discount fields are being updated
        if "discount_type" in update_data or "value" in update_data:
            discount_type = update_data.get("discount_type") if "discount_type" in update_data else promotion.discount_type
            value = update_data.get("value") if "value" in update_data else float(promotion.value)
            if discount_type == "percentage" and value > 100:
                return error_response(
                    message="Percentage discount cannot exceed 100",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # Handle applicable_dish_ids separately (convert UUIDs to strings)
        if "applicable_dish_ids" in update_data and update_data["applicable_dish_ids"] is not None:
            update_data["applicable_dish_ids"] = [str(dish_id) for dish_id in update_data["applicable_dish_ids"]]
        
        # Update only non-None fields (None values mean "keep existing value")
        # Fields not in update_data are not updated (exclude_unset=True handles this)
        for field, value in update_data.items():
            if value is not None:
                setattr(promotion, field, value)
        
        await session.commit()
        await session.refresh(promotion)
        
        # Convert string UUIDs back to UUID objects for response
        applicable_dish_ids_out = None
        if promotion.applicable_dish_ids:
            applicable_dish_ids_out = [UUID(dish_id) for dish_id in promotion.applicable_dish_ids]
        
        promotion_out = PromotionOut(
            id=promotion.id,
            title=promotion.title,
            description=promotion.description,
            promo_code=promotion.promo_code,
            discount_type=promotion.discount_type,
            value=float(promotion.value),
            start_date=promotion.start_date,
            end_date=promotion.end_date,
            minimum_order_amount=float(promotion.minimum_order_amount),
            applicable_dish_ids=applicable_dish_ids_out,
            created_at=promotion.created_at,
            updated_at=promotion.updated_at,
        )
        
        return success_response(
            message="Promotion updated successfully",
            data=promotion_out.model_dump()
        )
        
    except IntegrityError as e:
        await session.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            return error_response(
                message="Promo code already exists",
                status_code=status.HTTP_409_CONFLICT
            )
        return error_response(
            message="Database integrity error occurred",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error updating promotion: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{promotion_id}")
async def delete_promotion(
    promotion_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Delete a promotion (soft delete)."""
    try:
        result = await session.execute(
            select(Promotion).where(
                Promotion.id == promotion_id,
                Promotion.is_deleted.is_(False)
            )
        )
        promotion = result.scalar_one_or_none()
        
        if not promotion:
            return error_response(
                message="Promotion not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Soft delete
        promotion.is_deleted = True
        await session.commit()
        
        return success_response(
            message="Promotion deleted successfully",
            data=None
        )
        
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error deleting promotion: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

