"""Service for Restaurant business logic operations."""

from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.food import Restaurant
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.base import BaseService


class RestaurantService(BaseService[Restaurant]):
    """Service for Restaurant business logic."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = RestaurantRepository(session)

    async def get_restaurant(self, restaurant_id: UUID) -> Restaurant:
        """
        Get restaurant by ID.
        
        Args:
            restaurant_id: Restaurant UUID
            
        Returns:
            Restaurant instance
            
        Raises:
            HTTPException: If restaurant not found
        """
        return await self.repository.get_by_id_or_404(restaurant_id)

    async def list_restaurants(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Restaurant]:
        """
        List all restaurants.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of restaurants
        """
        return await self.repository.list_all(limit=limit, offset=offset)

    async def list_top_rated_restaurants(
        self,
        min_rating: float = 4.0,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Restaurant]:
        """
        List top-rated restaurants.
        
        Args:
            min_rating: Minimum rating threshold
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of top-rated restaurants
        """
        return await self.repository.list_top_rated(
            min_rating=min_rating,
            limit=limit,
            offset=offset,
        )

