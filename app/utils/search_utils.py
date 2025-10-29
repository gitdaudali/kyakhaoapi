from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, case, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content import Content, ContentType, Genre, ContentGenre
from app.schemas.unified_content import UnifiedContentItem, CategoryItem
from app.schemas.search import SimpleContentItem


def _to_unified_item(content: Content) -> UnifiedContentItem:
    return UnifiedContentItem(
        id=str(content.id),
        title=content.title or "",
        slug=content.slug or "",
        content_type=str(content.content_type),
        poster_url=content.poster_url or "",
        backdrop_url=content.backdrop_url or "",
        thumbnail_url=(content.thumbnail_grid or ""),
        description=content.description,
        release_date=(content.release_date.isoformat() if content.release_date else None),
        platform_rating=content.platform_rating or 0.0,
        platform_votes=content.platform_votes or 0,
        is_featured=bool(content.is_featured),
        is_trending=bool(content.is_trending),
    )


def _to_simple_item(content: Content) -> SimpleContentItem:
    # Map non-standard content types to standard ones
    content_type = str(content.content_type)
    if content_type in ["documentary", "anime"]:
        content_type = "movie"
    elif content_type not in ["movie", "tv_series", "episode"]:
        content_type = "movie"  # Default fallback
    
    return SimpleContentItem(
        id=str(content.id),
        title=content.title or "",
        content_type=content_type,
        poster_url=content.poster_url or "",
        platform_rating=content.platform_rating or 0.0,
        is_featured=bool(content.is_featured),
        is_trending=bool(content.is_trending),
    )


async def search_grouped(
    db: AsyncSession,
    q: str,
    page: int = 1,
    size: int = 20,
    content_type: Optional[str] = None,
    match: str = "smart",  # "smart" | "title"
) -> Tuple[Dict[str, List[SimpleContentItem]], int, Dict[str, List[SimpleContentItem]], List[CategoryItem]]:
    offset = (page - 1) * size
    
    # Build search conditions (smart = title + keywords [+ description]); title = title only
    search_term = f"%{q}%"

    base_conditions: List = [Content.is_deleted == False]  # noqa: E712
    if content_type:
        try:
            ct_enum = ContentType(content_type)
            base_conditions.append(Content.content_type == ct_enum)
        except Exception:
            pass

    if match == "title":
        # Search in titles only - this will match movies, TV shows, episodes, documentaries, etc.
        text_match_condition = Content.title.ilike(search_term)
        where_conditions = and_(*(base_conditions + [text_match_condition]))
        # Count
        count_query = select(func.count(Content.id)).where(where_conditions)
        total_result = await db.execute(count_query)
        total = int(total_result.scalar() or 0)
        # Query (no relevance ordering)
        query = (
            select(Content)
            .where(where_conditions)
            .options(
                selectinload(Content.genres),
                selectinload(Content.movie_files),
                selectinload(Content.seasons),
            )
            .order_by(desc(Content.platform_rating), desc(Content.total_views))
            .offset(offset)
            .limit(size)
        )
    else:
        # smart mode: title > search_keywords > description
        or_clauses = [
            Content.title.ilike(search_term),
        ]
        if hasattr(Content, "search_keywords"):
            or_clauses.append(Content.search_keywords.ilike(search_term))
        # Keep description low-weight; optional but included for recall
        or_clauses.append(Content.description.ilike(search_term))
        text_match_condition = or_(*or_clauses)
        where_conditions = and_(*(base_conditions + [text_match_condition]))

        relevance = case(
            (
                Content.title.ilike(search_term),
                100,
            ),
            (
                (Content.search_keywords.ilike(search_term) if hasattr(Content, "search_keywords") else False),
                60,
            ),
            (
                Content.description.ilike(search_term),
                20,
            ),
            else_=0,
        ).label("relevance")

        # Count
        count_query = select(func.count(Content.id)).where(where_conditions)
        total_result = await db.execute(count_query)
        total = int(total_result.scalar() or 0)

        # Query with relevance ordering (avoid NULLS LAST syntax pitfalls)
        query = (
            select(Content, relevance)
            .where(where_conditions)
            .options(
                selectinload(Content.genres),
                selectinload(Content.movie_files),
                selectinload(Content.seasons),
            )
            .order_by(desc(relevance), desc(Content.platform_rating), desc(Content.total_views))
            .offset(offset)
            .limit(size)
        )

    result = await db.execute(query)
    # In smart mode we selected (Content, relevance); scalars() returns first column (Content)
    contents = result.scalars().all()

    # Group by type (simple items)
    movies: List[SimpleContentItem] = []
    tv_series: List[SimpleContentItem] = []
    episodes: List[SimpleContentItem] = []

    for c in contents:
        item = _to_simple_item(c)
        # Use the original content type for proper grouping
        original_ct = str(c.content_type)
        if original_ct == "movie":
            movies.append(item)
        elif original_ct == "tv_series":
            tv_series.append(item)
        elif original_ct == "episode":
            episodes.append(item)
        else:
            # Map documentaries, anime, etc. to movies for display
            movies.append(item)

    grouped: Dict[str, List[SimpleContentItem]] = {
        "movies": movies,
        "tv_series": tv_series,
        "episodes": episodes,
    }

    # Sections derived from matched pool (top N from matched universe, not only current page)
    top_n = 10

    # Build section base where from same where_conditions
    # Top rated from matches
    top_rated_query = (
        select(Content)
        .where(where_conditions)
        .order_by(desc(Content.platform_rating), desc(Content.total_views))
        .limit(top_n)
    )

    # Trending from matches
    trending_query = (
        select(Content)
        .where(and_(where_conditions, Content.is_trending == True))  # noqa: E712
        .order_by(desc(Content.platform_rating), desc(Content.total_views))
        .limit(top_n)
    )

    # New releases from matches
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
    new_releases_query = (
        select(Content)
        .where(and_(where_conditions, Content.release_date >= thirty_days_ago))
        .order_by(desc(Content.release_date), desc(Content.platform_rating))
        .limit(top_n)
    )

    top_rated_result = await db.execute(top_rated_query)
    top_rated = [_to_simple_item(c) for c in top_rated_result.scalars().all()]

    trending_result = await db.execute(trending_query)
    trending = [_to_simple_item(c) for c in trending_result.scalars().all()]

    new_releases_result = await db.execute(new_releases_query)
    new_releases = [_to_simple_item(c) for c in new_releases_result.scalars().all()]

    # Categories from matched content's genres
    genre_counter: Counter[str] = Counter()
    genre_info: Dict[str, Genre] = {}
    for c in contents:
        # Join through ContentGenre if needed is handled via separate queries elsewhere; here we count names available on Content.genres via selectinload
        if hasattr(c, "genres") and c.genres:
            for g in c.genres:
                if getattr(g, "is_deleted", False):
                    continue
                genre_counter[g.name] += 1
                genre_info[g.name] = g

    categories: List[CategoryItem] = []
    for name, count in genre_counter.most_common(10):
        g = genre_info[name]
        categories.append(
            CategoryItem(
                id=str(g.id),
                name=g.name,
                slug=g.slug,
                description=g.description,
                icon_url=getattr(g, "cover_image_url", None),
                content_count=count,
            )
        )

    sections: Dict[str, List[SimpleContentItem]] = {
        "top_rated": top_rated,
        "trending": trending,
        "new_releases": new_releases,
    }

    return grouped, total, sections, categories


