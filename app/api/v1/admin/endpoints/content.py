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
        content = await create_content(db, content_data.dict())

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
        update_data = {k: v for k, v in content_data.dict().items() if v is not None}

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
