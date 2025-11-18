"""Admin contact endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.contact import ContactMessage
from app.schemas.contact import ContactAdminOut
from app.schemas.pagination import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/contact", tags=["Admin Contact"])


@router.get("/")
async def list_all_contact_messages(
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Get all contact form submissions (admin only)."""
    try:
        # Build query
        query = select(ContactMessage).where(ContactMessage.is_deleted.is_(False))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        query = query.order_by(ContactMessage.created_at.desc())
        query = query.offset(pagination.offset).limit(pagination.limit)
        
        # Execute query
        result = await session.execute(query)
        messages = result.scalars().all()
        
        messages_list = [
            ContactAdminOut(
                id=message.id,
                name=message.name,
                email=message.email,
                phone=message.phone,
                message=message.message,
                created_at=message.created_at,
                updated_at=message.updated_at,
            ).model_dump()
            for message in messages
        ]
        
        paginated_response = PaginatedResponse(
            items=messages_list,
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            total_pages=(total + pagination.limit - 1) // pagination.limit if pagination.limit > 0 else 0
        )
        
        return success_response(
            message="Contact messages retrieved successfully",
            data=paginated_response.model_dump()
        )
        
    except Exception as e:
        return error_response(
            message=f"Error retrieving contact messages: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

