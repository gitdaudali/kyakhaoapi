"""Admin reviews endpoints."""
from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Dish, Review
from app.schemas.review import ReviewAdminOut
from app.schemas.pagination import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/reviews", tags=["Admin Reviews"])


async def update_dish_rating(session: AsyncSession, dish_id: uuid.UUID) -> None:
    """Calculate and update the average rating for a dish."""
    result = await session.execute(
        select(func.avg(Review.rating))
        .where(Review.dish_id == dish_id, Review.is_deleted.is_(False))
    )
    avg_rating = result.scalar()
    
    # Update dish rating
    dish_result = await session.execute(
        select(Dish).where(Dish.id == dish_id, Dish.is_deleted.is_(False))
    )
    dish = dish_result.scalar_one_or_none()
    if dish:
        dish.rating = float(avg_rating) if avg_rating else None
        await session.commit()


@router.get("/")
async def list_all_reviews(
    pagination: PaginationParams = Depends(),
    dish_id: uuid.UUID | None = Query(None, description="Filter by dish ID"),
    user_id: uuid.UUID | None = Query(None, description="Filter by user ID"),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """List all reviews (admin view) with optional filters."""
    try:
        # Build query
        query = select(Review).where(Review.is_deleted.is_(False))
        
        if dish_id:
            query = query.where(Review.dish_id == dish_id)
        if user_id:
            query = query.where(Review.user_id == user_id)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        query = query.order_by(Review.created_at.desc())
        query = query.offset(pagination.offset).limit(pagination.limit)
        
        # Execute query
        result = await session.execute(query)
        reviews = result.scalars().all()
        
        reviews_list = [
            ReviewAdminOut(
                id=review.id,
                user_id=review.user_id,
                dish_id=review.dish_id,
                rating=review.rating,
                title=review.title,
                comment=review.comment,
                visit_date=review.visit_date,
                spice_level=review.spice_level,
                delivery_time=review.delivery_time,
                companion_type=review.companion_type,
                photos=review.photos,  # JSON type returns List[str] directly
                created_at=review.created_at,
                updated_at=review.updated_at
            ).model_dump()
            for review in reviews
        ]
        
        paginated_response = PaginatedResponse(
            items=reviews_list,
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            total_pages=(total + pagination.limit - 1) // pagination.limit if pagination.limit > 0 else 0
        )
        
        return success_response(
            message="Reviews retrieved successfully",
            data=paginated_response.model_dump()
        )
        
    except Exception as e:
        return error_response(
            message=f"Error retrieving reviews: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{review_id}")
async def delete_review(
    review_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Delete any review (admin only)."""
    try:
        # Get review
        result = await session.execute(
            select(Review).where(
                Review.id == review_id,
                Review.is_deleted.is_(False)
            )
        )
        review = result.scalar_one_or_none()
        
        if not review:
            return error_response(
                message="Review not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Soft delete
        dish_id = review.dish_id
        review.is_deleted = True
        await session.commit()

        # Update dish average rating
        await update_dish_rating(session, dish_id)

        return success_response(
            message="Review deleted successfully",
            data=None
        )

    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error deleting review: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

