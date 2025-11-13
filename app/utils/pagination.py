from __future__ import annotations

from typing import Any, Callable, Iterable, Sequence, Tuple, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.pagination import PaginatedResponse, PaginationParams

T = TypeVar("T")


async def paginate(
    session: AsyncSession,
    stmt: Select[Any],
    params: PaginationParams,
    *,
    mapper: Callable[[Any], T],
) -> PaginatedResponse[T]:
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await session.execute(count_stmt)
    total = total_result.scalar_one()

    paginated_stmt = stmt.offset(params.offset).limit(params.limit)
    items_result = await session.execute(paginated_stmt)
    raw_items = items_result.scalars().all()
    items = [mapper(item) for item in raw_items]

    return PaginatedResponse.create(
        items=items,
        total=total,
        limit=params.limit,
        offset=params.offset,
    )
