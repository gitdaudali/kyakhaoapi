"""Public allergies endpoints."""
from __future__ import annotations

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.food import Allergy

router = APIRouter(prefix="/allergies", tags=["Allergies"])


@router.get("")
async def get_allergies(
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    Get list of all available allergies.
    Public endpoint - no authentication required.
    Used by onboarding screen to show allergy options.
    
    Returns format:
    [
        {"id": "wheat", "name": "Wheat"},
        {"id": "peanut", "name": "Peanut"},
        ...
    ]
    """
    try:
        stmt = select(Allergy).where(Allergy.is_deleted.is_(False))
        stmt = stmt.order_by(Allergy.name.asc())
        
        result = await db.execute(stmt)
        allergies = result.scalars().all()
        
        allergy_list = [
            {"id": str(allergy.id), "name": allergy.name}
            for allergy in allergies
        ]
        
        return allergy_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving allergies: {str(e)}"
        )

