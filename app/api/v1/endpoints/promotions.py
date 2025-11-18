"""User promotions endpoints."""
from datetime import date
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.promotion import Promotion
from app.schemas.promotion import PromotionApply, PromotionApplyResponse, PromotionOut

router = APIRouter(tags=["Promotions"])


@router.get("/active")
async def get_active_promotions(
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Get all currently active promotions."""
    try:
        today = date.today()
        
        # Query active promotions (start_date <= today <= end_date)
        result = await session.execute(
            select(Promotion)
            .where(
                and_(
                    Promotion.start_date <= today,
                    Promotion.end_date >= today,
                    Promotion.is_deleted.is_(False)
                )
            )
            .order_by(Promotion.created_at.desc())
        )
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
        
        return success_response(
            message="Active promotions retrieved successfully",
            data=promotions_list
        )
        
    except Exception as e:
        return error_response(
            message=f"Error retrieving active promotions: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/apply")
async def apply_promo_code(
    payload: PromotionApply,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Apply a promo code to an order."""
    try:
        # Find promotion by promo code
        result = await session.execute(
            select(Promotion).where(
                Promotion.promo_code == payload.promo_code.upper(),
                Promotion.is_deleted.is_(False)
            )
        )
        promotion = result.scalar_one_or_none()
        
        if not promotion:
            return error_response(
                message="Invalid promo code",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Validate promotion is active
        today = date.today()
        if promotion.start_date > today or promotion.end_date < today:
            return error_response(
                message="This promo code is not currently active",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate minimum order amount
        if payload.order_amount < float(promotion.minimum_order_amount):
            return error_response(
                message=f"Minimum order amount of {promotion.minimum_order_amount} is required. Your order amount is {payload.order_amount}.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate applicable dish IDs if promotion is restricted
        if promotion.applicable_dish_ids is not None and payload.dish_ids:
            # Convert string UUIDs from DB to UUID objects for comparison
            promo_dish_ids = set([UUID(dish_id) for dish_id in promotion.applicable_dish_ids])
            order_dish_ids = set(payload.dish_ids)
            if not promo_dish_ids.intersection(order_dish_ids):
                return error_response(
                    message="This promo code does not apply to the selected dishes",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # Calculate discount
        original_amount = payload.order_amount
        discount_amount = 0.0
        
        if promotion.discount_type == "percentage":
            discount_amount = (original_amount * float(promotion.value)) / 100
        elif promotion.discount_type == "fixed":
            discount_amount = float(promotion.value)
            # Ensure discount doesn't exceed order amount
            if discount_amount > original_amount:
                discount_amount = original_amount
        
        final_amount = original_amount - discount_amount
        
        response = PromotionApplyResponse(
            original_amount=original_amount,
            discount_amount=round(discount_amount, 2),
            final_amount=round(final_amount, 2),
            message="Promo applied successfully"
        )
        
        return success_response(
            message="Promo applied successfully",
            data=response.model_dump()
        )
        
    except Exception as e:
        return error_response(
            message=f"Error applying promo code: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

