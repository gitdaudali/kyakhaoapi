from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.models.moviesource import MovieSource
from app.schemas.admin import (
    MovieSourceAdminCreate,
    MovieSourceAdminListResponse,
    MovieSourceAdminQueryParams,
    MovieSourceAdminResponse,
    MovieSourceAdminUpdate,
)
from app.utils.content_utils import calculate_pagination_info

router = APIRouter()

# Custom messages for Movie Source
MOVIE_SOURCE_CREATED = "Movie source created successfully"
MOVIE_SOURCE_UPDATED = "Movie source updated successfully"
MOVIE_SOURCE_DELETED = "Movie source deleted successfully"
MOVIE_SOURCE_NOT_FOUND = "Movie source not found"


@router.post("/", response_model=MovieSourceAdminResponse)
async def create_movie_source_admin(
    current_user: AdminUser,
    movie_source_data: MovieSourceAdminCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new movie source (Admin only).
    """
    try:
        # Create MovieSource instance
        movie_source = MovieSource(
            source=movie_source_data.source,
            destination=movie_source_data.destination,
            active=movie_source_data.active,
        )
        
        db.add(movie_source)
        await db.commit()
        await db.refresh(movie_source)
        
        return MovieSourceAdminResponse.model_validate(movie_source)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating movie source: {str(e)}",
        )


@router.get("/", response_model=MovieSourceAdminListResponse)
async def get_movie_sources_admin(
    current_user: AdminUser,
    query_params: MovieSourceAdminQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get paginated list of movie sources for admin.
    """
    try:
        # Build query
        query = select(MovieSource).where(MovieSource.is_deleted == False)
        
        # Apply filters
        if query_params.search:
            search_filter = or_(
                MovieSource.source.ilike(f"%{query_params.search}%"),
                MovieSource.destination.ilike(f"%{query_params.search}%"),
            )
            query = query.where(search_filter)
        
        if query_params.active is not None:
            query = query.where(MovieSource.active == query_params.active)
        
        # Apply sorting
        sort_column = getattr(MovieSource, query_params.sort_by, MovieSource.created_at)
        if query_params.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Get total count
        count_query = select(func.count(MovieSource.id)).where(MovieSource.is_deleted == False)
        if query_params.search:
            count_query = count_query.where(search_filter)
        if query_params.active is not None:
            count_query = count_query.where(MovieSource.active == query_params.active)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (query_params.page - 1) * query_params.size
        query = query.offset(offset).limit(query_params.size)
        
        # Execute query
        result = await db.execute(query)
        movie_sources = result.scalars().all()
        
        # Calculate pagination info
        pagination_info = calculate_pagination_info(
            query_params.page, query_params.size, total
        )
        
        return MovieSourceAdminListResponse(
            items=[MovieSourceAdminResponse.model_validate(ms) for ms in movie_sources],
            total=pagination_info["total"],
            page=pagination_info["page"],
            size=pagination_info["size"],
            pages=pagination_info["pages"],
            has_next=pagination_info["has_next"],
            has_prev=pagination_info["has_prev"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving movie sources list: {str(e)}",
        )


@router.get("/{movie_source_id}", response_model=MovieSourceAdminResponse)
async def get_movie_source_admin(
    movie_source_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get movie source by ID for admin.
    """
    try:
        query = select(MovieSource).where(
            and_(MovieSource.id == movie_source_id, MovieSource.is_deleted == False)
        )
        result = await db.execute(query)
        movie_source = result.scalar_one_or_none()
        
        if not movie_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=MOVIE_SOURCE_NOT_FOUND,
            )
        
        return MovieSourceAdminResponse.model_validate(movie_source)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving movie source: {str(e)}",
        )


@router.put("/{movie_source_id}", response_model=MovieSourceAdminResponse)
async def update_movie_source_admin(
    movie_source_id: UUID,
    current_user: AdminUser,
    movie_source_data: MovieSourceAdminUpdate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update movie source (Admin only).
    """
    try:
        # Get existing movie source
        query = select(MovieSource).where(
            and_(MovieSource.id == movie_source_id, MovieSource.is_deleted == False)
        )
        result = await db.execute(query)
        movie_source = result.scalar_one_or_none()
        
        if not movie_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=MOVIE_SOURCE_NOT_FOUND,
            )
        
        # Update fields - only update fields that are explicitly provided and not None
        update_data = movie_source_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            # Skip None values to avoid setting required fields to null
            if value is not None:
                setattr(movie_source, field, value)
        
        await db.commit()
        await db.refresh(movie_source)
        
        return MovieSourceAdminResponse.model_validate(movie_source)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating movie source: {str(e)}",
        )


@router.delete("/{movie_source_id}")
async def delete_movie_source_admin(
    movie_source_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete movie source (Admin only).
    """
    try:
        # Get existing movie source
        query = select(MovieSource).where(
            and_(MovieSource.id == movie_source_id, MovieSource.is_deleted == False)
        )
        result = await db.execute(query)
        movie_source = result.scalar_one_or_none()
        
        if not movie_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=MOVIE_SOURCE_NOT_FOUND,
            )
        
        # Soft delete
        movie_source.is_deleted = True
        await db.commit()
        
        return {"message": MOVIE_SOURCE_DELETED}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting movie source: {str(e)}",
        )


@router.patch("/{movie_source_id}/toggle-active")
async def toggle_movie_source_active_admin(
    movie_source_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Toggle movie source active status (Admin only).
    """
    try:
        # Get existing movie source
        query = select(MovieSource).where(
            and_(MovieSource.id == movie_source_id, MovieSource.is_deleted == False)
        )
        result = await db.execute(query)
        movie_source = result.scalar_one_or_none()
        
        if not movie_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=MOVIE_SOURCE_NOT_FOUND,
            )
        
        # Toggle active status
        movie_source.active = not movie_source.active
        await db.commit()
        await db.refresh(movie_source)
        
        message = "Movie source activated" if movie_source.active else "Movie source deactivated"
        
        return {
            "message": message,
            "movie_source": MovieSourceAdminResponse.model_validate(movie_source),
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling movie source active status: {str(e)}",
        )