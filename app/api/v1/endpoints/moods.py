from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.food import Mood
from app.schemas.mood import MoodCreate, MoodOut, MoodUpdate
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.utils.pagination import paginate

router = APIRouter(prefix="/moods", tags=["Moods"])


async def get_mood_or_404(session: AsyncSession, mood_id: uuid.UUID) -> Mood:
    result = await session.execute(
        select(Mood).where(Mood.id == mood_id, Mood.is_deleted.is_(False))
    )
    mood = result.scalar_one_or_none()
    if not mood:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mood not found")
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


@router.post("/", response_model=MoodOut, status_code=status.HTTP_201_CREATED)
async def create_mood(payload: MoodCreate, session: AsyncSession = Depends(get_db)) -> MoodOut:
    mood = Mood(**payload.dict())
    session.add(mood)
    await session.commit()
    await session.refresh(mood)
    return MoodOut.model_validate(mood)


@router.get("/{mood_id}", response_model=MoodOut)
async def get_mood(mood_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> MoodOut:
    mood = await get_mood_or_404(session, mood_id)
    return MoodOut.model_validate(mood)


@router.put("/{mood_id}", response_model=MoodOut)
async def update_mood(
    mood_id: uuid.UUID,
    payload: MoodUpdate,
    session: AsyncSession = Depends(get_db),
) -> MoodOut:
    mood = await get_mood_or_404(session, mood_id)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(mood, field, value)
    await session.commit()
    await session.refresh(mood)
    return MoodOut.model_validate(mood)


@router.delete("/{mood_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mood(mood_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> Response:
    mood = await get_mood_or_404(session, mood_id)
    mood.is_deleted = True
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
