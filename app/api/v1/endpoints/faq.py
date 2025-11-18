"""User FAQ endpoints."""
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.schemas.faq import FAQResponse, FAQListResponse
from app.utils.faq_utils import (
    get_faq_by_id_or_404,
    get_published_faqs,
)

router = APIRouter(tags=["FAQs"])


@router.get("/")
async def get_all_faqs(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
) -> Any:
    """Get all published FAQs."""
    try:
        faqs, total = await get_published_faqs(
            db, skip=skip, limit=limit, category=category
        )

        faq_list = FAQListResponse(
            faqs=[FAQResponse.model_validate(faq) for faq in faqs],
            total=total,
        )
        return success_response(
            message="FAQs retrieved successfully",
            data=faq_list.model_dump()
        )

    except Exception as e:
        return error_response(
            message=f"Error retrieving FAQs: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{faq_id}")
async def get_faq(
    faq_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """View specific FAQ (optional)."""
    try:
        # Get FAQ and verify it's published
        faq = await get_faq_by_id_or_404(db, faq_id)

        if not faq.is_published:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FAQ not found",
            )

        faq_response = FAQResponse.model_validate(faq)
        return success_response(
            message="FAQ retrieved successfully",
            data=faq_response.model_dump()
        )

    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Error retrieving FAQ: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

