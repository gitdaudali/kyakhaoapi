from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.food import Reservation, Restaurant
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.reservation import ReservationCreate, ReservationOut
from app.utils.pagination import paginate

router = APIRouter(prefix="/reservations", tags=["Reservations"])


async def get_reservation_or_404(session: AsyncSession, reservation_id: uuid.UUID) -> Reservation:
    result = await session.execute(
        select(Reservation)
        .options(selectinload(Reservation.restaurant))
        .where(Reservation.id == reservation_id, Reservation.is_deleted.is_(False))
    )
    reservation = result.scalar_one_or_none()
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    return reservation


@router.get("/", response_model=PaginatedResponse[ReservationOut])
async def list_reservations(
    params: PaginationParams = Depends(),
    restaurant_id: uuid.UUID | None = Query(default=None),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ReservationOut]:
    stmt = select(Reservation).where(Reservation.is_deleted.is_(False))
    if restaurant_id:
        stmt = stmt.where(Reservation.restaurant_id == restaurant_id)
    stmt = stmt.order_by(Reservation.reservation_time.asc())
    return await paginate(session, stmt, params, mapper=lambda obj: ReservationOut.model_validate(obj))


@router.post("/", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    payload: ReservationCreate,
    session: AsyncSession = Depends(get_db),
) -> ReservationOut:
    restaurant = await session.get(Restaurant, payload.restaurant_id)
    if not restaurant or restaurant.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    reservation = Reservation(**payload.dict())
    session.add(reservation)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A reservation already exists for this time slot",
        )
    await session.refresh(reservation)
    return ReservationOut.model_validate(reservation)


@router.get("/{reservation_id}", response_model=ReservationOut)
async def get_reservation(
    reservation_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> ReservationOut:
    reservation = await get_reservation_or_404(session, reservation_id)
    return ReservationOut.model_validate(reservation)
