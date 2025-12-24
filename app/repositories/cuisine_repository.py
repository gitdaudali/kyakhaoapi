"""Repository for Cuisine data access operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.food import Cuisine
from app.repositories.base import BaseRepository


class CuisineRepository(BaseRepository[Cuisine]):
    """Repository for Cuisine model with specialized query methods."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Cuisine)

    async def get_by_id_with_dishes(self, id: UUID) -> Optional[Cuisine]:
        """
        Get cuisine by ID with dishes eagerly loaded.
        
        Args:
            id: Cuisine UUID
            
        Returns:
            Cuisine with dishes loaded
        """
        stmt = (
            select(Cuisine)
            .options(selectinload(Cuisine.dishes))
            .where(Cuisine.id == id, Cuisine.is_deleted == False)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_by_name(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> List[Cuisine]:
        """
        Search cuisines by name (case-insensitive partial match).
        
        Args:
            query: Search query string
            limit: Maximum number of results
            offset: Number of results to skip
            include_deleted: Whether to include soft-deleted cuisines
            
        Returns:
            List of matching cuisines
        """
        stmt = select(Cuisine).where(Cuisine.name.ilike(f"%{query}%"))
        
        if not include_deleted:
            stmt = stmt.where(Cuisine.is_deleted == False)
        
        stmt = stmt.order_by(Cuisine.name.asc())
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

