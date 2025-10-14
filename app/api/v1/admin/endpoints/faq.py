from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.core.messages import (
    CONTENT_NOT_FOUND,
    CONTENT_CREATED,
    CONTENT_UPDATED,
    CONTENT_DELETED,
)
from app.models.faq import FAQ
from app.schemas.admin import (
    FAQAdminCreate,
    FAQAdminListResponse,
    FAQAdminQueryParams,
    FAQAdminResponse,
    FAQAdminUpdate,
)
from app.utils.content_utils import calculate_pagination_info

router = APIRouter()

# Custom messages for FAQ
FAQ_CREATED = "FAQ created successfully"
FAQ_UPDATED = "FAQ updated successfully"
FAQ_DELETED = "FAQ deleted successfully"
FAQ_NOT_FOUND = "FAQ not found"


@router.post("/", response_model=FAQAdminResponse)
async def create_faq_admin(
    current_user: AdminUser,
    faq_data: FAQAdminCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new FAQ (Admin only).
    """
    try:
        # Create FAQ instance
        faq = FAQ(
            question=faq_data.question,
            answer=faq_data.answer,
            category=faq_data.category,
            is_active=faq_data.is_active,
            is_featured=faq_data.is_featured,
            sort_order=faq_data.sort_order,
        )
        
        db.add(faq)
        await db.commit()
        await db.refresh(faq)
        
        return FAQAdminResponse.model_validate(faq)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating FAQ: {str(e)}",
        )


@router.get("/", response_model=FAQAdminListResponse)
async def get_faqs_admin(
    current_user: AdminUser,
    query_params: FAQAdminQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get paginated list of FAQs for admin.
    """
    try:
        # Build query
        query = select(FAQ).where(FAQ.is_deleted == False)
        
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
        
        if query_params.is_active is not None:
            query = query.where(FAQ.is_active == query_params.is_active)
        
        if query_params.is_featured is not None:
            query = query.where(FAQ.is_featured == query_params.is_featured)
        
        # Apply sorting
        sort_column = getattr(FAQ, query_params.sort_by, FAQ.created_at)
        if query_params.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Get total count
        count_query = select(func.count(FAQ.id)).where(FAQ.is_deleted == False)
        if query_params.search:
            count_query = count_query.where(search_filter)
        if query_params.category:
            count_query = count_query.where(FAQ.category == query_params.category)
        if query_params.is_active is not None:
            count_query = count_query.where(FAQ.is_active == query_params.is_active)
        if query_params.is_featured is not None:
            count_query = count_query.where(FAQ.is_featured == query_params.is_featured)
        
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
        
        return FAQAdminListResponse(
            items=[FAQAdminResponse.model_validate(faq) for faq in faqs],
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


@router.get("/{faq_id}", response_model=FAQAdminResponse)
async def get_faq_admin(
    faq_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get FAQ by ID for admin.
    """
    try:
        query = select(FAQ).where(and_(FAQ.id == faq_id, FAQ.is_deleted == False))
        result = await db.execute(query)
        faq = result.scalar_one_or_none()
        
        if not faq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=FAQ_NOT_FOUND,
            )
        
        return FAQAdminResponse.model_validate(faq)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving FAQ: {str(e)}",
        )


@router.put("/{faq_id}", response_model=FAQAdminResponse)
async def update_faq_admin(
    faq_id: UUID,
    current_user: AdminUser,
    faq_data: FAQAdminUpdate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update FAQ (Admin only).
    """
    try:
        # Get existing FAQ
        query = select(FAQ).where(and_(FAQ.id == faq_id, FAQ.is_deleted == False))
        result = await db.execute(query)
        faq = result.scalar_one_or_none()
        
        if not faq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=FAQ_NOT_FOUND,
            )
        
        # Update fields
        update_data = faq_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(faq, field, value)
        
        await db.commit()
        await db.refresh(faq)
        
        return FAQAdminResponse.model_validate(faq)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating FAQ: {str(e)}",
        )


@router.delete("/{faq_id}")
async def delete_faq_admin(
    faq_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete FAQ (Admin only).
    """
    try:
        # Get existing FAQ
        query = select(FAQ).where(and_(FAQ.id == faq_id, FAQ.is_deleted == False))
        result = await db.execute(query)
        faq = result.scalar_one_or_none()
        
        if not faq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=FAQ_NOT_FOUND,
            )
        
        # Soft delete
        faq.is_deleted = True
        await db.commit()
        
        return {"message": FAQ_DELETED}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting FAQ: {str(e)}",
        )


@router.patch("/{faq_id}/toggle-active")
async def toggle_faq_active_admin(
    faq_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Toggle FAQ active status (Admin only).
    """
    try:
        # Get existing FAQ
        query = select(FAQ).where(and_(FAQ.id == faq_id, FAQ.is_deleted == False))
        result = await db.execute(query)
        faq = result.scalar_one_or_none()
        
        if not faq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=FAQ_NOT_FOUND,
            )
        
        # Toggle active status
        faq.is_active = not faq.is_active
        await db.commit()
        await db.refresh(faq)
        
        message = "FAQ activated" if faq.is_active else "FAQ deactivated"
        
        return {
            "message": message,
            "faq": FAQAdminResponse.model_validate(faq),
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling FAQ active status: {str(e)}",
        )


@router.patch("/{faq_id}/toggle-featured")
async def toggle_faq_featured_admin(
    faq_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Toggle FAQ featured status (Admin only).
    """
    try:
        # Get existing FAQ
        query = select(FAQ).where(and_(FAQ.id == faq_id, FAQ.is_deleted == False))
        result = await db.execute(query)
        faq = result.scalar_one_or_none()
        
        if not faq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=FAQ_NOT_FOUND,
            )
        
        # Toggle featured status
        faq.is_featured = not faq.is_featured
        await db.commit()
        await db.refresh(faq)
        
        message = "FAQ featured" if faq.is_featured else "FAQ unfeatured"
        
        return {
            "message": message,
            "faq": FAQAdminResponse.model_validate(faq),
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling FAQ featured status: {str(e)}",
        )
