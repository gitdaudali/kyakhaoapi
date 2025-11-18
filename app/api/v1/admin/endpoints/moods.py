from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Mood
from app.schemas.mood import MoodCreate, MoodOut, MoodUpdate
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.utils.pagination import paginate
from app.api.v1.endpoints.moods import get_mood_or_404

router = APIRouter(prefix="/moods", tags=["Admin"])


@router.get("/")
async def list_moods(
    params: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """List all moods (admin view)."""
    try:
        stmt = select(Mood).where(Mood.is_deleted.is_(False))
        stmt = stmt.order_by(Mood.name.asc())
        
        result = await paginate(
            session,
            stmt,
            params,
            mapper=lambda obj: MoodOut.model_validate(obj),
        )
        
        return success_response(
            message="Moods retrieved successfully",
            data=result.model_dump()
        )
    except Exception as e:
        return error_response(
            message=f"Error retrieving moods: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{mood_id}")
async def get_mood(
    mood_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Get a specific mood by ID."""
    try:
        mood = await get_mood_or_404(session, mood_id)
        mood_out = MoodOut.model_validate(mood)
        return success_response(
            message="Mood retrieved successfully",
            data=mood_out.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Error retrieving mood: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_mood(
    payload: MoodCreate,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        mood = Mood(**payload.dict())
        session.add(mood)
        await session.commit()
        await session.refresh(mood)
        
        mood_out = MoodOut.model_validate(mood)
        return success_response(
            message="Mood created successfully",
            data=mood_out.model_dump(),
            status_code=status.HTTP_201_CREATED
        )
    except IntegrityError as e:
        await session.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            return error_response(
                message=f"Mood with name '{payload.name}' already exists",
                status_code=status.HTTP_409_CONFLICT
            )
        return error_response(
            message="Database integrity error occurred",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error creating mood: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/{mood_id}")
async def update_mood(
    mood_id: uuid.UUID,
    payload: MoodUpdate,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        mood = await get_mood_or_404(session, mood_id)
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(mood, field, value)
        await session.commit()
        await session.refresh(mood)
        
        mood_out = MoodOut.model_validate(mood)
        return success_response(
            message="Mood updated successfully",
            data=mood_out.model_dump()
        )
    except IntegrityError as e:
        await session.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
            name = payload.name if hasattr(payload, 'name') and payload.name else "this name"
            return error_response(
                message=f"Mood with name '{name}' already exists",
                status_code=status.HTTP_409_CONFLICT
            )
        return error_response(
            message="Database integrity error occurred",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error updating mood: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{mood_id}")
async def delete_mood(
    mood_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        mood = await get_mood_or_404(session, mood_id)
        mood.is_deleted = True
        await session.commit()
        return success_response(
            message="Mood deleted successfully",
            data={"id": str(mood.id), "name": mood.name}
        )
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error deleting mood: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

