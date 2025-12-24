"""Base service class providing common business logic patterns."""

from typing import Generic, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseService(Generic[T]):
    """
    Base service class providing common business logic patterns.
    
    All services should inherit from this class to ensure
    consistent patterns and transaction management.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize service with database session.
        
        Args:
            session: Async database session
        """
        self.session = session

    async def commit(self):
        """Commit current transaction."""
        await self.session.commit()

    async def flush(self):
        """Flush pending changes without committing."""
        await self.session.flush()

    async def rollback(self):
        """Rollback current transaction."""
        await self.session.rollback()

    async def refresh(self, instance: T):
        """Refresh instance from database."""
        await self.session.refresh(instance)

