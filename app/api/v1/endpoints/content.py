from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.messages import (
    CAST_CREW_SUCCESS,
    CAST_LIST_SUCCESS,
    CAST_NOT_FOUND,
    CONTENT_FEATURED_SUCCESS,
    CONTENT_LIST_SUCCESS,
    CONTENT_NOT_FOUND,
    CONTENT_TRENDING_SUCCESS,
    CREW_LIST_SUCCESS,
    CREW_NOT_FOUND,
    GENRE_LIST_SUCCESS,
    GENRE_NOT_FOUND,
    INVALID_FILTERS,
    INVALID_PAGINATION,
    INVALID_SORT_PARAMS,
)
from app.schemas.content import (
    CastCrewResponse,
    CastFilters,
    CastListResponse,
    Content,
    ContentDetail,
    ContentFilters,
    ContentList,
    ContentListResponse,
    CrewFilters,
    CrewListResponse,
    Genre,
    GenreFilters,
    GenreListResponse,
    PaginatedResponse,
    PaginationParams,
)
from app.utils.content_utils import (
    calculate_pagination_info,
    get_content_by_id,
    get_content_cast,
    get_content_cast_crew,
    get_content_crew,
    get_content_list,
    get_featured_content,
    get_genre_by_id,
    get_genre_by_slug,
    get_genres_list,
    get_trending_content,
)

router = APIRouter()


@router.get("/featured", response_model=ContentListResponse)
async def get_featured_contents(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Page size",
    ),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    rating: Optional[str] = Query(None, description="Filter by rating"),
    genre_ids: Optional[str] = Query(None, description="Comma-separated genre IDs"),
    year: Optional[int] = Query(None, description="Filter by release year"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get featured content with pagination and filtering.
    Returns a paginated list of featured content that is published and available to users.
    """
    try:
        genre_id_list = None
        if genre_ids:
            try:
                genre_id_list = [UUID(gid.strip()) for gid in genre_ids.split(",")]
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_FILTERS
                )

        filters = ContentFilters(
            content_type=content_type,
            rating=rating,
            genre_ids=genre_id_list,
            year=year,
            search=search,
            is_featured=True,
        )

        pagination = PaginationParams(
            page=page, size=size, sort_by=sort_by, sort_order=sort_order
        )

        contents, total = await get_featured_content(db, pagination, filters)

        pagination_info = calculate_pagination_info(page, size, total)

        return ContentListResponse(items=contents, **pagination_info)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving featured content: {str(e)}",
        )


@router.get("/trending", response_model=ContentListResponse)
async def get_trending_contents(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Page size",
    ),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    rating: Optional[str] = Query(None, description="Filter by rating"),
    genre_ids: Optional[str] = Query(None, description="Comma-separated genre IDs"),
    year: Optional[int] = Query(None, description="Filter by release year"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: str = Query("view_count", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get trending content with pagination and filtering.
    Returns a paginated list of trending content that is published and available to users.
    """
    try:
        genre_id_list = None
        if genre_ids:
            try:
                genre_id_list = [UUID(gid.strip()) for gid in genre_ids.split(",")]
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_FILTERS
                )

        filters = ContentFilters(
            content_type=content_type,
            rating=rating,
            genre_ids=genre_id_list,
            year=year,
            search=search,
            is_trending=True,
        )

        pagination = PaginationParams(
            page=page, size=size, sort_by=sort_by, sort_order=sort_order
        )

        contents, total = await get_trending_content(db, pagination, filters)

        pagination_info = calculate_pagination_info(page, size, total)

        return ContentListResponse(items=contents, **pagination_info)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving trending content: {str(e)}",
        )


@router.get("/", response_model=ContentListResponse)
async def get_contents(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Page size",
    ),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    rating: Optional[str] = Query(None, description="Filter by rating"),
    genre_ids: Optional[str] = Query(None, description="Comma-separated genre IDs"),
    is_featured: Optional[bool] = Query(None, description="Filter featured content"),
    is_trending: Optional[bool] = Query(None, description="Filter trending content"),
    year: Optional[int] = Query(None, description="Filter by release year"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get content list with pagination and filtering.
    Returns a paginated list of content with various filtering options.
    """
    try:
        # Parse genre IDs
        genre_id_list = None
        if genre_ids:
            try:
                genre_id_list = [UUID(gid.strip()) for gid in genre_ids.split(",")]
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_FILTERS
                )

        filters = ContentFilters(
            content_type=content_type,
            status=status,
            rating=rating,
            genre_ids=genre_id_list,
            is_featured=is_featured,
            is_trending=is_trending,
            year=year,
            search=search,
        )

        pagination = PaginationParams(
            page=page, size=size, sort_by=sort_by, sort_order=sort_order
        )

        contents, total = await get_content_list(db, pagination, filters)

        pagination_info = calculate_pagination_info(page, size, total)

        return ContentListResponse(items=contents, **pagination_info)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving content list: {str(e)}",
        )


@router.get("/{content_id}", response_model=ContentDetail)
async def get_content(
    content_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get content by ID.
    Returns detailed information about a specific content item including cast, crew, and genres.
    """
    try:
        content = await get_content_by_id(db, content_id, include_relationships=True)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        return content

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving content: {str(e)}",
        )


@router.get("/genres/", response_model=GenreListResponse)
async def get_genres(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Page size",
    ),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    sort_by: str = Query("name", description="Sort field"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get genres list with pagination and filtering.
    Returns a paginated list of genres with optional filtering.
    """
    try:
        filters = GenreFilters(is_active=is_active, search=search)

        pagination = PaginationParams(
            page=page, size=size, sort_by=sort_by, sort_order=sort_order
        )

        genres, total = await get_genres_list(db, pagination, filters)

        pagination_info = calculate_pagination_info(page, size, total)

        return GenreListResponse(items=genres, **pagination_info)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving genres: {str(e)}",
        )


@router.get("/genres/{genre_id}", response_model=Genre)
async def get_genre(
    genre_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get genre by ID.

    Returns detailed information about a specific genre.
    """
    try:
        genre = await get_genre_by_id(db, genre_id)
        if not genre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=GENRE_NOT_FOUND
            )

        return genre

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving genre: {str(e)}",
        )


@router.get("/genres/slug/{slug}", response_model=Genre)
async def get_genre_by_slug_endpoint(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get genre by slug.

    Returns detailed information about a specific genre using its slug.
    """
    try:
        genre = await get_genre_by_slug(db, slug)
        if not genre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=GENRE_NOT_FOUND
            )

        return genre

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving genre: {str(e)}",
        )


@router.get("/{content_id}/cast", response_model=CastListResponse)
async def get_content_cast_endpoint(
    content_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Page size",
    ),
    is_main_cast: Optional[bool] = Query(
        None, description="Filter by main cast status"
    ),
    search: Optional[str] = Query(
        None, description="Search in character name or person name"
    ),
    department: Optional[str] = Query(None, description="Filter by department"),
    sort_by: str = Query("cast_order", description="Sort field"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get cast for a specific content with pagination and filtering.
    Returns a paginated list of cast members for the specified content.
    """
    try:
        content = await get_content_by_id(db, content_id, include_relationships=False)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        filters = CastFilters(
            is_main_cast=is_main_cast,
            search=search,
            department=department,
        )

        pagination = PaginationParams(
            page=page, size=size, sort_by=sort_by, sort_order=sort_order
        )

        cast_members, total = await get_content_cast(
            db, content_id, pagination, filters
        )

        pagination_info = calculate_pagination_info(page, size, total)

        return CastListResponse(items=cast_members, **pagination_info)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cast: {str(e)}",
        )


@router.get("/{content_id}/crew", response_model=CrewListResponse)
async def get_content_crew_endpoint(
    content_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Page size",
    ),
    department: Optional[str] = Query(None, description="Filter by department"),
    job_title: Optional[str] = Query(None, description="Filter by job title"),
    search: Optional[str] = Query(
        None, description="Search in job title or person name"
    ),
    sort_by: str = Query("credit_order", description="Sort field"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get crew for a specific content with pagination and filtering.
    Returns a paginated list of crew members for the specified content.
    """
    try:
        # Verify content exists
        content = await get_content_by_id(db, content_id, include_relationships=False)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        filters = CrewFilters(
            department=department,
            job_title=job_title,
            search=search,
        )

        pagination = PaginationParams(
            page=page, size=size, sort_by=sort_by, sort_order=sort_order
        )

        crew_members, total = await get_content_crew(
            db, content_id, pagination, filters
        )

        pagination_info = calculate_pagination_info(page, size, total)

        return CrewListResponse(items=crew_members, **pagination_info)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving crew: {str(e)}",
        )


@router.get("/{content_id}/cast-crew", response_model=CastCrewResponse)
async def get_content_cast_crew_endpoint(
    content_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get both cast and crew for a specific content.
    Returns both cast and crew members for the specified content in a single response.
    """
    try:
        content = await get_content_by_id(db, content_id, include_relationships=False)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        cast_members, crew_members = await get_content_cast_crew(db, content_id)

        return CastCrewResponse(cast=cast_members, crew=crew_members)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cast and crew: {str(e)}",
        )
