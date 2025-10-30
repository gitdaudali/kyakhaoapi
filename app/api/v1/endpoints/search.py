from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.search import MainSearchResponse
from app.utils.search_utils import search_grouped


router = APIRouter(tags=["Search"], responses={404: {"description": "Not found"}})


@router.get("/", response_model=MainSearchResponse)
async def main_search(
    q: str = Query(..., min_length=2, max_length=100, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    content_type: str | None = Query(None, description="movie | tv_series | episode"),
    year: int | None = Query(None, description="Filter by release year"),
    rating_min: float | None = Query(None, ge=0, le=10, description="Minimum rating filter"),
    genre: str | None = Query(None, description="Filter by genre name"),
    match: str = Query("title", pattern="^(smart|title)$", description="Search matching mode: smart|title"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Main search API that returns paginated matched content organized in sections.
    Like Netflix - shows everything that matches your search in organized categories.
    
    Supports pagination with page and size parameters for efficient handling of large result sets.
    """
    try:
        # Fetch paginated matched content
        grouped, total, sections, categories = await search_grouped(
            db=db,
            q=q,
            page=page,
            size=size,
            content_type=content_type,
            match=match,
        )

        # Apply additional filters if provided
        if year or rating_min or genre:
            grouped = await apply_advanced_filters(db, grouped, year, rating_min, genre)

        # Calculate pagination info
        total_pages = (total + size - 1) // size  # Ceiling division
        has_next = page < total_pages
        has_previous = page > 1

        return MainSearchResponse(
            query=q.strip(),
            total_results=total,
            page=page,
            size=size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
            results=grouped,
            sections={
                "top_rated": sections.get("top_rated", []),
                "trending": sections.get("trending", []),
                "new_releases": sections.get("new_releases", []),
                "categories": categories,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {e}",
        )


async def apply_advanced_filters(db: AsyncSession, grouped: dict, year: int = None, rating_min: float = None, genre: str = None):
    """Apply advanced filters to grouped results"""
    # This is a simplified filter - in production, you'd want to filter at database level
    filtered = {"movies": [], "tv_series": [], "episodes": []}
    
    for content_type, items in grouped.items():
        for item in items:
            # Apply year filter
            if year and item.release_date:
                item_year = int(item.release_date.split('-')[0]) if item.release_date else None
                if item_year and item_year != year:
                    continue
            
            # Apply rating filter
            if rating_min and item.platform_rating < rating_min:
                continue
            
            # Apply genre filter (simplified - would need genre info in item)
            if genre and genre.lower() not in (item.title or "").lower():
                continue
            
            filtered[content_type].append(item)
    
    return filtered