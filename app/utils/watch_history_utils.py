"""
Watch History Utilities

This module contains utility functions for watch history operations.
"""

from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.watch_history import WatchHistory
from app.schemas.watch_history import (
    WatchHistoryCreate,
    WatchHistoryUpdate,
    WatchHistoryListResponse,
    PaginationParams
)


class WatchHistoryService:
    """Service class for watch history operations."""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize the service with a database session."""
        self.db = db_session
    
    async def create_watch_history(
        self, 
        watch_history_data: WatchHistoryCreate
    ) -> WatchHistory:
        """
        Create a new watch history record.
        
        Args:
            watch_history_data: Data for creating the watch history record
            
        Returns:
            WatchHistory: The created watch history record
            
        Raises:
            Exception: If there's an error creating the record
        """
        try:
            # Check if a record already exists for this user and content
            existing_record = await self.get_watch_history_by_user_and_content(
                user_id=watch_history_data.user_id,
                content_id=watch_history_data.content_id,
                episode_id=watch_history_data.episode_id
            )
            
            if existing_record:
                # Update the existing record instead of creating a new one
                existing_record.title = watch_history_data.title
                existing_record.thumbnail_url = watch_history_data.thumbnail_url
                existing_record.last_watched_at = (
                    watch_history_data.last_watched_at or datetime.utcnow()
                )
                existing_record.updated_at = datetime.utcnow()
                
                await self.db.commit()
                await self.db.refresh(existing_record)
                return existing_record
            
            # Create new record
            watch_history = WatchHistory(
                user_id=watch_history_data.user_id,
                title=watch_history_data.title,
                thumbnail_url=watch_history_data.thumbnail_url,
                content_id=watch_history_data.content_id,
                episode_id=watch_history_data.episode_id,
                last_watched_at=watch_history_data.last_watched_at or datetime.utcnow()
            )
            
            self.db.add(watch_history)
            await self.db.commit()
            await self.db.refresh(watch_history)
            
            return watch_history
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error creating watch history: {str(e)}")
    
    async def get_watch_history_by_id(
        self, 
        history_id: UUID
    ) -> Optional[WatchHistory]:
        """
        Get a watch history record by ID.
        
        Args:
            history_id: The ID of the watch history record
            
        Returns:
            Optional[WatchHistory]: The watch history record if found, None otherwise
        """
        try:
            stmt = select(WatchHistory).where(
                and_(
                    WatchHistory.id == history_id,
                    WatchHistory.is_deleted == False
                )
            )
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
            
        except Exception as e:
            raise Exception(f"Error fetching watch history: {str(e)}")
    
    async def get_watch_history_by_user_and_content(
        self,
        user_id: UUID,
        content_id: Optional[UUID] = None,
        episode_id: Optional[UUID] = None
    ) -> Optional[WatchHistory]:
        """
        Get a watch history record by user and content.
        
        Args:
            user_id: The user ID
            content_id: Optional content ID
            episode_id: Optional episode ID
            
        Returns:
            Optional[WatchHistory]: The watch history record if found, None otherwise
        """
        try:
            conditions = [
                WatchHistory.user_id == user_id,
                WatchHistory.is_deleted == False
            ]
            
            if content_id:
                conditions.append(WatchHistory.content_id == content_id)
            if episode_id:
                conditions.append(WatchHistory.episode_id == episode_id)
            
            stmt = select(WatchHistory).where(and_(*conditions))
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
            
        except Exception as e:
            raise Exception(f"Error fetching watch history: {str(e)}")
    
    async def get_user_watch_history(
        self,
        user_id: UUID,
        pagination: PaginationParams
    ) -> WatchHistoryListResponse:
        """
        Get paginated watch history for a user.
        
        Args:
            user_id: The user ID
            pagination: Pagination parameters
            
        Returns:
            WatchHistoryListResponse: Paginated watch history response
        """
        try:
            # Calculate offset
            offset = (pagination.page - 1) * pagination.limit
            
            # Get total count
            count_stmt = select(func.count(WatchHistory.id)).where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.is_deleted == False
                )
            )
            count_result = await self.db.execute(count_stmt)
            total_items = count_result.scalar()
            
            # Get paginated results
            stmt = (
                select(WatchHistory)
                .where(
                    and_(
                        WatchHistory.user_id == user_id,
                        WatchHistory.is_deleted == False
                    )
                )
                .order_by(desc(WatchHistory.last_watched_at))
                .offset(offset)
                .limit(pagination.limit)
            )
            
            result = await self.db.execute(stmt)
            items = result.scalars().all()
            
            # Calculate pagination info
            total_pages = (total_items + pagination.limit - 1) // pagination.limit
            has_next = pagination.page < total_pages
            has_previous = pagination.page > 1
            
            return WatchHistoryListResponse(
                items=items,
                total_items=total_items,
                total_pages=total_pages,
                current_page=pagination.page,
                page_size=pagination.limit,
                has_next=has_next,
                has_previous=has_previous
            )
            
        except Exception as e:
            raise Exception(f"Error fetching user watch history: {str(e)}")
    
    async def update_watch_history(
        self,
        history_id: UUID,
        update_data: WatchHistoryUpdate
    ) -> Optional[WatchHistory]:
        """
        Update a watch history record.
        
        Args:
            history_id: The ID of the watch history record
            update_data: Data for updating the record
            
        Returns:
            Optional[WatchHistory]: The updated watch history record if found, None otherwise
        """
        try:
            # Get the existing record
            watch_history = await self.get_watch_history_by_id(history_id)
            if not watch_history:
                return None
            
            # Update fields
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(watch_history, field, value)
            
            watch_history.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(watch_history)
            
            return watch_history
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error updating watch history: {str(e)}")
    
    async def delete_watch_history(self, history_id: UUID) -> bool:
        """
        Soft delete a watch history record.
        
        Args:
            history_id: The ID of the watch history record
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            watch_history = await self.get_watch_history_by_id(history_id)
            if not watch_history:
                return False
            
            # Soft delete
            watch_history.is_deleted = True
            watch_history.updated_at = datetime.utcnow()
            
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error deleting watch history: {str(e)}")
    
    async def clear_user_watch_history(self, user_id: UUID) -> int:
        """
        Clear all watch history for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            int: Number of records deleted
        """
        try:
            # Get all non-deleted records for the user
            stmt = select(WatchHistory).where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.is_deleted == False
                )
            )
            result = await self.db.execute(stmt)
            records = result.scalars().all()
            
            # Soft delete all records
            deleted_count = 0
            for record in records:
                record.is_deleted = True
                record.updated_at = datetime.utcnow()
                deleted_count += 1
            
            await self.db.commit()
            return deleted_count
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error clearing user watch history: {str(e)}")
    
    async def get_watch_history_stats(self, user_id: UUID) -> dict:
        """
        Get watch history statistics for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            dict: Statistics about the user's watch history
        """
        try:
            # Get total count
            count_stmt = select(func.count(WatchHistory.id)).where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.is_deleted == False
                )
            )
            count_result = await self.db.execute(count_stmt)
            total_watched = count_result.scalar()
            
            # Get most recent watch
            recent_stmt = (
                select(WatchHistory)
                .where(
                    and_(
                        WatchHistory.user_id == user_id,
                        WatchHistory.is_deleted == False
                    )
                )
                .order_by(desc(WatchHistory.last_watched_at))
                .limit(1)
            )
            recent_result = await self.db.execute(recent_stmt)
            most_recent = recent_result.scalar_one_or_none()
            
            return {
                "total_watched": total_watched,
                "most_recent_watch": most_recent.last_watched_at if most_recent else None,
                "most_recent_title": most_recent.title if most_recent else None
            }
            
        except Exception as e:
            raise Exception(f"Error getting watch history stats: {str(e)}")


# Convenience functions for direct use
async def create_watch_history(
    db_session: AsyncSession,
    watch_history_data: WatchHistoryCreate
) -> WatchHistory:
    """Create a new watch history record."""
    service = WatchHistoryService(db_session)
    return await service.create_watch_history(watch_history_data)


async def get_watch_history_by_id(
    db_session: AsyncSession,
    history_id: UUID
) -> Optional[WatchHistory]:
    """Get a watch history record by ID."""
    service = WatchHistoryService(db_session)
    return await service.get_watch_history_by_id(history_id)


async def get_user_watch_history(
    db_session: AsyncSession,
    user_id: UUID,
    pagination: PaginationParams
) -> WatchHistoryListResponse:
    """Get paginated watch history for a user."""
    service = WatchHistoryService(db_session)
    return await service.get_user_watch_history(user_id, pagination)


async def update_watch_history(
    db_session: AsyncSession,
    history_id: UUID,
    update_data: WatchHistoryUpdate
) -> Optional[WatchHistory]:
    """Update a watch history record."""
    service = WatchHistoryService(db_session)
    return await service.update_watch_history(history_id, update_data)


async def delete_watch_history(
    db_session: AsyncSession,
    history_id: UUID
) -> bool:
    """Delete a watch history record."""
    service = WatchHistoryService(db_session)
    return await service.delete_watch_history(history_id)


async def clear_user_watch_history(
    db_session: AsyncSession,
    user_id: UUID
) -> int:
    """Clear all watch history for a user."""
    service = WatchHistoryService(db_session)
    return await service.clear_user_watch_history(user_id)
