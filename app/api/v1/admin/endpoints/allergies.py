"""Admin allergies management endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Allergy
from app.schemas.allergy import AllergyCreate, AllergyResponse

router = APIRouter(prefix="/allergies", tags=["Admin"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_allergy(
    payload: AllergyCreate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new allergy option.
    Admin only endpoint.
    """
    try:
        # Check if allergy with same identifier already exists (if provided)
        if payload.id:
            stmt = select(Allergy).where(Allergy.identifier == payload.id, Allergy.is_deleted.is_(False))
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Allergy with identifier '{payload.id}' already exists"
                )
        
        # Create new allergy (UUID will be auto-generated)
        new_allergy = Allergy(
            name=payload.name,
            type=payload.type or "food",
            identifier=payload.id  # Store the identifier string
        )
        
        db.add(new_allergy)
        await db.commit()
        await db.refresh(new_allergy)
        
        return success_response(
            message="Allergy created successfully",
            data=AllergyResponse(
                id=str(new_allergy.id),
                name=new_allergy.name,
                type=new_allergy.type,
                identifier=new_allergy.identifier
            ).model_dump(),
            status_code=status.HTTP_201_CREATED
        )
        
    except HTTPException:
        raise
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Allergy creation failed: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        return error_response(
            message=f"Error creating allergy: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{allergy_id}")
async def delete_allergy(
    allergy_id: str,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete an allergy option from the master list.
    Admin only endpoint.
    This will also remove the allergy from all users who have it selected.
    """
    try:
        from uuid import UUID as PyUUID
        # Try to parse as UUID first, if fails try as identifier
        try:
            allergy_uuid = PyUUID(allergy_id)
            stmt = select(Allergy).where(Allergy.id == allergy_uuid, Allergy.is_deleted.is_(False))
        except ValueError:
            # If not a valid UUID, try as identifier
            stmt = select(Allergy).where(Allergy.identifier == allergy_id, Allergy.is_deleted.is_(False))
        
        result = await db.execute(stmt)
        allergy = result.scalar_one_or_none()
        
        if not allergy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Allergy with ID '{allergy_id}' not found"
            )
        
        # Soft delete the allergy
        allergy.is_deleted = True
        await db.commit()
        
        return success_response(
            message=f"Allergy '{allergy_id}' deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        return error_response(
            message=f"Error deleting allergy: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

