from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.user import UserSearchHistory
from app.schemas.user import SearchHistoryCreate


async def add_search_to_history(
    db: AsyncSession, user_id: UUID, search_query: str
) -> UserSearchHistory:
    """
    Add or update search query in user's search history.
    If the same search query exists, update the count and last_searched_at.
    If it doesn't exist, create a new entry.
    """
    try:
        # Clean and normalize the search query
        clean_query = search_query.strip()
        if not clean_query:
            raise ValueError("Search query cannot be empty")

        # Check if search query already exists for this user
        existing_search = await db.execute(
            select(UserSearchHistory).where(
                and_(
                    UserSearchHistory.user_id == user_id,
                    UserSearchHistory.search_query == clean_query,
                    UserSearchHistory.is_deleted == False,
                )
            )
        )
        existing_search = existing_search.scalar_one_or_none()

        if existing_search:
            # Update existing search - increment count and update last_searched_at
            existing_search.search_count += 1
            existing_search.last_searched_at = datetime.now(timezone.utc)
            existing_search.updated_at = datetime.now(timezone.utc)

            await db.commit()
            await db.refresh(existing_search)
            return existing_search
        else:
            # Create new search history entry
            new_search = UserSearchHistory(
                user_id=user_id,
                search_query=clean_query,
                search_count=1,
                last_searched_at=datetime.now(timezone.utc),
            )

            db.add(new_search)
            await db.commit()
            await db.refresh(new_search)
            return new_search

    except Exception as e:
        await db.rollback()
        raise e


async def get_user_search_history(
    db: AsyncSession,
    user_id: UUID,
    page: int = 1,
    size: int = 10,
    limit: Optional[int] = None,
) -> Tuple[List[UserSearchHistory], int]:
    """
    Get user's search history ordered by last_searched_at (most recent first).
    If limit is provided, return only that many recent searches.
    """
    try:
        # Build base query
        query = (
            select(UserSearchHistory)
            .where(
                and_(
                    UserSearchHistory.user_id == user_id,
                    UserSearchHistory.is_deleted == False,
                )
            )
            .order_by(desc(UserSearchHistory.last_searched_at))
        )

        # Get total count
        count_query = select(func.count(UserSearchHistory.id)).where(
            and_(
                UserSearchHistory.user_id == user_id,
                UserSearchHistory.is_deleted == False,
            )
        )
        count_result = await db.execute(count_query)
        total = count_result.scalar()

        # Apply limit if provided (for recent searches)
        if limit:
            query = query.limit(limit)
            search_results = await db.execute(query)
            return search_results.scalars().all(), total

        # Apply pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        search_results = await db.execute(query)
        return search_results.scalars().all(), total

    except Exception as e:
        raise e


async def delete_search_from_history(
    db: AsyncSession, user_id: UUID, search_history_id: UUID
) -> bool:
    """
    Delete a specific search history entry for a user.
    Returns True if deleted, False if not found.
    """
    try:
        # Find the search history entry
        search_entry = await db.execute(
            select(UserSearchHistory).where(
                and_(
                    UserSearchHistory.id == search_history_id,
                    UserSearchHistory.user_id == user_id,
                    UserSearchHistory.is_deleted == False,
                )
            )
        )
        search_entry = search_entry.scalar_one_or_none()

        if not search_entry:
            return False

        # Soft delete the entry
        search_entry.is_deleted = True
        search_entry.updated_at = datetime.now(timezone.utc)

        await db.commit()
        return True

    except Exception as e:
        await db.rollback()
        raise e


async def clear_all_search_history(db: AsyncSession, user_id: UUID) -> int:
    """
    Clear all search history for a user.
    Returns the number of entries deleted.
    """
    try:
        # Get count before deletion
        count_query = select(func.count(UserSearchHistory.id)).where(
            and_(
                UserSearchHistory.user_id == user_id,
                UserSearchHistory.is_deleted == False,
            )
        )
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()

        # Soft delete all entries
        update_query = select(UserSearchHistory).where(
            and_(
                UserSearchHistory.user_id == user_id,
                UserSearchHistory.is_deleted == False,
            )
        )

        search_entries = await db.execute(update_query)
        entries = search_entries.scalars().all()

        for entry in entries:
            entry.is_deleted = True
            entry.updated_at = datetime.now(timezone.utc)

        await db.commit()
        return total_count

    except Exception as e:
        await db.rollback()
        raise e


async def get_recent_searches(
    db: AsyncSession, user_id: UUID, limit: int = 5
) -> List[UserSearchHistory]:
    """
    Get recent search queries for a user (for autocomplete/suggestions).
    Returns the most recent searches ordered by last_searched_at.
    """
    try:
        query = (
            select(UserSearchHistory)
            .where(
                and_(
                    UserSearchHistory.user_id == user_id,
                    UserSearchHistory.is_deleted == False,
                )
            )
            .order_by(desc(UserSearchHistory.last_searched_at))
            .limit(limit)
        )

        result = await db.execute(query)
        return result.scalars().all()

    except Exception as e:
        raise e
