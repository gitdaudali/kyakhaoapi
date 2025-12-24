"""Transaction management utilities for ensuring atomic operations."""

from functools import wraps
from typing import Callable, TypeVar, ParamSpec
from sqlalchemy.ext.asyncio import AsyncSession

P = ParamSpec("P")
R = TypeVar("R")


def transactional(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator to ensure function runs within a transaction.
    
    Automatically commits on success, rolls back on exception.
    
    Usage:
        @transactional
        async def create_order(session: AsyncSession, ...):
            # Multiple database operations
            # All committed atomically
            pass
    """
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # Find session in kwargs or args
        session: AsyncSession | None = kwargs.get("session")
        
        if not session:
            # Look for session in args
            for arg in args:
                if isinstance(arg, AsyncSession):
                    session = arg
                    break
        
        if not session:
            raise ValueError(
                "No AsyncSession found in function arguments. "
                "Session must be passed as 'session' kwarg or positional arg."
            )
        
        try:
            result = await func(*args, **kwargs)
            await session.commit()
            return result
        except Exception:
            await session.rollback()
            raise
    
    return wrapper


class TransactionContext:
    """
    Context manager for explicit transaction boundaries.
    
    Usage:
        async with TransactionContext(session) as tx:
            # Multiple operations
            await tx.commit()  # or auto-commits on exit
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._committed = False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and not self._committed:
            await self.session.commit()
        elif exc_type is not None:
            await self.session.rollback()
        return False
    
    async def commit(self):
        """Explicitly commit the transaction."""
        await self.session.commit()
        self._committed = True
    
    async def rollback(self):
        """Explicitly rollback the transaction."""
        await self.session.rollback()
        self._committed = True

