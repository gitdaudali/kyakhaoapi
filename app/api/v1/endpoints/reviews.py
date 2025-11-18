"""User reviews endpoints."""
from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Dish, Review
from app.schemas.review import ReviewCreate, ReviewListItem, ReviewOut, ReviewUpdate
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter(tags=["Reviews"])


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


@router.post("/dishes/{dish_id}/reviews", status_code=status.HTTP_201_CREATED)
async def create_review(
    dish_id: uuid.UUID,
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Add a review for a dish."""
    try:
        # Verify dish exists
        dish_result = await session.execute(
            select(Dish).where(Dish.id == dish_id, Dish.is_deleted.is_(False))
        )
        dish = dish_result.scalar_one_or_none()
        if not dish:
            return error_response(
                message="Dish not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Check if user already reviewed this dish
        existing_result = await session.execute(
            select(Review).where(
                Review.user_id == current_user.id,
                Review.dish_id == dish_id,
                Review.is_deleted.is_(False)
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            return error_response(
                message="You have already reviewed this dish. Use PUT to update your review.",
                status_code=status.HTTP_409_CONFLICT
            )

        # Create review (photos is now stored as JSON type, no conversion needed)
        review = Review(
            user_id=current_user.id,
            dish_id=dish_id,
            rating=payload.rating,
            title=payload.title,
            comment=payload.comment,
            visit_date=payload.visit_date,
            spice_level=payload.spice_level,
            delivery_time=payload.delivery_time,
            companion_type=payload.companion_type,
            photos=payload.photos  # JSON type handles List[str] automatically
        )
        session.add(review)
        await session.commit()
        await session.refresh(review)

        # Update dish average rating
        await update_dish_rating(session, dish_id)

        review_out = ReviewOut(
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
        )

        return success_response(
            message="Review created successfully",
            data=review_out.model_dump(),
            status_code=status.HTTP_201_CREATED
        )

    except IntegrityError as e:
        await session.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            return error_response(
                message="You have already reviewed this dish",
                status_code=status.HTTP_409_CONFLICT
            )
        return error_response(
            message="Database integrity error occurred",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error creating review: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/dishes/{dish_id}/reviews")
async def get_dish_reviews(
    dish_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Fetch all reviews for a dish."""
    try:
        # Verify dish exists
        dish_result = await session.execute(
            select(Dish).where(Dish.id == dish_id, Dish.is_deleted.is_(False))
        )
        dish = dish_result.scalar_one_or_none()
        if not dish:
            return error_response(
                message="Dish not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Get all reviews for the dish
        result = await session.execute(
            select(Review)
            .where(Review.dish_id == dish_id, Review.is_deleted.is_(False))
            .order_by(Review.created_at.desc())
        )
        reviews = result.scalars().all()

        reviews_list = [
            ReviewListItem(
                id=review.id,
                user_id=review.user_id,
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

        return success_response(
            message="Reviews retrieved successfully",
            data={
                "dish_id": str(dish_id),
                "total_reviews": len(reviews_list),
                "reviews": reviews_list
            }
        )

    except Exception as e:
        return error_response(
            message=f"Error retrieving reviews: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/reviews/{review_id}")
async def update_review(
    review_id: uuid.UUID,
    payload: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Update a review. Users can only update their own reviews."""
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

        # Check if user owns this review
        if review.user_id != current_user.id:
            return error_response(
                message="You can only update your own reviews",
                status_code=status.HTTP_403_FORBIDDEN
            )

        # Update review fields
        if payload.rating is not None:
            review.rating = payload.rating
        if payload.title is not None:
            review.title = payload.title
        if payload.comment is not None:
            review.comment = payload.comment
        if payload.visit_date is not None:
            review.visit_date = payload.visit_date
        if payload.spice_level is not None:
            review.spice_level = payload.spice_level
        if payload.delivery_time is not None:
            review.delivery_time = payload.delivery_time
        if payload.companion_type is not None:
            review.companion_type = payload.companion_type
        if payload.photos is not None:
            review.photos = payload.photos  # JSON type handles List[str] automatically

        await session.commit()
        await session.refresh(review)

        # Update dish average rating
        await update_dish_rating(session, review.dish_id)

        review_out = ReviewOut(
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
        )

        return success_response(
            message="Review updated successfully",
            data=review_out.model_dump()
        )

    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error updating review: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/reviews/{review_id}")
async def delete_review(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Delete a review. Users can only delete their own reviews."""
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

        # Check if user owns this review
        if review.user_id != current_user.id:
            return error_response(
                message="You can only delete your own reviews",
                status_code=status.HTTP_403_FORBIDDEN
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

