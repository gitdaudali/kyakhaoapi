from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.database import get_db
from app.core.messages import (
    FILE_INVALID_FORMAT,
    FILE_UPLOADED,
    GENRE_ALREADY_EXISTS,
    GENRE_CREATED,
    GENRE_DELETED,
    GENRE_FEATURED,
    GENRE_NOT_FOUND,
    GENRE_UNFEATURED,
    GENRE_UPDATED,
)
from app.models.user import User
from app.schemas.admin import (
    GenreAdminCreate,
    GenreAdminListResponse,
    GenreAdminQueryParams,
    GenreAdminResponse,
    GenreAdminUpdate,
)
from app.utils.admin_utils import (
    create_genre,
    delete_genre,
    get_genre_admin_by_id,
    get_genres_admin_list,
    toggle_genre_featured,
    update_genre,
    upload_genre_cover_image,
)
from app.utils.content_utils import calculate_pagination_info

router = APIRouter()


@router.post("/", response_model=GenreAdminResponse)
async def create_genre_admin(
    genre_data: GenreAdminCreate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new genre (Admin only).
    """
    try:
        genre = await create_genre(db, genre_data.dict())
        return GenreAdminResponse.model_validate(genre)
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=GENRE_ALREADY_EXISTS,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating genre: {str(e)}",
        )


@router.get("/", response_model=GenreAdminListResponse)
async def get_genres_admin(
    current_user: AdminUser,
    query_params: GenreAdminQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get paginated list of genres for admin.
    """
    try:
        genres, total = await get_genres_admin_list(db, query_params)
        pagination_info = calculate_pagination_info(
            query_params.page, query_params.size, total
        )

        return GenreAdminListResponse(
            items=genres,
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
            detail=f"Error retrieving genres: {str(e)}",
        )


@router.get("/{genre_id}", response_model=GenreAdminResponse)
async def get_genre_admin(
    genre_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get genre details by ID (Admin only).
    """
    try:
        genre = await get_genre_admin_by_id(db, genre_id)

        if not genre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=GENRE_NOT_FOUND,
            )

        return GenreAdminResponse.model_validate(genre)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving genre: {str(e)}",
        )


@router.put("/{genre_id}", response_model=GenreAdminResponse)
async def update_genre_admin(
    genre_id: UUID,
    update_data: GenreAdminUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update genre (Admin only).
    """
    try:
        # Filter out None values
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}

        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update",
            )

        genre = await update_genre(db, genre_id, update_dict)

        if not genre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=GENRE_NOT_FOUND,
            )

        return GenreAdminResponse.model_validate(genre)
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=GENRE_ALREADY_EXISTS,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating genre: {str(e)}",
        )


@router.delete("/{genre_id}")
async def delete_genre_admin(
    genre_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete genre (Admin only).
    """
    try:
        success = await delete_genre(db, genre_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=GENRE_NOT_FOUND,
            )

        return {"message": GENRE_DELETED}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting genre: {str(e)}",
        )


@router.post("/{genre_id}/feature")
async def feature_genre_admin(
    genre_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Toggle genre featured status (Admin only).
    """
    try:
        genre = await toggle_genre_featured(db, genre_id)

        if not genre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=GENRE_NOT_FOUND,
            )

        message = GENRE_FEATURED if genre.is_featured else GENRE_UNFEATURED
        return {"message": message, "is_featured": genre.is_featured}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling genre featured status: {str(e)}",
        )


@router.post("/{genre_id}/upload-cover")
async def upload_genre_cover(
    genre_id: UUID,
    current_user: AdminUser,
    cover_image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Upload genre cover image (Admin only).
    """
    try:
        # Check if genre exists
        genre = await get_genre_admin_by_id(db, genre_id)
        if not genre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=GENRE_NOT_FOUND,
            )

        # Validate file type
        if not cover_image.content_type or not cover_image.content_type.startswith(
            "image/"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=FILE_INVALID_FORMAT,
            )

        # Upload image to S3
        image_url = await upload_genre_cover_image(cover_image, genre_id)

        # Update genre with new cover image URL
        genre.cover_image_url = image_url
        await db.commit()
        await db.refresh(genre)

        return {
            "message": FILE_UPLOADED,
            "cover_image_url": image_url,
            "genre": GenreAdminResponse.model_validate(genre),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading genre cover image: {str(e)}",
        )
