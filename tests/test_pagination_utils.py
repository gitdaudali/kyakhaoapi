import asyncio
from dataclasses import dataclass

import pytest
import pytest_asyncio
from sqlalchemy import Column, Integer, MetaData, String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.schemas.pagination import PaginationParams
from app.utils.pagination import paginate
from app.utils.query_filters import haversine_distance_expr

Base = declarative_base(metadata=MetaData())


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


@dataclass
class ItemSchema:
    id: int
    name: str

    @classmethod
    def from_model(cls, model: Item) -> "ItemSchema":
        return cls(id=model.id, name=model.name)


@pytest_asyncio.fixture(scope="module")
async def async_session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with SessionLocal() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_paginate_returns_expected_slice(async_session: AsyncSession):
    async_session.add_all([Item(name=f"Item {idx}") for idx in range(1, 6)])
    await async_session.commit()

    stmt = select(Item).order_by(Item.id.asc())
    params = PaginationParams(limit=2, offset=2)

    result = await paginate(async_session, stmt, params, mapper=ItemSchema.from_model)

    assert result.total == 5
    assert result.limit == 2
    assert result.offset == 2
    assert result.total_pages == 3
    assert [item.name for item in result.items] == ["Item 3", "Item 4"]


@pytest.mark.asyncio
async def test_haversine_distance_expr(async_session: AsyncSession):
    distance_expr = haversine_distance_expr(0, 0, 0, 1)
    stmt = select(distance_expr.label("distance"))
    result = await async_session.execute(stmt)
    distance = result.scalar_one()
    assert distance == pytest.approx(111.19, rel=0.05)
