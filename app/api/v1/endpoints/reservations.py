from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import Reservation, Restaurant
from app.schemas.pagination import PaginationParams
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


@router.get("/")
async def list_reservations(
    params: PaginationParams = Depends(),
    restaurant_id: uuid.UUID | None = Query(default=None),
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        stmt = select(Reservation).where(Reservation.is_deleted.is_(False))
        if restaurant_id:
            stmt = stmt.where(Reservation.restaurant_id == restaurant_id)
        stmt = stmt.order_by(Reservation.reservation_time.asc())
        result = await paginate(session, stmt, params, mapper=lambda obj: ReservationOut.model_validate(obj))
        
        return success_response(
            message="Reservations retrieved successfully",
            data=result.model_dump()
        )
    except Exception as e:
        return error_response(
            message=f"Error retrieving reservations: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_reservation(
    payload: ReservationCreate,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        restaurant = await session.get(Restaurant, payload.restaurant_id)
        if not restaurant or restaurant.is_deleted:
            return error_response(
                message="Restaurant not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        reservation = Reservation(**payload.dict())
        session.add(reservation)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            return error_response(
                message="A reservation already exists for this time slot",
                status_code=status.HTTP_409_CONFLICT
            )
        await session.refresh(reservation)
        reservation_out = ReservationOut.model_validate(reservation)
        
        return success_response(
            message="Reservation created successfully",
            data=reservation_out.model_dump(),
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        return error_response(
            message=f"Error creating reservation: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{reservation_id}")
async def get_reservation(
    reservation_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Any:
    try:
        reservation = await get_reservation_or_404(session, reservation_id)
        reservation_out = ReservationOut.model_validate(reservation)
        return success_response(
            message="Reservation retrieved successfully",
            data=reservation_out.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Error retrieving reservation: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
