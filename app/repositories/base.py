"""Base repository class providing common data access patterns."""

from typing import Generic, TypeVar, Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Base repository providing common CRUD operations.
    
    All repositories should inherit from this class to ensure
    consistent data access patterns and soft delete support.
    """

    def __init__(self, session: AsyncSession, model: type[T]):
        """
        Initialize repository with database session and model.
        
        Args:
            session: Async database session
            model: SQLAlchemy model class
        """
        self.session = session
        self.model = model

    async def get_by_id(
        self, id: UUID, include_deleted: bool = False
    ) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            id: Entity UUID
            include_deleted: Whether to include soft-deleted entities
            
        Returns:
            Entity instance or None if not found
        """
        stmt = select(self.model).where(self.model.id == id)
        
        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_or_404(self, id: UUID, include_deleted: bool = False) -> T:
        """
        Get entity by ID or raise 404.
        
        Args:
            id: Entity UUID
            include_deleted: Whether to include soft-deleted entities
            
        Returns:
            Entity instance
            
        Raises:
            HTTPException: 404 if entity not found
        """
        from fastapi import HTTPException, status
        
        entity = await self.get_by_id(id, include_deleted)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )
        return entity

    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
        order_by: Optional[Any] = None,
    ) -> List[T]:
        """
        List all entities with pagination.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            include_deleted: Whether to include soft-deleted entities
            order_by: Column to order by (default: created_at desc)
            
        Returns:
            List of entities
        """
        stmt = select(self.model)
        
        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
        
        if order_by is None and hasattr(self.model, "created_at"):
            stmt = stmt.order_by(self.model.created_at.desc())
        elif order_by is not None:
            stmt = stmt.order_by(order_by)
        
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, include_deleted: bool = False) -> int:
        """
        Count total entities.
        
        Args:
            include_deleted: Whether to include soft-deleted entities
            
        Returns:
            Total count
        """
        from sqlalchemy import func
        
        stmt = select(func.count()).select_from(self.model)
        
        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
        
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, **kwargs) -> T:
        """
        Create new entity.
        
        Args:
            **kwargs: Entity attributes
            
        Returns:
            Created entity instance
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: UUID, **kwargs) -> Optional[T]:
        """
        Update entity by ID.
        
        Args:
            id: Entity UUID
            **kwargs: Attributes to update
            
        Returns:
            Updated entity or None if not found
        """
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .returning(self.model)
        )
        
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none()

    async def soft_delete(self, id: UUID) -> bool:
        """
        Soft delete entity (set is_deleted=True).
        
        Args:
            id: Entity UUID
            
        Returns:
            True if deleted, False if not found
        """
        if not hasattr(self.model, "is_deleted"):
            raise ValueError(f"{self.model.__name__} does not support soft deletes")
        
        stmt = (
            update(self.model)
            .where(self.model.id == id, self.model.is_deleted == False)
            .values(is_deleted=True)
        )
        
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def hard_delete(self, id: UUID) -> bool:
        """
        Permanently delete entity from database.
        
        Args:
            id: Entity UUID
            
        Returns:
            True if deleted, False if not found
        """
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def exists(self, id: UUID, include_deleted: bool = False) -> bool:
        """
        Check if entity exists.
        
        Args:
            id: Entity UUID
            include_deleted: Whether to include soft-deleted entities
            
        Returns:
            True if exists, False otherwise
        """
        entity = await self.get_by_id(id, include_deleted)
        return entity is not None

