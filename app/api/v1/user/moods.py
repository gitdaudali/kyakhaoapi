from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.food import Mood
from app.schemas.mood import MoodOut
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.utils.pagination import paginate

router = APIRouter(prefix="/moods", tags=["User Moods"])


async def get_mood_or_404(session: AsyncSession, mood_id: uuid.UUID) -> Mood:
    result = await session.execute(
        select(Mood).where(Mood.id == mood_id, Mood.is_deleted.is_(False))
    )
    mood = result.scalar_one_or_none()
    if not mood:
        raise HTTPException(status_code=404, detail="Mood not found")
    return mood


@router.get("/", response_model=PaginatedResponse[MoodOut])
async def list_moods(
    params: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[MoodOut]:
    stmt = select(Mood).where(Mood.is_deleted.is_(False)).order_by(Mood.name.asc())
    return await paginate(
        session,
        stmt,
        params,
        mapper=lambda obj: MoodOut.model_validate(obj),
    )


@router.get("/{mood_id}", response_model=MoodOut)
async def get_mood(mood_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> MoodOut:
    mood = await get_mood_or_404(session, mood_id)
    return MoodOut.model_validate(mood)
