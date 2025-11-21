"""User allergies management endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Allergy
from app.models.user import User
from app.schemas.allergy import UserAllergyResponse, UserAllergyUpdate
from app.utils.auth import get_current_user

router = APIRouter(prefix="/users", tags=["User Allergies"])


async def get_user_or_404(
    user_id: uuid.UUID,
    db: AsyncSession,
    current_user: User,
) -> User:
    """Get user by ID or raise 404. Also checks authorization."""
    # Only allow users to access their own data, or admins to access any user
    if str(current_user.id) != str(user_id) and not (current_user.is_staff or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own allergies"
        )
    
    stmt = select(User).where(User.id == user_id, User.is_deleted.is_(False))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}/allergies")
async def update_user_allergies(
    user_id: uuid.UUID,
    payload: UserAllergyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update user's selected allergies.
    Used when user presses Continue on onboarding screen.
    Replaces existing allergies with new selection.
    """
    try:
        # Get and verify user
        user = await get_user_or_404(user_id, db, current_user)
        
        # Validate that all allergy IDs exist
        if payload.allergies:
            from uuid import UUID as PyUUID
            # Convert string UUIDs to UUID objects
            try:
                allergy_uuids = [PyUUID(allergy_id) for allergy_id in payload.allergies]
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid allergy ID format: {str(e)}"
                )
            
            stmt = select(Allergy).where(
                Allergy.id.in_(allergy_uuids),
                Allergy.is_deleted.is_(False)
            )
            result = await db.execute(stmt)
            existing_allergies = {str(allergy.id) for allergy in result.scalars().all()}
            
            invalid_allergies = set(payload.allergies) - existing_allergies
            if invalid_allergies:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid allergy IDs: {', '.join(invalid_allergies)}"
                )
        
        # Use transaction to replace allergies
        from app.models.food import UserAllergyAssociation
        from sqlalchemy import insert, delete as sql_delete
        
        # Delete existing user allergies
        delete_stmt = sql_delete(UserAllergyAssociation).where(
            UserAllergyAssociation.c.user_id == user_id
        )
        await db.execute(delete_stmt)
        
        # Add new allergies
        if payload.allergies:
            from uuid import UUID as PyUUID
            # Convert string UUIDs to UUID objects for insertion
            allergy_uuids = [PyUUID(allergy_id) for allergy_id in payload.allergies]
            # Insert new user-allergy associations
            insert_values = [
                {"user_id": user_id, "allergy_id": allergy_uuid}
                for allergy_uuid in allergy_uuids
            ]
            if insert_values:
                insert_stmt = insert(UserAllergyAssociation).values(insert_values)
                await db.execute(insert_stmt)
        
        await db.commit()
        
        # Refresh user to get updated allergies
        await db.refresh(user)
        
        # Get updated allergies
        from app.models.food import UserAllergyAssociation
        stmt = select(Allergy).join(
            UserAllergyAssociation,
            Allergy.id == UserAllergyAssociation.c.allergy_id
        ).where(
            UserAllergyAssociation.c.user_id == user_id,
            Allergy.is_deleted.is_(False)
        )
        result = await db.execute(stmt)
        user_allergies = [str(allergy.id) for allergy in result.scalars().all()]
        
        return {
            "userId": str(user_id),
            "allergies": user_allergies,
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        return error_response(
            message=f"Error updating user allergies: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

