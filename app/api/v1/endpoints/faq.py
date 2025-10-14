from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.core.database import get_db
from app.models.faq import FAQ
from app.schemas.faq import (
    FAQListResponse,
    FAQQueryParams,
    FAQResponse,
)
from app.utils.content_utils import calculate_pagination_info

router = APIRouter()

FAQ_NOT_FOUND = "FAQ not found"


@router.get("/", response_model=FAQListResponse)
async def get_faqs(
    query_params: FAQQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get paginated list of active FAQs for users.
    """
    try:
        # Build query - only active, non-deleted FAQs
        query = select(FAQ).where(
            and_(FAQ.is_active == True, FAQ.is_deleted == False)
        )
        
        # Apply filters
        if query_params.search:
            search_filter = or_(
                FAQ.question.ilike(f"%{query_params.search}%"),
                FAQ.answer.ilike(f"%{query_params.search}%"),
                FAQ.category.ilike(f"%{query_params.search}%"),
            )
            query = query.where(search_filter)
        
        if query_params.category:
            query = query.where(FAQ.category == query_params.category)
        
        if query_params.featured_only:
            query = query.where(FAQ.is_featured == True)
        
        # Apply sorting - default by sort_order, then by created_at
        if query_params.sort_by == "sort_order":
            if query_params.sort_order == "desc":
                query = query.order_by(FAQ.sort_order.desc(), FAQ.created_at.desc())
            else:
                query = query.order_by(FAQ.sort_order.asc(), FAQ.created_at.asc())
        else:
            sort_column = getattr(FAQ, query_params.sort_by, FAQ.created_at)
            if query_params.sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        
        # Get total count
        count_query = select(func.count(FAQ.id)).where(
            and_(FAQ.is_active == True, FAQ.is_deleted == False)
        )
        if query_params.search:
            count_query = count_query.where(search_filter)
        if query_params.category:
            count_query = count_query.where(FAQ.category == query_params.category)
        if query_params.featured_only:
            count_query = count_query.where(FAQ.is_featured == True)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (query_params.page - 1) * query_params.size
        query = query.offset(offset).limit(query_params.size)
        
        # Execute query
        result = await db.execute(query)
        faqs = result.scalars().all()
        
        # Calculate pagination info
        pagination_info = calculate_pagination_info(
            query_params.page, query_params.size, total
        )
        
        return FAQListResponse(
            items=[FAQResponse.model_validate(faq) for faq in faqs],
            total=pagination_info["total"],
            page=pagination_info["page"],
            size=pagination_info["size"],
            pages=pagination_info["pages"],
            has_next=pagination_info["has_next"],
            has_prev=pagination_info["has_prev"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving FAQ list: {str(e)}",
        )


@router.get("/{faq_id}", response_model=FAQResponse)
async def get_faq(
    faq_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get FAQ by ID for users.
    """
    try:
        query = select(FAQ).where(
            and_(
                FAQ.id == faq_id,
                FAQ.is_active == True,
                FAQ.is_deleted == False
            )
        )
        result = await db.execute(query)
        faq = result.scalar_one_or_none()
        
        if not faq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=FAQ_NOT_FOUND,
            )
        
        # Increment view count
        faq.view_count += 1
        await db.commit()
        
        return FAQResponse.model_validate(faq)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving FAQ: {str(e)}",
        )


@router.get("/categories/list")
async def get_faq_categories(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get list of FAQ categories.
    """
    try:
        query = select(FAQ.category).where(
            and_(
                FAQ.is_active == True,
                FAQ.is_deleted == False,
                FAQ.category.isnot(None)
            )
        ).distinct()
        
        result = await db.execute(query)
        categories = [row[0] for row in result.fetchall() if row[0]]
        
        return {"categories": sorted(categories)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving FAQ categories: {str(e)}",
        )


@router.get("/featured/list", response_model=FAQListResponse)
async def get_featured_faqs(
    query_params: FAQQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get list of featured FAQs.
    """
    try:
        # Build query - only featured, active, non-deleted FAQs
        query = select(FAQ).where(
            and_(
                FAQ.is_featured == True,
                FAQ.is_active == True,
                FAQ.is_deleted == False
            )
        )
        
        # Apply search filter if provided
        if query_params.search:
            search_filter = or_(
                FAQ.question.ilike(f"%{query_params.search}%"),
                FAQ.answer.ilike(f"%{query_params.search}%"),
                FAQ.category.ilike(f"%{query_params.search}%"),
            )
            query = query.where(search_filter)
        
        # Apply category filter if provided
        if query_params.category:
            query = query.where(FAQ.category == query_params.category)
        
        # Sort by sort_order, then by created_at
        query = query.order_by(FAQ.sort_order.asc(), FAQ.created_at.asc())
        
        # Get total count
        count_query = select(func.count(FAQ.id)).where(
            and_(
                FAQ.is_featured == True,
                FAQ.is_active == True,
                FAQ.is_deleted == False
            )
        )
        if query_params.search:
            count_query = count_query.where(search_filter)
        if query_params.category:
            count_query = count_query.where(FAQ.category == query_params.category)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (query_params.page - 1) * query_params.size
        query = query.offset(offset).limit(query_params.size)
        
        # Execute query
        result = await db.execute(query)
        faqs = result.scalars().all()
        
        # Calculate pagination info
        pagination_info = calculate_pagination_info(
            query_params.page, query_params.size, total
        )
        
        return FAQListResponse(
            items=[FAQResponse.model_validate(faq) for faq in faqs],
            total=pagination_info["total"],
            page=pagination_info["page"],
            size=pagination_info["size"],
            pages=pagination_info["pages"],
            has_next=pagination_info["has_next"],
            has_prev=pagination_info["has_prev"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving featured FAQs: {str(e)}",
        )
