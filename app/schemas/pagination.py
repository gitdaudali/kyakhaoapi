from __future__ import annotations

from math import ceil
from typing import Generic, Iterable, List, Optional, Sequence, TypeVar

from pydantic import BaseModel, Field, PositiveInt

T = TypeVar("T")


class PaginationParams(BaseModel):
    limit: PositiveInt = Field(default=20, le=100)
    offset: int = Field(default=0, ge=0)
    sort: Optional[str] = Field(default=None, description="Field to sort by e.g. rating,-name")


class PaginatedResponse(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    limit: int
    offset: int
    total_pages: int

    @classmethod
    def create(
        cls,
        *,
        items: Sequence[T],
        total: int,
        limit: int,
        offset: int,
    ) -> "PaginatedResponse[T]":
        total_pages = ceil(total / limit) if total else 0
        return cls(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            total_pages=total_pages,
        )
