"""Admin FAQ management endpoints."""
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.admin_deps import AdminUser
from app.core.response_handler import success_response
from app.models.faq import FAQ
from app.schemas.faq import FAQCreate, FAQUpdate, FAQResponse, FAQListResponse
from app.utils.faq_utils import (
    get_all_faqs,
    get_faq_by_id_or_404,
    get_faq_by_question,
    soft_delete_faq,
)

router = APIRouter()
security = HTTPBearer()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_faq(
    faq_data: FAQCreate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new FAQ."""
    try:
        # Check if FAQ with same question already exists
        existing_faq = await get_faq_by_question(db, faq_data.question)
        if existing_faq:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FAQ with this question already exists",
            )

        db_faq = FAQ(
            question=faq_data.question,
            answer=faq_data.answer,
            category=faq_data.category,
            is_published=faq_data.is_published,
            order=faq_data.order,
        )
        db.add(db_faq)
        await db.commit()
        await db.refresh(db_faq)

        faq_response = FAQResponse.model_validate(db_faq)
        return success_response(
            message="FAQ created successfully",
            data=faq_response.model_dump(),
            status_code=status.HTTP_201_CREATED,
            use_body=True
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        # Check if it's a unique constraint violation
        if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FAQ with this question already exists",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating FAQ: {str(e)}",
        )


@router.get("/")
async def list_faqs(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """View all FAQs (for dashboard)."""
    try:
        faqs, total = await get_all_faqs(db, skip=skip, limit=limit)

        faq_list = FAQListResponse(
            faqs=[FAQResponse.model_validate(faq) for faq in faqs],
            total=total,
        )
        return success_response(
            message="FAQs retrieved successfully",
            data=faq_list.model_dump(),
            use_body=True
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving FAQs: {str(e)}",
        )


@router.get("/{faq_id}")
async def get_faq(
    faq_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get specific FAQ."""
    try:
        faq = await get_faq_by_id_or_404(db, faq_id)
        faq_response = FAQResponse.model_validate(faq)
        return success_response(
            message="FAQ retrieved successfully",
            data=faq_response.model_dump(),
            use_body=True
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving FAQ: {str(e)}",
        )


@router.put("/{faq_id}")
async def update_faq(
    faq_id: UUID,
    faq_data: FAQUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update FAQ."""
    try:
        faq = await get_faq_by_id_or_404(db, faq_id)

        # Update fields if provided (exclude None values except for fields that can be None)
        update_data = faq_data.model_dump(exclude_unset=True, exclude_none=False)
        
        # Filter out None values for required fields (question, answer)
        # But allow None for optional fields (category can be None)
        for field, value in update_data.items():
            # Skip None values for required fields
            if field in ['question', 'answer'] and value is None:
                continue
            # Allow None for category (it's optional)
            if field == 'category' and value is None:
                setattr(faq, field, None)
            # For other fields, only update if value is not None
            elif value is not None:
                setattr(faq, field, value)

        await db.commit()
        await db.refresh(faq)

        faq_response = FAQResponse.model_validate(faq)
        return success_response(
            message="FAQ updated successfully",
            data=faq_response.model_dump(),
            use_body=True
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        # Check if it's a unique constraint violation (for question updates)
        if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FAQ with this question already exists",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating FAQ: {str(e)}",
        )


@router.delete("/{faq_id}")
async def delete_faq(
    faq_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
):
    """Delete FAQ (soft delete)."""
    try:
        faq = await soft_delete_faq(db, faq_id)
        await db.commit()
        
        return success_response(
            message="FAQ deleted successfully",
            data={"id": str(faq.id), "question": faq.question},
            use_body=True
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting FAQ: {str(e)}",
        )

