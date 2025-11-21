"""User profile endpoints."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Allergy, UserAllergyAssociation
from app.models.user import User
from app.schemas.allergy import UserAllergyUpdate
from app.utils.auth import get_current_user

router = APIRouter(prefix="/user", tags=["User Profile"])


@router.post("/allergies", status_code=status.HTTP_201_CREATED)
async def submit_user_allergies(
    payload: UserAllergyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Submit user's allergy survey answers.
    Called after login (first-run) or when user completes the survey.
    Replaces existing allergies with new selection.
    
    **Authentication Required**: Bearer token in Authorization header
    
    Request body:
    {
        "allergies": ["uuid1", "uuid2", ...]  // List of allergy UUIDs
    }
    """
    try:
        user_id = current_user.id
        
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
        
        # Get updated allergies with full details
        stmt = select(Allergy).join(
            UserAllergyAssociation,
            Allergy.id == UserAllergyAssociation.c.allergy_id
        ).where(
            UserAllergyAssociation.c.user_id == user_id,
            Allergy.is_deleted.is_(False)
        )
        result = await db.execute(stmt)
        user_allergies = result.scalars().all()
        
        # Build response with allergy details
        allergies_list = [
            {
                "id": str(allergy.id),
                "name": allergy.name,
                "identifier": allergy.identifier
            }
            for allergy in user_allergies
        ]
        
        return success_response(
            message="Allergies submitted successfully",
            data={
                "userId": str(user_id),
                "allergies": allergies_list,
                "updatedAt": datetime.now(timezone.utc).isoformat()
            },
            status_code=status.HTTP_201_CREATED
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        return error_response(
            message=f"Error submitting allergies: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

