"""Service for Cuisine business logic operations."""

from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.food import Cuisine
from app.repositories.cuisine_repository import CuisineRepository
from app.services.base import BaseService


class CuisineService(BaseService[Cuisine]):
    """Service for Cuisine business logic."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = CuisineRepository(session)

    async def get_cuisine(self, cuisine_id: UUID) -> Cuisine:
        """
        Get cuisine by ID.
        
        Args:
            cuisine_id: Cuisine UUID
            
        Returns:
            Cuisine instance
            
        Raises:
            HTTPException: If cuisine not found
        """
        return await self.repository.get_by_id_or_404(cuisine_id)

    async def list_cuisines(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Cuisine]:
        """
        List all cuisines.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of cuisines
        """
        return await self.repository.list_all(limit=limit, offset=offset)

