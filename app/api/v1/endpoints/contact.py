"""User contact endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.contact import ContactMessage
from app.schemas.contact import ContactCreate, ContactOut

router = APIRouter(tags=["Contact"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_contact_message(
    payload: ContactCreate,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Submit a contact form message."""
    try:
        # Create contact message
        contact = ContactMessage(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            message=payload.message,
        )
        session.add(contact)
        await session.commit()
        await session.refresh(contact)

        contact_out = ContactOut(
            id=contact.id,
            name=contact.name,
            email=contact.email,
            phone=contact.phone,
            message=contact.message,
            created_at=contact.created_at,
        )

        return success_response(
            message="Your message has been received.",
            data=contact_out.model_dump(),
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error submitting contact message: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

