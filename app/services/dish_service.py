"""Service for Dish business logic operations."""

from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.food import Dish
from app.repositories.dish_repository import DishRepository
from app.schemas.dish import DishCreate, DishUpdate
from app.services.base import BaseService


class DishService(BaseService[Dish]):
    """Service for Dish business logic."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = DishRepository(session)

    async def create_dish(self, payload: DishCreate) -> Dish:
        """
        Create a new dish with validation.
        
        Args:
            payload: Dish creation data
            
        Returns:
            Created dish instance
            
        Raises:
            HTTPException: If validation fails or dish already exists
        """
        # Validate restaurant exists
        restaurant_exists = await self.repository.validate_restaurant_exists(
            payload.restaurant_id
        )
        if not restaurant_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )

        # Validate cuisine exists
        cuisine_exists = await self.repository.validate_cuisine_exists(
            payload.cuisine_id
        )
        if not cuisine_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuisine not found"
            )

        # Validate moods if provided
        moods = []
        if payload.mood_ids:
            moods = await self.repository.get_moods_by_ids(payload.mood_ids)
            if len(moods) != len(set(payload.mood_ids)):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="One or more moods not found"
                )

        # Create dish
        try:
            dish_data = payload.dict(exclude={"mood_ids"})
            dish = await self.repository.create(**dish_data)
            
            # Associate moods
            if moods:
                dish.moods = moods
                await self.flush()
            
            await self.commit()
            await self.refresh(dish)
            
            # Reload with relations
            dish = await self.repository.get_by_id_with_relations(dish.id)
            
            # Invalidate cache (new dish, invalidate lists)
            from app.services.cache_service import get_cache_service
            cache = await get_cache_service()
            await cache.invalidate_dish(dish.id)
            
            return dish
            
        except IntegrityError as e:
            await self.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "unique constraint" in error_msg.lower() or "duplicate key" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Dish with name '{payload.name}' already exists for this restaurant"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database integrity error occurred"
            )

    async def update_dish(self, dish_id: UUID, payload: DishUpdate) -> Dish:
        """
        Update an existing dish.
        
        Args:
            dish_id: Dish UUID
            payload: Dish update data
            
        Returns:
            Updated dish instance
            
        Raises:
            HTTPException: If dish not found or validation fails
        """
        # Get existing dish
        dish = await self.repository.get_by_id_or_404(dish_id)
        
        # Validate restaurant if provided
        if payload.restaurant_id:
            restaurant_exists = await self.repository.validate_restaurant_exists(
                payload.restaurant_id
            )
            if not restaurant_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurant not found"
                )

        # Validate cuisine if provided
        if payload.cuisine_id:
            cuisine_exists = await self.repository.validate_cuisine_exists(
                payload.cuisine_id
            )
            if not cuisine_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cuisine not found"
                )

        # Validate moods if provided
        if payload.mood_ids is not None:
            moods = await self.repository.get_moods_by_ids(payload.mood_ids)
            if len(moods) != len(set(payload.mood_ids)):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="One or more moods not found"
                )
            dish.moods = moods

        # Update dish attributes
        update_data = payload.dict(exclude_unset=True, exclude={"mood_ids"})
        if update_data:
            for key, value in update_data.items():
                setattr(dish, key, value)

        try:
            await self.flush()
            await self.commit()
            await self.refresh(dish)
            
            # Reload with relations
            dish = await self.repository.get_by_id_with_relations(dish.id)
            
            # Invalidate cache
            from app.services.cache_service import get_cache_service
            cache = await get_cache_service()
            await cache.invalidate_dish(dish.id)
            
            return dish
            
        except IntegrityError as e:
            await self.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "unique constraint" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Dish with this name already exists for this restaurant"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database integrity error occurred"
            )

    async def delete_dish(self, dish_id: UUID) -> bool:
        """
        Soft delete a dish.
        
        Args:
            dish_id: Dish UUID
            
        Returns:
            True if deleted successfully
            
        Raises:
            HTTPException: If dish not found
        """
        # Verify dish exists
        await self.repository.get_by_id_or_404(dish_id)
        
        # Soft delete
        deleted = await self.repository.soft_delete(dish_id)
        if deleted:
            await self.commit()
            
            # Invalidate cache
            from app.services.cache_service import get_cache_service
            cache = await get_cache_service()
            await cache.invalidate_dish(dish_id)
        
        return deleted

    async def get_dish(self, dish_id: UUID) -> Dish:
        """
        Get dish by ID with all relations.
        
        Args:
            dish_id: Dish UUID
            
        Returns:
            Dish instance with relations loaded
            
        Raises:
            HTTPException: If dish not found
        """
        dish = await self.repository.get_by_id_with_relations(dish_id)
        if not dish:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dish not found"
            )
        return dish

    async def list_dishes(
        self,
        restaurant_id: Optional[UUID] = None,
        cuisine_id: Optional[UUID] = None,
        mood_id: Optional[UUID] = None,
        min_rating: Optional[float] = None,
        max_price: Optional[float] = None,
        is_featured: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dish]:
        """
        List dishes with optional filters.
        
        Args:
            restaurant_id: Filter by restaurant
            cuisine_id: Filter by cuisine
            mood_id: Filter by mood
            min_rating: Minimum rating
            max_price: Maximum price
            is_featured: Filter featured dishes
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of dishes
        """
        return await self.repository.filter_dishes(
            restaurant_id=restaurant_id,
            cuisine_id=cuisine_id,
            mood_id=mood_id,
            min_rating=min_rating,
            max_price=max_price,
            is_featured=is_featured,
            limit=limit,
            offset=offset,
        )

    async def list_featured_dishes(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Dish]:
        """
        List featured dishes.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of featured dishes
        """
        return await self.repository.list_featured(limit=limit, offset=offset)

    async def list_top_rated_dishes(
        self,
        min_rating: float = 4.0,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Dish]:
        """
        List top-rated dishes.
        
        Args:
            min_rating: Minimum rating threshold
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of top-rated dishes
        """
        return await self.repository.list_top_rated(
            min_rating=min_rating,
            limit=limit,
            offset=offset,
        )

