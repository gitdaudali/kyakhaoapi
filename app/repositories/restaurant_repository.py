"""Repository for Restaurant data access operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.food import Restaurant
from app.repositories.base import BaseRepository


class RestaurantRepository(BaseRepository[Restaurant]):
    """Repository for Restaurant model with specialized query methods."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Restaurant)

    async def get_by_id_with_dishes(self, id: UUID) -> Optional[Restaurant]:
        """
        Get restaurant by ID with dishes eagerly loaded.
        
        Args:
            id: Restaurant UUID
            
        Returns:
            Restaurant with dishes loaded
        """
        stmt = (
            select(Restaurant)
            .options(selectinload(Restaurant.dishes))
            .where(Restaurant.id == id, Restaurant.is_deleted == False)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_top_rated(
        self,
        min_rating: float = 4.0,
        limit: int = 10,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> List[Restaurant]:
        """
        List top-rated restaurants.
        
        Args:
            min_rating: Minimum rating threshold
            limit: Maximum number of results
            offset: Number of results to skip
            include_deleted: Whether to include soft-deleted restaurants
            
        Returns:
            List of top-rated restaurants
        """
        stmt = (
            select(Restaurant)
            .where(
                Restaurant.rating.isnot(None),
                Restaurant.rating >= min_rating,
            )
        )
        
        if not include_deleted:
            stmt = stmt.where(Restaurant.is_deleted == False)
        
        stmt = stmt.order_by(Restaurant.rating.desc(), Restaurant.name.asc())
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_name(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> List[Restaurant]:
        """
        Search restaurants by name (case-insensitive partial match).
        
        Args:
            query: Search query string
            limit: Maximum number of results
            offset: Number of results to skip
            include_deleted: Whether to include soft-deleted restaurants
            
        Returns:
            List of matching restaurants
        """
        stmt = select(Restaurant).where(Restaurant.name.ilike(f"%{query}%"))
        
        if not include_deleted:
            stmt = stmt.where(Restaurant.is_deleted == False)
        
        stmt = stmt.order_by(Restaurant.rating.desc().nullslast(), Restaurant.name.asc())
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

