from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Mood
from app.schemas.mood import MoodOut
from app.schemas.pagination import PaginationParams
from app.utils.pagination import paginate

router = APIRouter(prefix="/moods", tags=["Moods"])


async def get_mood_or_404(session: AsyncSession, mood_id: uuid.UUID) -> Mood:
    result = await session.execute(
        select(Mood).where(Mood.id == mood_id, Mood.is_deleted.is_(False))
    )
    mood = result.scalar_one_or_none()
    if not mood:
        raise HTTPException(status_code=404, detail="Mood not found")
    return mood


@router.get("/")
async def list_moods(
    params: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        stmt = select(Mood).where(Mood.is_deleted.is_(False)).order_by(Mood.name.asc())
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
async def get_mood(mood_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> Any:
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
