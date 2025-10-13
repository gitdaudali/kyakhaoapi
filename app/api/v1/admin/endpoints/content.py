from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.core.messages import (
    CONTENT_ALREADY_EXISTS,
    CONTENT_CREATED,
    CONTENT_DELETED,
    CONTENT_FEATURED,
    CONTENT_NOT_FOUND,
    CONTENT_PUBLISHED,
    CONTENT_TRENDING,
    CONTENT_UNFEATURED,
    CONTENT_UNPUBLISHED,
)
from app.schemas.admin import (
    ContentAdminCreate,
    ContentAdminListResponse,
    ContentAdminQueryParams,
    ContentAdminResponse,
    ContentAdminUpdate,
    TVShowAdminCreate,
)
from app.utils.admin_utils import (
    create_content,
    delete_content,
    get_content_admin_by_id,
    get_contents_admin_list,
    publish_content,
    toggle_content_featured,
    toggle_content_trending,
    unpublish_content,
    update_content,
)
from app.utils.content_utils import calculate_pagination_info

router = APIRouter()


# =============================================================================
# ADMIN TV SHOW SPECIFIC ENDPOINTS (MUST BE FIRST - Before generic content routes)
# =============================================================================
# These endpoints are for admin management of TV shows specifically
# They provide CRUD operations for TV shows, seasons, and episodes
# NOTE: These MUST be defined BEFORE the generic content routes (/{content_id})
# to avoid route matching conflicts where "tv-shows" is interpreted as a UUID

@router.get("/tv-shows", response_model=ContentAdminListResponse)
async def get_admin_tv_shows(
    current_user: AdminUser,
    query_params: ContentAdminQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get TV shows list for admin management.
    This endpoint automatically filters for content_type=TV_SERIES
    so admins can manage TV shows separately from movies.
    """
    try:
        # Force content_type to be tv_series to only show TV shows
        query_params.content_type = "tv_series"
        
        # Use the same function as regular admin content list
        contents, total = await get_contents_admin_list(db, query_params)
        pagination_info = calculate_pagination_info(
            query_params.page, query_params.size, total
        )

        # Convert SQLAlchemy objects to dictionaries (same as regular admin endpoint)
        serialized_contents = []
        for content in contents:
            content_dict = {
                "id": content.id,
                "title": content.title,
                "slug": content.slug,
                "description": content.description,
                "tagline": content.tagline,
                "content_type": content.content_type,
                "status": content.status,
                "content_rating": content.content_rating,
                "poster_url": content.poster_url,
                "backdrop_url": content.backdrop_url,
                "trailer_url": content.trailer_url,
                "logo_url": content.logo_url,
                "release_date": content.release_date,
                "premiere_date": content.premiere_date,
                "end_date": content.end_date,
                "runtime": content.runtime,
                "language": content.language,
                "original_language": content.original_language,
                "total_seasons": content.total_seasons,
                "total_episodes": content.total_episodes,
                "is_ongoing": content.is_ongoing,
                "is_featured": content.is_featured,
                "is_trending": content.is_trending,
                "is_new_release": content.is_new_release,
                "is_premium": content.is_premium,
                "available_from": content.available_from,
                "available_until": content.available_until,
                "total_views": content.total_views,
                "likes_count": content.likes_count,
                "reviews_count": content.reviews_count,
                "platform_rating": content.platform_rating,
                "platform_votes": content.platform_votes,
                "created_at": content.created_at,
                "updated_at": content.updated_at,
                # Convert relationships to dictionaries
                "genres": [
                    {"id": genre.id, "name": genre.name, "slug": genre.slug}
                    for genre in content.genres
                ],
                "seasons": [
                    {
                        "id": season.id,
                        "season_number": season.season_number,
                        "title": season.title,
                    }
                    for season in content.seasons
                ],
                "cast": [
                    {
                        "person_id": cast.person_id,
                        "character_name": cast.character_name,
                        "job_title": cast.job_title,
                    }
                    for cast in content.cast
                ],
                "crew": [
                    {
                        "person_id": crew.person_id,
                        "job_title": crew.job_title,
                        "department": crew.department,
                    }
                    for crew in content.crew
                ],
                "movie_files": [
                    {
                        "id": file.id,
                        "quality_level": file.quality_level,
                        "file_url": file.file_url,
                    }
                    for file in content.movie_files
                ],
            }
            serialized_contents.append(content_dict)

        return ContentAdminListResponse(
            items=serialized_contents,
            total=pagination_info["total"],
            page=pagination_info["page"],
            size=pagination_info["size"],
            pages=pagination_info["pages"],
            has_next=pagination_info["has_next"],
            has_prev=pagination_info["has_prev"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving TV shows list: {str(e)}",
        )


@router.post("/tv-shows", response_model=ContentAdminResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_tv_show(
    current_user: AdminUser,
    tv_show_data: TVShowAdminCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new TV show (Admin only).
    This endpoint is specifically for creating TV shows.
    The content_type will be automatically set to 'tv_series'.
    """
    try:
        # Convert to dict and force content_type to be tv_series
        content_data = tv_show_data.model_dump()
        content_data["content_type"] = "tv_series"
        
        # Create the TV show using the same function as regular content
        content = await create_content(db, content_data)

        # Convert SQLAlchemy object to dictionary for proper serialization
        content_dict = {
            "id": content.id,
            "title": content.title,
            "slug": content.slug,
            "description": content.description,
            "tagline": content.tagline,
            "content_type": content.content_type,
            "status": content.status,
            "content_rating": content.content_rating,
            "poster_url": content.poster_url,
            "backdrop_url": content.backdrop_url,
            "trailer_url": content.trailer_url,
            "logo_url": content.logo_url,
            "release_date": content.release_date,
            "premiere_date": content.premiere_date,
            "end_date": content.end_date,
            "runtime": content.runtime,
            "language": content.language,
            "original_language": content.original_language,
            "total_seasons": content.total_seasons,
            "total_episodes": content.total_episodes,
            "is_ongoing": content.is_ongoing,
            "is_featured": content.is_featured,
            "is_trending": content.is_trending,
            "is_new_release": content.is_new_release,
            "is_premium": content.is_premium,
            "available_from": content.available_from,
            "available_until": content.available_until,
            "total_views": content.total_views,
            "likes_count": content.likes_count,
            "reviews_count": content.reviews_count,
            "platform_rating": content.platform_rating,
            "platform_votes": content.platform_votes,
            "keywords": content.keywords,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            # Convert relationships to dictionaries
            "genres": [
                {"id": genre.id, "name": genre.name, "slug": genre.slug}
                for genre in content.genres
            ],
            "seasons": [
                {
                    "id": season.id,
                    "season_number": season.season_number,
                    "title": season.title,
                }
                for season in content.seasons
            ],
            "cast": [
                {
                    "person_id": cast.person_id,
                    "character_name": cast.character_name,
                    "job_title": cast.job_title,
                }
                for cast in content.cast
            ],
            "crew": [
                {
                    "person_id": crew.person_id,
                    "job_title": crew.job_title,
                    "department": crew.department,
                }
                for crew in content.crew
            ],
            "movie_files": [
                {
                    "id": file.id,
                    "quality_level": file.quality_level,
                    "file_url": file.file_url,
                }
                for file in content.movie_files
            ],
        }
        return ContentAdminResponse.model_validate(content_dict)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating TV show: {str(e)}",
        )


@router.put("/tv-shows/{tv_show_id}", response_model=ContentAdminResponse)
async def update_admin_tv_show(
    current_user: AdminUser,
    tv_show_id: UUID,
    tv_show_data: ContentAdminUpdate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update TV show (Admin only).
    Updates an existing TV show. Only provided fields will be updated.
    """
    try:
        # First verify it's a TV show
        existing_content = await get_content_admin_by_id(db, tv_show_id)
        if not existing_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTENT_NOT_FOUND
            )
        
        if existing_content.content_type != "tv_series":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content is not a TV show"
            )
        
        # Filter out None values
        update_data = {k: v for k, v in tv_show_data.model_dump().items() if v is not None}
        
        # Update the TV show
        content = await update_content(db, tv_show_id, update_data)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTENT_NOT_FOUND
            )

        # Convert SQLAlchemy object to dictionary for proper serialization
        content_dict = {
            "id": content.id,
            "title": content.title,
            "slug": content.slug,
            "description": content.description,
            "tagline": content.tagline,
            "content_type": content.content_type,
            "status": content.status,
            "content_rating": content.content_rating,
            "poster_url": content.poster_url,
            "backdrop_url": content.backdrop_url,
            "trailer_url": content.trailer_url,
            "logo_url": content.logo_url,
            "release_date": content.release_date,
            "premiere_date": content.premiere_date,
            "end_date": content.end_date,
            "runtime": content.runtime,
            "language": content.language,
            "original_language": content.original_language,
            "total_seasons": content.total_seasons,
            "total_episodes": content.total_episodes,
            "is_ongoing": content.is_ongoing,
            "is_featured": content.is_featured,
            "is_trending": content.is_trending,
            "is_new_release": content.is_new_release,
            "is_premium": content.is_premium,
            "available_from": content.available_from,
            "available_until": content.available_until,
            "total_views": content.total_views,
            "likes_count": content.likes_count,
            "reviews_count": content.reviews_count,
            "platform_rating": content.platform_rating,
            "platform_votes": content.platform_votes,
            "keywords": content.keywords,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            # Convert relationships to dictionaries
            "genres": [
                {"id": genre.id, "name": genre.name, "slug": genre.slug}
                for genre in content.genres
            ],
            "seasons": [
                {
                    "id": season.id,
                    "season_number": season.season_number,
                    "title": season.title,
                }
                for season in content.seasons
            ],
            "cast": [
                {
                    "person_id": cast.person_id,
                    "character_name": cast.character_name,
                    "job_title": cast.job_title,
                }
                for cast in content.cast
            ],
            "crew": [
                {
                    "person_id": crew.person_id,
                    "job_title": crew.job_title,
                    "department": crew.department,
                }
                for crew in content.crew
            ],
            "movie_files": [
                {
                    "id": file.id,
                    "quality_level": file.quality_level,
                    "file_url": file.file_url,
                }
                for file in content.movie_files
            ],
        }
        return ContentAdminResponse.model_validate(content_dict)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating TV show: {str(e)}",
        )


@router.delete("/tv-shows/{tv_show_id}")
async def delete_admin_tv_show(
    current_user: AdminUser,
    tv_show_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete TV show (Admin only).
    Soft deletes a TV show (sets is_deleted=True).
    """
    try:
        # First verify it's a TV show
        existing_content = await get_content_admin_by_id(db, tv_show_id)
        if not existing_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTENT_NOT_FOUND
            )
        
        if existing_content.content_type != "tv_series":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content is not a TV show"
            )
        
        # Delete the TV show
        success = await delete_content(db, tv_show_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTENT_NOT_FOUND
            )
        
        return {"message": CONTENT_DELETED, "id": str(tv_show_id)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting TV show: {str(e)}",
        )


# NOTE: ALL other TV show routes (GET /tv-shows/{tv_show_id}, seasons, episodes) 
# are defined below after the generic content routes.
# Only the /tv-shows CRUD routes (GET, POST, PUT, DELETE) need to be here at the top to avoid conflicts.

# =============================================================================
# END TV SHOW ROUTES - NOW CONTINUE WITH GENERIC CONTENT ROUTES
# =============================================================================


@router.post("/", response_model=ContentAdminResponse)
async def create_content_admin(
    current_user: AdminUser,
    content_data: ContentAdminCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new content (Admin only).
    """
    try:
        content = await create_content(db, content_data.model_dump())

        # Convert SQLAlchemy object to dictionary for proper serialization
        content_dict = {
            "id": content.id,
            "title": content.title,
            "slug": content.slug,
            "description": content.description,
            "tagline": content.tagline,
            "content_type": content.content_type,
            "status": content.status,
            "content_rating": content.content_rating,
            "poster_url": content.poster_url,
            "backdrop_url": content.backdrop_url,
            "trailer_url": content.trailer_url,
            "logo_url": content.logo_url,
            "release_date": content.release_date,
            "premiere_date": content.premiere_date,
            "end_date": content.end_date,
            "runtime": content.runtime,
            "language": content.language,
            "original_language": content.original_language,
            "total_seasons": content.total_seasons,
            "total_episodes": content.total_episodes,
            "is_ongoing": content.is_ongoing,
            "is_featured": content.is_featured,
            "is_trending": content.is_trending,
            "is_new_release": content.is_new_release,
            "is_premium": content.is_premium,
            "available_from": content.available_from,
            "available_until": content.available_until,
            "total_views": content.total_views,
            "likes_count": content.likes_count,
            "reviews_count": content.reviews_count,
            "platform_rating": content.platform_rating,
            "platform_votes": content.platform_votes,
            "keywords": content.keywords,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            # Convert relationships to dictionaries
            "genres": [
                {"id": genre.id, "name": genre.name, "slug": genre.slug}
                for genre in content.genres
            ],
            "seasons": [
                {
                    "id": season.id,
                    "season_number": season.season_number,
                    "title": season.title,
                }
                for season in content.seasons
            ],
            "cast": [
                {
                    "person_id": cast.person_id,
                    "character_name": cast.character_name,
                    "job_title": cast.job_title,
                }
                for cast in content.cast
            ],
            "crew": [
                {
                    "person_id": crew.person_id,
                    "job_title": crew.job_title,
                    "department": crew.department,
                }
                for crew in content.crew
            ],
            "movie_files": [
                {
                    "id": file.id,
                    "quality_level": file.quality_level,
                    "file_url": file.file_url,
                }
                for file in content.movie_files
            ],
        }
        return ContentAdminResponse.model_validate(content_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating content: {str(e)}",
        )


@router.get("/", response_model=ContentAdminListResponse)
async def get_contents_admin(
    current_user: AdminUser,
    query_params: ContentAdminQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get paginated list of content for admin.
    """
    try:
        contents, total = await get_contents_admin_list(db, query_params)
        pagination_info = calculate_pagination_info(
            query_params.page, query_params.size, total
        )

        # Convert SQLAlchemy objects to dictionaries for proper serialization
        serialized_contents = []
        for content in contents:
            content_dict = {
                "id": content.id,
                "title": content.title,
                "slug": content.slug,
                "description": content.description,
                "tagline": content.tagline,
                "content_type": content.content_type,
                "status": content.status,
                "content_rating": content.content_rating,
                "poster_url": content.poster_url,
                "backdrop_url": content.backdrop_url,
                "trailer_url": content.trailer_url,
                "logo_url": content.logo_url,
                "release_date": content.release_date,
                "premiere_date": content.premiere_date,
                "end_date": content.end_date,
                "runtime": content.runtime,
                "language": content.language,
                "original_language": content.original_language,
                "total_seasons": content.total_seasons,
                "total_episodes": content.total_episodes,
                "is_ongoing": content.is_ongoing,
                "is_featured": content.is_featured,
                "is_trending": content.is_trending,
                "is_new_release": content.is_new_release,
                "is_premium": content.is_premium,
                "available_from": content.available_from,
                "available_until": content.available_until,
                "total_views": content.total_views,
                "likes_count": content.likes_count,
                "reviews_count": content.reviews_count,
                "platform_rating": content.platform_rating,
                "platform_votes": content.platform_votes,
                "created_at": content.created_at,
                "updated_at": content.updated_at,
                # Convert relationships to dictionaries
                "genres": [
                    {"id": genre.id, "name": genre.name, "slug": genre.slug}
                    for genre in content.genres
                ],
                "seasons": [
                    {
                        "id": season.id,
                        "season_number": season.season_number,
                        "title": season.title,
                    }
                    for season in content.seasons
                ],
                "cast": [
                    {
                        "person_id": cast.person_id,
                        "character_name": cast.character_name,
                        "job_title": cast.job_title,
                    }
                    for cast in content.cast
                ],
                "crew": [
                    {
                        "person_id": crew.person_id,
                        "job_title": crew.job_title,
                        "department": crew.department,
                    }
                    for crew in content.crew
                ],
                "movie_files": [
                    {
                        "id": file.id,
                        "quality_level": file.quality_level,
                        "file_url": file.file_url,
                    }
                    for file in content.movie_files
                ],
            }
            serialized_contents.append(content_dict)

        return ContentAdminListResponse(
            items=serialized_contents,
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
            detail=f"Error retrieving content list: {str(e)}",
        )


@router.get("/{content_id}", response_model=ContentAdminResponse)
async def get_content_admin(
    content_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get content by ID for admin.
    """
    try:
        content = await get_content_admin_by_id(db, content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTENT_NOT_FOUND,
            )

        # Convert SQLAlchemy object to dictionary for proper serialization
        content_dict = {
            "id": content.id,
            "title": content.title,
            "slug": content.slug,
            "description": content.description,
            "tagline": content.tagline,
            "content_type": content.content_type,
            "status": content.status,
            "content_rating": content.content_rating,
            "poster_url": content.poster_url,
            "backdrop_url": content.backdrop_url,
            "trailer_url": content.trailer_url,
            "logo_url": content.logo_url,
            "release_date": content.release_date,
            "premiere_date": content.premiere_date,
            "end_date": content.end_date,
            "runtime": content.runtime,
            "language": content.language,
            "original_language": content.original_language,
            "total_seasons": content.total_seasons,
            "total_episodes": content.total_episodes,
            "keywords": content.keywords,
            "is_ongoing": content.is_ongoing,
            "is_featured": content.is_featured,
            "is_trending": content.is_trending,
            "is_new_release": content.is_new_release,
            "is_premium": content.is_premium,
            "available_from": content.available_from,
            "available_until": content.available_until,
            "total_views": content.total_views,
            "likes_count": content.likes_count,
            "reviews_count": content.reviews_count,
            "platform_rating": content.platform_rating,
            "platform_votes": content.platform_votes,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            # Convert relationships to dictionaries
            "genres": [
                {"id": genre.id, "name": genre.name, "slug": genre.slug}
                for genre in content.genres
            ],
            "seasons": [
                {
                    "id": season.id,
                    "season_number": season.season_number,
                    "title": season.title,
                }
                for season in content.seasons
            ],
            "cast": [
                {
                    "person_id": cast.person_id,
                    "character_name": cast.character_name,
                    "job_title": cast.job_title,
                }
                for cast in content.cast
            ],
            "crew": [
                {
                    "person_id": crew.person_id,
                    "job_title": crew.job_title,
                    "department": crew.department,
                }
                for crew in content.crew
            ],
            "movie_files": [
                {
                    "id": file.id,
                    "quality_level": file.quality_level,
                    "file_url": file.file_url,
                }
                for file in content.movie_files
            ],
        }
        return ContentAdminResponse.model_validate(content_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving content: {str(e)}",
        )


@router.put("/{content_id}", response_model=ContentAdminResponse)
async def update_content_admin(
    content_id: UUID,
    current_user: AdminUser,
    content_data: ContentAdminUpdate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update content (Admin only).
    """
    try:
        # Filter out None values
        update_data = {k: v for k, v in content_data.model_dump().items() if v is not None}

        content = await update_content(db, content_id, update_data)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTENT_NOT_FOUND,
            )

        # Convert SQLAlchemy object to dictionary for proper serialization
        content_dict = {
            "id": content.id,
            "title": content.title,
            "slug": content.slug,
            "description": content.description,
            "tagline": content.tagline,
            "content_type": content.content_type,
            "status": content.status,
            "content_rating": content.content_rating,
            "poster_url": content.poster_url,
            "backdrop_url": content.backdrop_url,
            "trailer_url": content.trailer_url,
            "logo_url": content.logo_url,
            "release_date": content.release_date,
            "premiere_date": content.premiere_date,
            "end_date": content.end_date,
            "runtime": content.runtime,
            "language": content.language,
            "original_language": content.original_language,
            "total_seasons": content.total_seasons,
            "total_episodes": content.total_episodes,
            "is_ongoing": content.is_ongoing,
            "is_featured": content.is_featured,
            "is_trending": content.is_trending,
            "is_new_release": content.is_new_release,
            "is_premium": content.is_premium,
            "available_from": content.available_from,
            "available_until": content.available_until,
            "total_views": content.total_views,
            "likes_count": content.likes_count,
            "keywords": content.keywords,
            "reviews_count": content.reviews_count,
            "platform_rating": content.platform_rating,
            "platform_votes": content.platform_votes,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            # Convert relationships to dictionaries
            "genres": [
                {"id": genre.id, "name": genre.name, "slug": genre.slug}
                for genre in content.genres
            ],
            "seasons": [
                {
                    "id": season.id,
                    "season_number": season.season_number,
                    "title": season.title,
                }
                for season in content.seasons
            ],
            "cast": [
                {
                    "person_id": cast.person_id,
                    "character_name": cast.character_name,
                    "job_title": cast.job_title,
                }
                for cast in content.cast
            ],
            "crew": [
                {
                    "person_id": crew.person_id,
                    "job_title": crew.job_title,
                    "department": crew.department,
                }
                for crew in content.crew
            ],
            "movie_files": [
                {
                    "id": file.id,
                    "quality_level": file.quality_level,
                    "file_url": file.file_url,
                }
                for file in content.movie_files
            ],
        }
        return ContentAdminResponse.model_validate(content_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating content: {str(e)}",
        )


@router.delete("/{content_id}")
async def delete_content_admin(
    content_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete content (Admin only).
    """
    try:
        success = await delete_content(db, content_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTENT_NOT_FOUND,
            )
        return {"message": CONTENT_DELETED}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting content: {str(e)}",
        )


@router.patch("/{content_id}/featured")
async def toggle_content_featured_admin(
    content_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Toggle content featured status (Admin only).
    """
    try:
        content = await toggle_content_featured(db, content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTENT_NOT_FOUND,
            )

        message = CONTENT_FEATURED if content.is_featured else CONTENT_UNFEATURED

        # Convert SQLAlchemy object to dictionary for proper serialization
        content_dict = {
            "id": content.id,
            "title": content.title,
            "slug": content.slug,
            "description": content.description,
            "tagline": content.tagline,
            "content_type": content.content_type,
            "status": content.status,
            "content_rating": content.content_rating,
            "poster_url": content.poster_url,
            "backdrop_url": content.backdrop_url,
            "trailer_url": content.trailer_url,
            "logo_url": content.logo_url,
            "release_date": content.release_date,
            "premiere_date": content.premiere_date,
            "end_date": content.end_date,
            "runtime": content.runtime,
            "language": content.language,
            "original_language": content.original_language,
            "total_seasons": content.total_seasons,
            "total_episodes": content.total_episodes,
            "is_ongoing": content.is_ongoing,
            "is_featured": content.is_featured,
            "is_trending": content.is_trending,
            "is_new_release": content.is_new_release,
            "is_premium": content.is_premium,
            "available_from": content.available_from,
            "available_until": content.available_until,
            "total_views": content.total_views,
            "likes_count": content.likes_count,
            "reviews_count": content.reviews_count,
            "platform_rating": content.platform_rating,
            "platform_votes": content.platform_votes,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            # Convert relationships to dictionaries
            "genres": [
                {"id": genre.id, "name": genre.name, "slug": genre.slug}
                for genre in content.genres
            ],
            "seasons": [
                {
                    "id": season.id,
                    "season_number": season.season_number,
                    "title": season.title,
                }
                for season in content.seasons
            ],
            "cast": [
                {
                    "person_id": cast.person_id,
                    "character_name": cast.character_name,
                    "job_title": cast.job_title,
                }
                for cast in content.cast
            ],
            "crew": [
                {
                    "person_id": crew.person_id,
                    "job_title": crew.job_title,
                    "department": crew.department,
                }
                for crew in content.crew
            ],
            "movie_files": [
                {
                    "id": file.id,
                    "quality_level": file.quality_level,
                    "file_url": file.file_url,
                }
                for file in content.movie_files
            ],
        }

        return {
            "message": message,
            "content": ContentAdminResponse.model_validate(content_dict),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling content featured status: {str(e)}",
        )


@router.patch("/{content_id}/trending")
async def toggle_content_trending_admin(
    content_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Toggle content trending status (Admin only).
    """
    try:
        content = await toggle_content_trending(db, content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTENT_NOT_FOUND,
            )

        message = CONTENT_TRENDING

        # Convert SQLAlchemy object to dictionary for proper serialization
        content_dict = {
            "id": content.id,
            "title": content.title,
            "slug": content.slug,
            "description": content.description,
            "tagline": content.tagline,
            "content_type": content.content_type,
            "status": content.status,
            "content_rating": content.content_rating,
            "poster_url": content.poster_url,
            "backdrop_url": content.backdrop_url,
            "trailer_url": content.trailer_url,
            "logo_url": content.logo_url,
            "release_date": content.release_date,
            "premiere_date": content.premiere_date,
            "end_date": content.end_date,
            "runtime": content.runtime,
            "language": content.language,
            "original_language": content.original_language,
            "total_seasons": content.total_seasons,
            "total_episodes": content.total_episodes,
            "is_ongoing": content.is_ongoing,
            "is_featured": content.is_featured,
            "is_trending": content.is_trending,
            "is_new_release": content.is_new_release,
            "is_premium": content.is_premium,
            "available_from": content.available_from,
            "available_until": content.available_until,
            "total_views": content.total_views,
            "likes_count": content.likes_count,
            "reviews_count": content.reviews_count,
            "platform_rating": content.platform_rating,
            "platform_votes": content.platform_votes,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            # Convert relationships to dictionaries
            "genres": [
                {"id": genre.id, "name": genre.name, "slug": genre.slug}
                for genre in content.genres
            ],
            "seasons": [
                {
                    "id": season.id,
                    "season_number": season.season_number,
                    "title": season.title,
                }
                for season in content.seasons
            ],
            "cast": [
                {
                    "person_id": cast.person_id,
                    "character_name": cast.character_name,
                    "job_title": cast.job_title,
                }
                for cast in content.cast
            ],
            "crew": [
                {
                    "person_id": crew.person_id,
                    "job_title": crew.job_title,
                    "department": crew.department,
                }
                for crew in content.crew
            ],
            "movie_files": [
                {
                    "id": file.id,
                    "quality_level": file.quality_level,
                    "file_url": file.file_url,
                }
                for file in content.movie_files
            ],
        }

        return {
            "message": message,
            "content": ContentAdminResponse.model_validate(content_dict),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling content trending status: {str(e)}",
        )


@router.patch("/{content_id}/publish")
async def publish_content_admin(
    content_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Publish content (Admin only).
    """
    try:
        content = await publish_content(db, content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTENT_NOT_FOUND,
            )
        # Convert SQLAlchemy object to dictionary for proper serialization
        content_dict = {
            "id": content.id,
            "title": content.title,
            "slug": content.slug,
            "description": content.description,
            "tagline": content.tagline,
            "content_type": content.content_type,
            "status": content.status,
            "content_rating": content.content_rating,
            "poster_url": content.poster_url,
            "backdrop_url": content.backdrop_url,
            "trailer_url": content.trailer_url,
            "logo_url": content.logo_url,
            "release_date": content.release_date,
            "premiere_date": content.premiere_date,
            "end_date": content.end_date,
            "runtime": content.runtime,
            "language": content.language,
            "original_language": content.original_language,
            "total_seasons": content.total_seasons,
            "total_episodes": content.total_episodes,
            "is_ongoing": content.is_ongoing,
            "is_featured": content.is_featured,
            "is_trending": content.is_trending,
            "is_new_release": content.is_new_release,
            "is_premium": content.is_premium,
            "available_from": content.available_from,
            "available_until": content.available_until,
            "total_views": content.total_views,
            "likes_count": content.likes_count,
            "reviews_count": content.reviews_count,
            "platform_rating": content.platform_rating,
            "platform_votes": content.platform_votes,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            # Convert relationships to dictionaries
            "genres": [
                {"id": genre.id, "name": genre.name, "slug": genre.slug}
                for genre in content.genres
            ],
            "seasons": [
                {
                    "id": season.id,
                    "season_number": season.season_number,
                    "title": season.title,
                }
                for season in content.seasons
            ],
            "cast": [
                {
                    "person_id": cast.person_id,
                    "character_name": cast.character_name,
                    "job_title": cast.job_title,
                }
                for cast in content.cast
            ],
            "crew": [
                {
                    "person_id": crew.person_id,
                    "job_title": crew.job_title,
                    "department": crew.department,
                }
                for crew in content.crew
            ],
            "movie_files": [
                {
                    "id": file.id,
                    "quality_level": file.quality_level,
                    "file_url": file.file_url,
                }
                for file in content.movie_files
            ],
        }

        return {
            "message": CONTENT_PUBLISHED,
            "content": ContentAdminResponse.model_validate(content_dict),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error publishing content: {str(e)}",
        )


@router.patch("/{content_id}/unpublish")
async def unpublish_content_admin(
    content_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Unpublish content (Admin only).
    """
    try:
        content = await unpublish_content(db, content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTENT_NOT_FOUND,
            )
        # Convert SQLAlchemy object to dictionary for proper serialization
        content_dict = {
            "id": content.id,
            "title": content.title,
            "slug": content.slug,
            "description": content.description,
            "tagline": content.tagline,
            "content_type": content.content_type,
            "status": content.status,
            "content_rating": content.content_rating,
            "poster_url": content.poster_url,
            "backdrop_url": content.backdrop_url,
            "trailer_url": content.trailer_url,
            "logo_url": content.logo_url,
            "release_date": content.release_date,
            "premiere_date": content.premiere_date,
            "end_date": content.end_date,
            "runtime": content.runtime,
            "language": content.language,
            "original_language": content.original_language,
            "total_seasons": content.total_seasons,
            "total_episodes": content.total_episodes,
            "is_ongoing": content.is_ongoing,
            "is_featured": content.is_featured,
            "is_trending": content.is_trending,
            "is_new_release": content.is_new_release,
            "is_premium": content.is_premium,
            "available_from": content.available_from,
            "available_until": content.available_until,
            "total_views": content.total_views,
            "likes_count": content.likes_count,
            "reviews_count": content.reviews_count,
            "platform_rating": content.platform_rating,
            "platform_votes": content.platform_votes,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            # Convert relationships to dictionaries
            "genres": [
                {"id": genre.id, "name": genre.name, "slug": genre.slug}
                for genre in content.genres
            ],
            "seasons": [
                {
                    "id": season.id,
                    "season_number": season.season_number,
                    "title": season.title,
                }
                for season in content.seasons
            ],
            "cast": [
                {
                    "person_id": cast.person_id,
                    "character_name": cast.character_name,
                    "job_title": cast.job_title,
                }
                for cast in content.cast
            ],
            "crew": [
                {
                    "person_id": crew.person_id,
                    "job_title": crew.job_title,
                    "department": crew.department,
                }
                for crew in content.crew
            ],
            "movie_files": [
                {
                    "id": file.id,
                    "quality_level": file.quality_level,
                    "file_url": file.file_url,
                }
                for file in content.movie_files
            ],
        }

        return {
            "message": CONTENT_UNPUBLISHED,
            "content": ContentAdminResponse.model_validate(content_dict),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error unpublishing content: {str(e)}",
        )


@router.get("/tv-shows/{tv_show_id}", response_model=ContentAdminResponse)
async def get_admin_tv_show(
    current_user: AdminUser,
    tv_show_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get TV show details for admin management.
    This is the same as the regular admin content endpoint, but we verify
    that the content is actually a TV show (content_type=TV_SERIES).
    """
    try:
        # Get content by ID (same as regular admin content endpoint)
        content = await get_content_admin_by_id(db, tv_show_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        # IMPORTANT: Check if this content is actually a TV show
        # If admin tries to access a movie ID with this endpoint, we reject it
        if content.content_type != "tv_series":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Content is not a TV show"
            )

        # Return the same admin content response format
        return content

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving TV show: {str(e)}",
        )


@router.post("/tv-shows", response_model=ContentAdminResponse)
async def create_admin_tv_show(
    current_user: AdminUser,
    content_data: ContentAdminCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new TV show (Admin only).
    This endpoint automatically sets content_type=TV_SERIES
    so admins can create TV shows specifically.
    """
    try:
        # IMPORTANT: Force content_type to be TV_SERIES for TV show creation
        # This ensures only TV shows are created through this endpoint
        content_data.content_type = "tv_series"
        
        # Use existing admin function to create content, but now for TV shows only
        content = await create_content(db, content_data, current_user.id)

        return content

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating TV show: {str(e)}",
        )


@router.put("/tv-shows/{tv_show_id}", response_model=ContentAdminResponse)
async def update_admin_tv_show(
    current_user: AdminUser,
    tv_show_id: UUID,
    content_data: ContentAdminUpdate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update TV show (Admin only).
    This endpoint verifies the content is a TV show before allowing updates.
    """
    try:
        # First, verify the TV show exists and is actually a TV show
        existing_content = await get_content_admin_by_id(db, tv_show_id)
        if not existing_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        # Check if it's actually a TV show
        if existing_content.content_type != "tv_series":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Content is not a TV show"
            )

        # IMPORTANT: Prevent changing content_type from TV_SERIES
        # This ensures the content remains a TV show
        content_data.content_type = "tv_series"
        
        # Use existing admin function to update content
        content = await update_content(db, tv_show_id, content_data, current_user.id)

        return content

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating TV show: {str(e)}",
        )


@router.delete("/tv-shows/{tv_show_id}")
async def delete_admin_tv_show(
    current_user: AdminUser,
    tv_show_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete TV show (Admin only).
    This endpoint verifies the content is a TV show before allowing deletion.
    """
    try:
        # First, verify the TV show exists and is actually a TV show
        existing_content = await get_content_admin_by_id(db, tv_show_id)
        if not existing_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        # Check if it's actually a TV show
        if existing_content.content_type != "tv_series":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Content is not a TV show"
            )

        # Use existing admin function to delete content
        await delete_content(db, tv_show_id, current_user.id)

        return {"message": CONTENT_DELETED, "content_id": str(tv_show_id)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting TV show: {str(e)}",
        )


# =============================================================================
# ADMIN TV SHOW SEASONS CRUD ENDPOINTS
# =============================================================================
# These endpoints manage seasons for TV shows (admin only)

@router.get("/tv-shows/{tv_show_id}/seasons")
async def get_admin_tv_show_seasons(
    current_user: AdminUser,
    tv_show_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get all seasons for a TV show (Admin only).
    Returns list of seasons with their details.
    """
    try:
        # First, verify the TV show exists and is actually a TV show
        content = await get_content_admin_by_id(db, tv_show_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        # Check if it's actually a TV show
        if content.content_type != "tv_series":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Content is not a TV show"
            )

        # Return the seasons that are already loaded with the content
        return content.seasons

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving TV show seasons: {str(e)}",
        )


@router.post("/tv-shows/{tv_show_id}/seasons")
async def create_admin_tv_show_season(
    current_user: AdminUser,
    tv_show_id: UUID,
    season_data: dict,  # We'll create a proper schema later
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new season for a TV show (Admin only).
    """
    try:
        # First, verify the TV show exists and is actually a TV show
        content = await get_content_admin_by_id(db, tv_show_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        # Check if it's actually a TV show
        if content.content_type != "tv_series":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Content is not a TV show"
            )

        # Create season using existing admin utilities
        from app.models.content import Season
        from sqlalchemy import select
        from datetime import datetime
        
        # Get the next season number
        max_season_query = select(Season.season_number).where(Season.content_id == tv_show_id).order_by(Season.season_number.desc())
        result = await db.execute(max_season_query)
        max_season = result.scalar_one_or_none()
        next_season_number = (max_season or 0) + 1

        # Parse dates from strings if provided
        air_date = None
        if season_data.get("air_date"):
            air_date = datetime.strptime(season_data["air_date"], "%Y-%m-%d").date()
        
        end_date = None
        if season_data.get("end_date"):
            end_date = datetime.strptime(season_data["end_date"], "%Y-%m-%d").date()

        # Create new season
        new_season = Season(
            content_id=tv_show_id,
            season_number=next_season_number,
            title=season_data.get("title"),
            description=season_data.get("description"),
            poster_url=season_data.get("poster_url"),
            backdrop_url=season_data.get("backdrop_url"),
            air_date=air_date,
            end_date=end_date,
            episode_count=season_data.get("episode_count", 0),
            is_complete=season_data.get("is_complete", False)
        )

        db.add(new_season)
        await db.commit()
        await db.refresh(new_season)

        return {"message": "Season created successfully", "season": new_season}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating season: {str(e)}",
        )


@router.put("/tv-shows/{tv_show_id}/seasons/{season_id}")
async def update_admin_tv_show_season(
    current_user: AdminUser,
    tv_show_id: UUID,
    season_id: UUID,
    season_data: dict,  # We'll create a proper schema later
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update season for a TV show (Admin only).
    """
    try:
        # First, verify the TV show exists and is actually a TV show
        content = await get_content_admin_by_id(db, tv_show_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        # Check if it's actually a TV show
        if content.content_type != "tv_series":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Content is not a TV show"
            )

        # Get the season
        from app.models.content import Season
        from sqlalchemy import select
        from datetime import datetime
        
        season_query = select(Season).where(
            Season.id == season_id,
            Season.content_id == tv_show_id
        )
        result = await db.execute(season_query)
        season = result.scalar_one_or_none()
        
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Season not found for this TV show"
            )

        # Update season fields
        if "title" in season_data:
            season.title = season_data["title"]
        if "description" in season_data:
            season.description = season_data["description"]
        if "poster_url" in season_data:
            season.poster_url = season_data["poster_url"]
        if "backdrop_url" in season_data:
            season.backdrop_url = season_data["backdrop_url"]
        if "air_date" in season_data:
            season.air_date = datetime.strptime(season_data["air_date"], "%Y-%m-%d").date()
        if "end_date" in season_data:
            season.end_date = datetime.strptime(season_data["end_date"], "%Y-%m-%d").date()
        if "episode_count" in season_data:
            season.episode_count = season_data["episode_count"]
        if "is_complete" in season_data:
            season.is_complete = season_data["is_complete"]

        await db.commit()
        await db.refresh(season)

        return {"message": "Season updated successfully", "season": season}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating season: {str(e)}",
        )


@router.delete("/tv-shows/{tv_show_id}/seasons/{season_id}")
async def delete_admin_tv_show_season(
    current_user: AdminUser,
    tv_show_id: UUID,
    season_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete season for a TV show (Admin only).
    """
    try:
        # First, verify the TV show exists and is actually a TV show
        content = await get_content_admin_by_id(db, tv_show_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        # Check if it's actually a TV show
        if content.content_type != "tv_series":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Content is not a TV show"
            )

        # Get the season
        from app.models.content import Season
        from sqlalchemy import select
        
        season_query = select(Season).where(
            Season.id == season_id,
            Season.content_id == tv_show_id
        )
        result = await db.execute(season_query)
        season = result.scalar_one_or_none()
        
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Season not found for this TV show"
            )

        # Delete the season (cascade will handle episodes)
        await db.delete(season)
        await db.commit()

        return {"message": "Season deleted successfully", "season_id": str(season_id)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting season: {str(e)}",
        )


# =============================================================================
# ADMIN TV SHOW EPISODES CRUD ENDPOINTS
# =============================================================================
# These endpoints manage episodes for TV show seasons (admin only)

@router.get("/tv-shows/{tv_show_id}/seasons/{season_id}/episodes")
async def get_admin_tv_show_episodes(
    current_user: AdminUser,
    tv_show_id: UUID,
    season_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get all episodes for a season (Admin only).
    Returns list of episodes with their details.
    """
    try:
        # First, verify the TV show exists and is actually a TV show
        content = await get_content_admin_by_id(db, tv_show_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        # Check if it's actually a TV show
        if content.content_type != "tv_series":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Content is not a TV show"
            )

        # Get the season
        from app.models.content import Season
        from sqlalchemy import select
        
        season_query = select(Season).where(
            Season.id == season_id,
            Season.content_id == tv_show_id
        )
        result = await db.execute(season_query)
        season = result.scalar_one_or_none()
        
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Season not found for this TV show"
            )

        # Return the episodes for this season
        return season.episodes

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving episodes: {str(e)}",
        )


@router.post("/tv-shows/{tv_show_id}/seasons/{season_id}/episodes")
async def create_admin_tv_show_episode(
    current_user: AdminUser,
    tv_show_id: UUID,
    season_id: UUID,
    episode_data: dict,  # We'll create a proper schema later
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new episode for a season (Admin only).
    """
    try:
        # First, verify the TV show exists and is actually a TV show
        content = await get_content_admin_by_id(db, tv_show_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        # Check if it's actually a TV show
        if content.content_type != "tv_series":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Content is not a TV show"
            )

        # Get the season
        from app.models.content import Season, Episode
        from sqlalchemy import select
        
        season_query = select(Season).where(
            Season.id == season_id,
            Season.content_id == tv_show_id
        )
        result = await db.execute(season_query)
        season = result.scalar_one_or_none()
        
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Season not found for this TV show"
            )

        # Get the next episode number
        max_episode_query = select(Episode.episode_number).where(
            Episode.content_id == tv_show_id,
            Episode.season_id == season_id
        ).order_by(Episode.episode_number.desc()).limit(1)
        result = await db.execute(max_episode_query)
        max_episode = result.scalar()
        next_episode_number = (max_episode or 0) + 1

        # Parse date fields if provided
        from datetime import datetime as dt
        
        air_date = None
        if episode_data.get("air_date"):
            air_date = dt.strptime(episode_data["air_date"], "%Y-%m-%d").date()
        
        available_from = None
        if episode_data.get("available_from"):
            available_from = dt.fromisoformat(episode_data["available_from"])
        
        available_until = None
        if episode_data.get("available_until"):
            available_until = dt.fromisoformat(episode_data["available_until"])

        # Create new episode
        new_episode = Episode(
            content_id=tv_show_id,
            season_id=season_id,
            episode_number=next_episode_number,
            title=episode_data.get("title"),
            slug=episode_data.get("slug", f"s{season.season_number}e{next_episode_number}"),
            description=episode_data.get("description"),
            tag_line=episode_data.get("tag_line"),
            runtime=episode_data.get("runtime"),
            air_date=air_date,
            video_file_url=episode_data.get("video_file_url"),
            thumbnail_url=episode_data.get("thumbnail_url"),
            preview_url=episode_data.get("preview_url"),
            file_size_bytes=episode_data.get("file_size_bytes"),
            video_codec=episode_data.get("video_codec"),
            audio_codec=episode_data.get("audio_codec"),
            container_format=episode_data.get("container_format"),
            bitrate_kbps=episode_data.get("bitrate_kbps"),
            frame_rate=episode_data.get("frame_rate"),
            storage_bucket=episode_data.get("storage_bucket"),
            storage_key=episode_data.get("storage_key"),
            storage_region=episode_data.get("storage_region"),
            cdn_url=episode_data.get("cdn_url"),
            processing_status=episode_data.get("processing_status", "pending"),
            subtitle_tracks=episode_data.get("subtitle_tracks"),
            audio_tracks=episode_data.get("audio_tracks"),
            available_languages=episode_data.get("available_languages"),
            views_count=episode_data.get("views_count", 0),
            average_completion_rate=episode_data.get("average_completion_rate"),
            is_available=episode_data.get("is_available", True),
            available_from=available_from,
            available_until=available_until
        )

        db.add(new_episode)
        await db.commit()
        await db.refresh(new_episode)

        return {"message": "Episode created successfully", "episode": new_episode}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating episode: {str(e)}",
        )


@router.put("/tv-shows/{tv_show_id}/seasons/{season_id}/episodes/{episode_id}")
async def update_admin_tv_show_episode(
    current_user: AdminUser,
    tv_show_id: UUID,
    season_id: UUID,
    episode_id: UUID,
    episode_data: dict,  # We'll create a proper schema later
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update episode for a season (Admin only).
    """
    try:
        # First, verify the TV show exists and is actually a TV show
        content = await get_content_admin_by_id(db, tv_show_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        # Check if it's actually a TV show
        if content.content_type != "tv_series":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Content is not a TV show"
            )

        # Get the episode
        from app.models.content import Episode
        from sqlalchemy import select
        
        episode_query = select(Episode).where(
            Episode.id == episode_id,
            Episode.content_id == tv_show_id,
            Episode.season_id == season_id
        )
        result = await db.execute(episode_query)
        episode = result.scalar_one_or_none()
        
        if not episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Episode not found for this season"
            )

        # Parse date fields if provided
        from datetime import datetime as dt
        
        # Update episode fields
        for field, value in episode_data.items():
            if hasattr(episode, field):
                # Parse date/datetime fields
                if field == "air_date" and value:
                    value = dt.strptime(value, "%Y-%m-%d").date()
                elif field == "available_from" and value:
                    value = dt.fromisoformat(value)
                elif field == "available_until" and value:
                    value = dt.fromisoformat(value)
                
                setattr(episode, field, value)

        await db.commit()
        await db.refresh(episode)

        return {"message": "Episode updated successfully", "episode": episode}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating episode: {str(e)}",
        )


@router.delete("/tv-shows/{tv_show_id}/seasons/{season_id}/episodes/{episode_id}")
async def delete_admin_tv_show_episode(
    current_user: AdminUser,
    tv_show_id: UUID,
    season_id: UUID,
    episode_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete episode for a season (Admin only).
    """
    try:
        # First, verify the TV show exists and is actually a TV show
        content = await get_content_admin_by_id(db, tv_show_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CONTENT_NOT_FOUND
            )

        # Check if it's actually a TV show
        if content.content_type != "tv_series":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Content is not a TV show"
            )

        # Get the episode
        from app.models.content import Episode
        from sqlalchemy import select
        
        episode_query = select(Episode).where(
            Episode.id == episode_id,
            Episode.content_id == tv_show_id,
            Episode.season_id == season_id
        )
        result = await db.execute(episode_query)
        episode = result.scalar_one_or_none()
        
        if not episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Episode not found for this season"
            )

        # Delete the episode
        await db.delete(episode)
        await db.commit()

        return {"message": "Episode deleted successfully", "episode_id": str(episode_id)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting episode: {str(e)}",
        )