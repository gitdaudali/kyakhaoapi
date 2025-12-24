"""Repository for Dish data access operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.food import Dish, Restaurant, Cuisine, Mood
from app.repositories.base import BaseRepository
from app.services.cache_service import get_cache_service
from app.core.config import settings


class DishRepository(BaseRepository[Dish]):
    """Repository for Dish model with specialized query methods."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Dish)

    async def get_by_id_with_relations(self, id: UUID, use_cache: bool = True) -> Optional[Dish]:
        """
        Get dish by ID with all relations eagerly loaded.
        
        Args:
            id: Dish UUID
            use_cache: Whether to use cache (default: True)
            
        Returns:
            Dish with moods, restaurant, and cuisine loaded
        """
        cache_key = f"dish:{id}:full"
        
        # Try cache first
        if use_cache and settings.CACHE_ENABLED:
            cache = await get_cache_service()
            cached = await cache.get(cache_key)
            if cached:
                # Reconstruct dish from cached data (simplified - in production, use proper deserialization)
                pass  # For now, always fetch from DB for data integrity
        
        stmt = (
            select(Dish)
            .options(
                selectinload(Dish.moods),
                selectinload(Dish.restaurant),
                selectinload(Dish.cuisine),
            )
            .where(Dish.id == id, Dish.is_deleted == False)
        )
        result = await self.session.execute(stmt)
        dish = result.scalar_one_or_none()
        
        # Cache result
        if dish and use_cache and settings.CACHE_ENABLED:
            cache = await get_cache_service()
            # Convert to dict for caching
            dish_dict = {
                "id": str(dish.id),
                "name": dish.name,
                "description": dish.description,
                "price": float(dish.price) if dish.price else None,
                "rating": float(dish.rating) if dish.rating else None,
                # Add more fields as needed
            }
            await cache.set(cache_key, dish_dict, ttl=settings.CACHE_DISH_TTL)
        
        return dish

    async def list_by_restaurant(
        self,
        restaurant_id: UUID,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> List[Dish]:
        """
        List dishes by restaurant.
        
        Args:
            restaurant_id: Restaurant UUID
            limit: Maximum number of results
            offset: Number of results to skip
            include_deleted: Whether to include soft-deleted dishes
            
        Returns:
            List of dishes
        """
        stmt = (
            select(Dish)
            .options(selectinload(Dish.moods))
            .where(Dish.restaurant_id == restaurant_id)
        )
        
        if not include_deleted:
            stmt = stmt.where(Dish.is_deleted == False)
        
        stmt = stmt.order_by(Dish.name.asc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_cuisine(
        self,
        cuisine_id: UUID,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> List[Dish]:
        """
        List dishes by cuisine.
        
        Args:
            cuisine_id: Cuisine UUID
            limit: Maximum number of results
            offset: Number of results to skip
            include_deleted: Whether to include soft-deleted dishes
            
        Returns:
            List of dishes
        """
        stmt = (
            select(Dish)
            .options(selectinload(Dish.moods))
            .where(Dish.cuisine_id == cuisine_id)
        )
        
        if not include_deleted:
            stmt = stmt.where(Dish.is_deleted == False)
        
        stmt = stmt.order_by(Dish.rating.desc().nullslast(), Dish.name.asc())
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_mood(
        self,
        mood_id: UUID,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> List[Dish]:
        """
        List dishes by mood.
        
        Args:
            mood_id: Mood UUID
            limit: Maximum number of results
            offset: Number of results to skip
            include_deleted: Whether to include soft-deleted dishes
            
        Returns:
            List of dishes
        """
        stmt = (
            select(Dish)
            .options(selectinload(Dish.moods))
            .join(Dish.moods)
            .where(Mood.id == mood_id)
        )
        
        if not include_deleted:
            stmt = stmt.where(Dish.is_deleted == False)
        
        stmt = stmt.order_by(Dish.rating.desc().nullslast(), Dish.name.asc())
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_featured(
        self,
        limit: int = 10,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> List[Dish]:
        """
        List featured dishes.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            include_deleted: Whether to include soft-deleted dishes
            
        Returns:
            List of featured dishes
        """
        stmt = (
            select(Dish)
            .options(selectinload(Dish.moods))
            .where(Dish.is_featured == True)
        )
        
        if not include_deleted:
            stmt = stmt.where(Dish.is_deleted == False)
        
        stmt = stmt.order_by(Dish.featured_week.desc().nullslast(), Dish.rating.desc().nullslast())
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_top_rated(
        self,
        min_rating: float = 4.0,
        limit: int = 10,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> List[Dish]:
        """
        List top-rated dishes.
        
        Args:
            min_rating: Minimum rating threshold
            limit: Maximum number of results
            offset: Number of results to skip
            include_deleted: Whether to include soft-deleted dishes
            
        Returns:
            List of top-rated dishes
        """
        stmt = (
            select(Dish)
            .options(selectinload(Dish.moods))
            .where(
                Dish.rating.isnot(None),
                Dish.rating >= min_rating,
            )
        )
        
        if not include_deleted:
            stmt = stmt.where(Dish.is_deleted == False)
        
        stmt = stmt.order_by(Dish.rating.desc(), Dish.name.asc())
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_name(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> List[Dish]:
        """
        Search dishes by name (case-insensitive partial match).
        
        Args:
            query: Search query string
            limit: Maximum number of results
            offset: Number of results to skip
            include_deleted: Whether to include soft-deleted dishes
            
        Returns:
            List of matching dishes
        """
        stmt = (
            select(Dish)
            .options(selectinload(Dish.moods))
            .where(Dish.name.ilike(f"%{query}%"))
        )
        
        if not include_deleted:
            stmt = stmt.where(Dish.is_deleted == False)
        
        stmt = stmt.order_by(Dish.rating.desc().nullslast(), Dish.name.asc())
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def filter_dishes(
        self,
        restaurant_id: Optional[UUID] = None,
        cuisine_id: Optional[UUID] = None,
        mood_id: Optional[UUID] = None,
        min_rating: Optional[float] = None,
        max_price: Optional[float] = None,
        is_featured: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> List[Dish]:
        """
        Filter dishes by multiple criteria.
        
        Args:
            restaurant_id: Filter by restaurant
            cuisine_id: Filter by cuisine
            mood_id: Filter by mood
            min_rating: Minimum rating
            max_price: Maximum price
            is_featured: Filter featured dishes
            limit: Maximum number of results
            offset: Number of results to skip
            include_deleted: Whether to include soft-deleted dishes
            
        Returns:
            List of filtered dishes
        """
        stmt = select(Dish).options(selectinload(Dish.moods))
        
        conditions = []
        
        if restaurant_id:
            conditions.append(Dish.restaurant_id == restaurant_id)
        
        if cuisine_id:
            conditions.append(Dish.cuisine_id == cuisine_id)
        
        if mood_id:
            stmt = stmt.join(Dish.moods)
            conditions.append(Mood.id == mood_id)
        
        if min_rating is not None:
            conditions.append(Dish.rating.isnot(None))
            conditions.append(Dish.rating >= min_rating)
        
        if max_price is not None:
            conditions.append(Dish.price.isnot(None))
            conditions.append(Dish.price <= max_price)
        
        if is_featured is not None:
            conditions.append(Dish.is_featured == is_featured)
        
        if not include_deleted:
            conditions.append(Dish.is_deleted == False)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.order_by(Dish.rating.desc().nullslast(), Dish.name.asc())
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def validate_restaurant_exists(self, restaurant_id: UUID) -> bool:
        """
        Validate that restaurant exists and is not deleted.
        
        Args:
            restaurant_id: Restaurant UUID
            
        Returns:
            True if restaurant exists and is active
        """
        result = await self.session.execute(
            select(Restaurant).where(
                Restaurant.id == restaurant_id,
                Restaurant.is_deleted == False,
            )
        )
        return result.scalar_one_or_none() is not None

    async def validate_cuisine_exists(self, cuisine_id: UUID) -> bool:
        """
        Validate that cuisine exists and is not deleted.
        
        Args:
            cuisine_id: Cuisine UUID
            
        Returns:
            True if cuisine exists and is active
        """
        result = await self.session.execute(
            select(Cuisine).where(
                Cuisine.id == cuisine_id,
                Cuisine.is_deleted == False,
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_moods_by_ids(self, mood_ids: List[UUID]) -> List[Mood]:
        """
        Get mood entities by IDs.
        
        Args:
            mood_ids: List of mood UUIDs
            
        Returns:
            List of mood entities
        """
        if not mood_ids:
            return []
        
        result = await self.session.execute(
            select(Mood).where(
                Mood.id.in_(mood_ids),
                Mood.is_deleted == False,
            )
        )
        return list(result.scalars().all())

