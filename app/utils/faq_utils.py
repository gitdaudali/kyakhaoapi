"""
FAQ utility functions for FAQ management and validation.
"""

from typing import List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.faq import FAQ


async def get_faq_by_question(
    session: AsyncSession, question: str, include_deleted: bool = False
) -> Optional[FAQ]:
    """
    Get FAQ by question text.

    Args:
        session: Database session
        question: FAQ question text
        include_deleted: Whether to include soft-deleted FAQs

    Returns:
        FAQ object if found, None otherwise
    """
    query = select(FAQ).where(FAQ.question == question)
    if not include_deleted:
        query = query.where(FAQ.is_deleted == False)

    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_faq_by_id(
    session: AsyncSession, faq_id: UUID, include_deleted: bool = False
) -> Optional[FAQ]:
    """
    Get FAQ by ID.

    Args:
        session: Database session
        faq_id: FAQ UUID
        include_deleted: Whether to include soft-deleted FAQs

    Returns:
        FAQ object if found, None otherwise
    """
    query = select(FAQ).where(FAQ.id == faq_id)
    if not include_deleted:
        query = query.where(FAQ.is_deleted == False)

    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_faq_by_id_or_404(
    session: AsyncSession, faq_id: UUID, include_deleted: bool = False
) -> FAQ:
    """
    Get FAQ by ID or raise 404 if not found.

    Args:
        session: Database session
        faq_id: FAQ UUID
        include_deleted: Whether to include soft-deleted FAQs

    Returns:
        FAQ object

    Raises:
        HTTPException: If FAQ not found
    """
    faq = await get_faq_by_id(session, faq_id, include_deleted)
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found",
        )
    return faq


async def get_published_faqs(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
) -> Tuple[List[FAQ], int]:
    """
    Get published FAQs with pagination and optional category filter.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        category: Optional category filter

    Returns:
        Tuple of (list of FAQs, total count)
    """
    # Build base query for published FAQs only
    base_query = select(FAQ).where(
        FAQ.is_published == True,
        FAQ.is_deleted == False
    )

    # Filter by category if provided
    if category:
        base_query = base_query.where(FAQ.category == category)

    # Get total count
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Get FAQs ordered by order field and creation date
    query = base_query.order_by(FAQ.order, FAQ.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    faqs = result.scalars().all()

    return list(faqs), total


async def get_all_faqs(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[FAQ], int]:
    """
    Get all FAQs (including unpublished) for admin dashboard.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of FAQs, total count)
    """
    # Get total count
    count_query = select(func.count()).select_from(FAQ).where(FAQ.is_deleted == False)
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Get FAQs
    query = (
        select(FAQ)
        .where(FAQ.is_deleted == False)
        .order_by(FAQ.order, FAQ.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(query)
    faqs = result.scalars().all()

    return list(faqs), total


async def soft_delete_faq(session: AsyncSession, faq_id: UUID) -> FAQ:
    """
    Soft delete an FAQ.

    Args:
        session: Database session
        faq_id: FAQ UUID

    Returns:
        Deleted FAQ object

    Raises:
        HTTPException: If FAQ not found
    """
    faq = await get_faq_by_id_or_404(session, faq_id)
    faq.is_deleted = True
    return faq

