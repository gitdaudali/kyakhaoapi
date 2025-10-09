from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.config import settings
from app.core.database import get_db
from app.core.messages import FILE_INVALID_FORMAT, FILE_UPLOADED
from app.core.response_handler import (
    success_response,
    error_response,
    InvalidFileFormatException,
    InternalServerException
)
from app.schemas.admin import EntityType, FileType, ImageType, S3PathType
from app.utils.s3_utils import upload_file_to_s3

router = APIRouter()


@router.post("/image")
async def upload_admin_image(
    current_user: AdminUser,
    image: UploadFile = File(...),
    s3_path: S3PathType = Form(
        ..., description="S3 path where image should be uploaded"
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Upload image to S3 with custom path (Admin only).

    This is a generic image upload API that can be used for:
    - Streaming channel icons: s3_path = "streaming-channels/icons"
    - Genre covers: s3_path = "genres/covers"
    - Content thumbnails: s3_path = "content/thumbnails"
    - User avatars: s3_path = "avatars"
    - Any other admin image uploads

    Args:
        image: Image file to upload
        s3_path: S3 folder path where image should be stored

    Returns:
        dict: Contains uploaded image URL and metadata
    """
    try:
        # Validate file type
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=FILE_INVALID_FORMAT,
            )

        # Define allowed extensions for images
        allowed_extensions = settings.AVATAR_ALLOWED_FILE_TYPES
        max_size_mb = 10  # 10MB for admin images

        # Upload image to S3 with custom path
        image_url = await upload_file_to_s3(
            file=image,
            folder=s3_path,
            allowed_extensions=allowed_extensions,
            max_size_mb=max_size_mb,
        )

        return {
            "message": FILE_UPLOADED,
            "image_url": image_url,
            "s3_path": s3_path.value,
            "filename": image.filename,
            "content_type": image.content_type,
            "size_bytes": image.size if hasattr(image, "size") else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image: {str(e)}",
        )


@router.post("/image/{entity_type}/{entity_id}")
async def upload_entity_image(
    entity_type: EntityType,
    entity_id: UUID,
    current_user: AdminUser,
    image: UploadFile = File(...),
    image_type: ImageType = Form(
        ImageType.COVER, description="Type of image (cover, icon, thumbnail, etc.)"
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Upload image for specific entity (Admin only).

    This API automatically generates the S3 path based on entity type and ID.

    Args:
        entity_type: Type of entity (streaming-channels, genres, content, users)
        entity_id: ID of the entity
        image: Image file to upload
        image_type: Type of image (cover, icon, thumbnail, avatar, etc.)

    Returns:
        dict: Contains uploaded image URL and metadata
    """
    try:
        # Entity type validation is handled by the EntityType enum

        # Validate file type
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=FILE_INVALID_FORMAT,
            )

        # Generate S3 path based on entity type and ID
        s3_path = f"{entity_type.value}/{entity_id}/{image_type.value}s"

        # Define allowed extensions for images
        allowed_extensions = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
        max_size_mb = 10  # 10MB for admin images

        # Upload image to S3
        image_url = await upload_file_to_s3(
            file=image,
            folder=s3_path,
            allowed_extensions=allowed_extensions,
            max_size_mb=max_size_mb,
        )

        return {
            "message": FILE_UPLOADED,
            "image_url": image_url,
            "s3_path": s3_path,
            "entity_type": entity_type.value,
            "entity_id": str(entity_id),
            "image_type": image_type.value,
            "filename": image.filename,
            "content_type": image.content_type,
            "size_bytes": image.size if hasattr(image, "size") else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading entity image: {str(e)}",
        )


@router.post("/video")
async def upload_admin_video(
    current_user: AdminUser,
    video: UploadFile = File(...),
    s3_path: S3PathType = Form(
        ..., description="S3 path where video should be uploaded"
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Upload video file to S3 with custom path (Admin only).

    This is a generic video upload API that can be used for:
    - Content videos: s3_path = "content/videos"
    - Episode videos: s3_path = "content/episodes"
    - Trailer videos: s3_path = "content/trailers"
    - Any other admin video uploads

    Args:
        video: Video file to upload
        s3_path: S3 folder path where video should be stored

    Returns:
        dict: Contains uploaded video URL and metadata
    """
    try:
        # Validate file type
        if not video.content_type or not video.content_type.startswith("video/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=FILE_INVALID_FORMAT,
            )

        # Define allowed extensions for videos
        allowed_extensions = [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv"]
        max_size_mb = 5000  # 5GB for video files

        # Upload video to S3
        video_url = await upload_file_to_s3(
            file=video,
            folder=s3_path,
            allowed_extensions=allowed_extensions,
            max_size_mb=max_size_mb,
        )

        return {
            "message": FILE_UPLOADED,
            "video_url": video_url,
            "s3_path": s3_path.value,
            "filename": video.filename,
            "content_type": video.content_type,
            "size_bytes": video.size if hasattr(video, "size") else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading video: {str(e)}",
        )


@router.post("/video/{entity_type}/{entity_id}")
async def upload_entity_video(
    entity_type: EntityType,
    entity_id: UUID,
    current_user: AdminUser,
    video: UploadFile = File(...),
    file_type: FileType = Form(
        FileType.VIDEO, description="Type of video file (video, episode, movie, etc.)"
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Upload video file for specific entity (Admin only).

    This API automatically generates the S3 path based on entity type and ID.

    Args:
        entity_type: Type of entity (streaming-channels, genres, content, users)
        entity_id: ID of the entity
        video: Video file to upload
        file_type: Type of video file (video, episode, movie, trailer, etc.)

    Returns:
        dict: Contains uploaded video URL and metadata
    """
    try:
        # Entity type validation is handled by the EntityType enum

        # Validate file type
        if not video.content_type or not video.content_type.startswith("video/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=FILE_INVALID_FORMAT,
            )

        # Generate S3 path based on entity type and ID
        s3_path = f"{entity_type.value}/{entity_id}/{file_type.value}s"

        # Define allowed extensions for videos
        allowed_extensions = [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv"]
        max_size_mb = 5000  # 5GB for video files

        # Upload video to S3
        video_url = await upload_file_to_s3(
            file=video,
            folder=s3_path,
            allowed_extensions=allowed_extensions,
            max_size_mb=max_size_mb,
        )

        return {
            "message": FILE_UPLOADED,
            "video_url": video_url,
            "s3_path": s3_path,
            "entity_type": entity_type.value,
            "entity_id": str(entity_id),
            "file_type": file_type.value,
            "filename": video.filename,
            "content_type": video.content_type,
            "size_bytes": video.size if hasattr(video, "size") else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading video for {entity_type} {entity_id}: {str(e)}",
        )
