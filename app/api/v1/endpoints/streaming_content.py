"""
Streaming Content Endpoints
Chunk-based streaming decryption for video content
"""

from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.core.messages import CONTENT_NOT_FOUND
from app.models.content import Content, Episode, EpisodeQuality, MovieFile
from app.models.streaming_encryption import (
    StreamingChunkAccess,
    StreamingEncryptionKey,
    StreamingEncryptionStatus,
    StreamingEncryptionTask,
)
from app.models.user import User
from app.schemas.content import (
    ChunkRequest,
    ChunkResponse,
    EncryptionStatusResponse,
    FileEncryptionStatus,
    LicenseRequest,
    LicenseResponse,
    NotEncryptedResponse,
    PlayContentRequest,
    PlayContentResponse,
    ProcessingStatusResponse,
)
from app.utils.s3_utils import generate_signed_url
from app.utils.streaming_decryption_utils import (
    calculate_streaming_chunks,
    create_streaming_access_token,
    decrypt_streaming_file_key,
    generate_chunk_encryption_key,
    validate_streaming_access_token,
)

router = APIRouter()


@router.post("/{content_id}/play", response_model=PlayContentResponse)
async def get_streaming_play_url(
    content_id: UUID,
    request: PlayContentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get streaming play URL for content with chunk-based decryption.

    This endpoint:
    1. Finds the appropriate file (movie or episode)
    2. Checks if file is streaming encrypted
    3. Returns streaming URL + access token
    4. Shows processing status if not ready
    """
    try:
        # Get content
        content_query = select(Content).where(Content.id == content_id)
        content_result = await db.execute(content_query)
        content = content_result.scalar_one_or_none()

        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTENT_NOT_FOUND,
            )

        # Find the appropriate file
        file_obj = None
        file_type = None

        if content.content_type.value == "movie":
            # Find movie file with requested quality
            movie_file_query = select(MovieFile).where(
                MovieFile.content_id == content_id,
                MovieFile.quality_level == request.quality.upper(),
            )
            movie_file_result = await db.execute(movie_file_query)
            file_obj = movie_file_result.scalar_one_or_none()
            file_type = "movie_file"

        elif content.content_type.value == "tv_series":
            if not request.season_number or not request.episode_number:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Season number and episode number are required for TV series",
                )

            # Find episode
            episode_query = select(Episode).where(
                Episode.content_id == content_id,
                Episode.season_number == request.season_number,
                Episode.episode_number == request.episode_number,
            )
            episode_result = await db.execute(episode_query)
            episode = episode_result.scalar_one_or_none()

            if not episode:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Episode S{request.season_number}E{request.episode_number} not found",
                )

            # Find episode quality file
            episode_quality_query = select(EpisodeQuality).where(
                EpisodeQuality.episode_id == episode.id,
                EpisodeQuality.quality_level == request.quality.upper(),
            )
            episode_quality_result = await db.execute(episode_quality_query)
            file_obj = episode_quality_result.scalar_one_or_none()
            file_type = "episode_quality"

        if not file_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quality '{request.quality}' not available for this content",
            )

        # Check streaming encryption status
        if not file_obj.is_streaming_encrypted:
            # Check if encryption is in progress
            encryption_task_query = select(StreamingEncryptionTask).where(
                StreamingEncryptionTask.file_id == file_obj.id,
                StreamingEncryptionTask.status.in_(
                    [StreamingEncryptionStatus.PROCESSING]
                ),
            )
            encryption_task_result = await db.execute(encryption_task_query)
            encryption_task = encryption_task_result.scalar_one_or_none()

            if encryption_task:
                return ProcessingStatusResponse(
                    content_id=content_id,
                    title=content.title,
                    status="processing",
                    message="Video is being encrypted for streaming. Please wait...",
                    progress_percentage=encryption_task.progress_percentage,
                    estimated_completion="5-10 minutes",
                )
            else:
                return NotEncryptedResponse(
                    content_id=content_id,
                    title=content.title,
                    status="not_encrypted",
                    message="Video streaming encryption is not available yet",
                    file_url=file_obj.file_url,  # Return original URL for now
                    is_encrypted=False,
                )

        # File is streaming encrypted, create access token
        if not file_obj.streaming_encryption_key_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Streaming encrypted file missing encryption key",
            )

        # Create access token (valid for 24 hours)
        access_token = create_streaming_access_token(
            key_id=file_obj.streaming_encryption_key_id,
            file_id=str(file_obj.id),
            expires_hours=24,
        )

        # Calculate total chunks
        total_chunks = file_obj.streaming_total_chunks or calculate_streaming_chunks(
            file_obj.file_size_bytes or 0, file_obj.streaming_chunk_size
        )

        return PlayContentResponse(
            content_id=content_id,
            title=content.title,
            content_type=content.content_type.value,
            quality=request.quality,
            season_number=request.season_number,
            episode_number=request.episode_number,
            status="ready",
            streaming_url=f"/api/v1/streaming-content/{content_id}/chunk",
            access_token=access_token,
            chunk_size=file_obj.streaming_chunk_size,
            total_file_size=file_obj.file_size_bytes or 0,
            total_chunks=total_chunks,
            encryption_method="AES-256-CBC",
            duration_seconds=file_obj.duration_seconds,
            bitrate_kbps=file_obj.bitrate_kbps,
            video_codec=file_obj.video_codec,
            audio_codec=getattr(file_obj, "audio_codec", None),
            container_format=getattr(file_obj, "container_format", None),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            is_encrypted=True,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting streaming play URL: {str(e)}",
        )


@router.post("/{content_id}/chunk", response_model=ChunkResponse)
async def get_streaming_chunk(
    content_id: UUID,
    request: ChunkRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get a streaming chunk with decryption key.

    This endpoint:
    1. Validates the access token
    2. Downloads the requested chunk from S3
    3. Returns encrypted chunk + decryption key
    4. Tracks chunk access for analytics
    """
    try:
        # Validate access token
        token_data = validate_streaming_access_token(request.access_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired access token",
            )

        file_id = UUID(token_data["file_id"])

        # Get encryption key from database
        encryption_key_query = select(StreamingEncryptionKey).where(
            StreamingEncryptionKey.key_id == token_data["key_id"],
            StreamingEncryptionKey.is_active == True,
        )
        encryption_key_result = await db.execute(encryption_key_query)
        encryption_key = encryption_key_result.scalar_one_or_none()

        if not encryption_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Streaming encryption key not found",
            )

        # Get file information
        file_query = select(MovieFile).where(MovieFile.id == file_id)
        file_result = await db.execute(file_query)
        file_obj = file_result.scalar_one_or_none()

        if not file_obj:
            # Try episode quality
            episode_quality_query = select(EpisodeQuality).where(
                EpisodeQuality.id == file_id
            )
            episode_quality_result = await db.execute(episode_quality_query)
            file_obj = episode_quality_result.scalar_one_or_none()

        if not file_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        # Check chunk index validity
        total_chunks = file_obj.streaming_total_chunks or calculate_streaming_chunks(
            file_obj.file_size_bytes or 0, file_obj.streaming_chunk_size
        )

        if request.chunk_index >= total_chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Chunk index {request.chunk_index} is out of range (0-{total_chunks-1})",
            )

        # Decrypt file key
        file_key = decrypt_streaming_file_key(encryption_key.encrypted_key)

        # Generate chunk-specific key and IV
        chunk_key, iv = generate_chunk_encryption_key(file_key, request.chunk_index)

        # For now, return mock chunk data (in real implementation, you'd download from S3)
        # In production, you would:
        # 1. Download the specific chunk from S3 using range requests
        # 2. Encrypt the chunk with the chunk-specific key
        # 3. Return the encrypted chunk data

        mock_chunk_data = (
            b"Mock encrypted chunk data for chunk " + str(request.chunk_index).encode()
        )
        encrypted_chunk_data = (
            mock_chunk_data  # In real implementation, this would be encrypted
        )

        # Track chunk access
        chunk_access = StreamingChunkAccess(
            file_id=file_id,
            chunk_index=request.chunk_index,
            user_id=current_user.id,
            access_time=datetime.utcnow(),
        )
        db.add(chunk_access)
        await db.commit()

        return ChunkResponse(
            chunk_index=request.chunk_index,
            chunk_size=len(encrypted_chunk_data),
            total_chunks=total_chunks,
            chunk_data=encrypted_chunk_data.hex(),  # Return as hex string
            decryption_key=chunk_key.hex(),
            iv=iv.hex(),
            is_last_chunk=request.chunk_index == total_chunks - 1,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting streaming chunk: {str(e)}",
        )


@router.post("/license", response_model=LicenseResponse)
async def get_streaming_license(
    request: LicenseRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get streaming decryption license.

    This endpoint:
    1. Validates the access token
    2. Returns the decryption key
    3. Tracks key usage
    """
    try:
        # Validate access token
        token_data = validate_streaming_access_token(request.access_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired access token",
            )

        key_id = token_data["key_id"]
        file_id = token_data["file_id"]

        # Get encryption key from database
        encryption_key_query = select(StreamingEncryptionKey).where(
            StreamingEncryptionKey.key_id == key_id,
            StreamingEncryptionKey.is_active == True,
        )
        encryption_key_result = await db.execute(encryption_key_query)
        encryption_key = encryption_key_result.scalar_one_or_none()

        if not encryption_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Streaming encryption key not found",
            )

        # Check usage limits
        if (
            encryption_key.max_usage
            and encryption_key.usage_count >= encryption_key.max_usage
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Maximum usage limit reached for this key",
            )

        # Check expiration
        if encryption_key.expires_at and datetime.utcnow() > encryption_key.expires_at:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Streaming encryption key has expired",
            )

        # Increment usage count
        encryption_key.usage_count += 1
        await db.commit()

        return LicenseResponse(
            key_id=key_id,
            file_id=file_id,
            decryption_key=encryption_key.encrypted_key,
            usage_count=encryption_key.usage_count,
            max_usage=encryption_key.max_usage,
            expires_at=encryption_key.expires_at,
            token_expires_at=token_data["expires_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting streaming license: {str(e)}",
        )


@router.get("/{content_id}/encryption-status", response_model=EncryptionStatusResponse)
async def get_streaming_encryption_status(
    content_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get streaming encryption status for all files in content.
    """
    try:
        # Get content
        content_query = select(Content).where(Content.id == content_id)
        content_result = await db.execute(content_query)
        content = content_result.scalar_one_or_none()

        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTENT_NOT_FOUND,
            )

        files_status = []

        if content.content_type.value == "movie":
            # Get all movie files
            movie_files_query = select(MovieFile).where(
                MovieFile.content_id == content_id
            )
            movie_files_result = await db.execute(movie_files_query)
            movie_files = movie_files_result.scalars().all()

            for file_obj in movie_files:
                # Check encryption task status
                encryption_task_query = (
                    select(StreamingEncryptionTask)
                    .where(StreamingEncryptionTask.file_id == file_obj.id)
                    .order_by(StreamingEncryptionTask.created_at.desc())
                )
                encryption_task_result = await db.execute(encryption_task_query)
                encryption_task = encryption_task_result.scalar_one_or_none()

                files_status.append(
                    FileEncryptionStatus(
                        file_id=file_obj.id,
                        file_type="movie_file",
                        quality=file_obj.quality_level.value,
                        is_encrypted=file_obj.is_streaming_encrypted,
                        is_ready=file_obj.is_ready,
                        encryption_status=encryption_task.status.value
                        if encryption_task
                        else "not_started",
                        progress_percentage=encryption_task.progress_percentage
                        if encryption_task
                        else 0,
                        error_message=encryption_task.error_message
                        if encryption_task
                        else None,
                    )
                )

        elif content.content_type.value == "tv_series":
            # Get all episodes and their quality files
            episodes_query = select(Episode).where(Episode.content_id == content_id)
            episodes_result = await db.execute(episodes_query)
            episodes = episodes_result.scalars().all()

            for episode in episodes:
                episode_qualities_query = select(EpisodeQuality).where(
                    EpisodeQuality.episode_id == episode.id
                )
                episode_qualities_result = await db.execute(episode_qualities_query)
                episode_qualities = episode_qualities_result.scalars().all()

                for file_obj in episode_qualities:
                    # Check encryption task status
                    encryption_task_query = (
                        select(StreamingEncryptionTask)
                        .where(StreamingEncryptionTask.file_id == file_obj.id)
                        .order_by(StreamingEncryptionTask.created_at.desc())
                    )
                    encryption_task_result = await db.execute(encryption_task_query)
                    encryption_task = encryption_task_result.scalar_one_or_none()

                    files_status.append(
                        FileEncryptionStatus(
                            file_id=file_obj.id,
                            file_type="episode_quality",
                            season_number=episode.season_number,
                            episode_number=episode.episode_number,
                            quality=file_obj.quality_level.value,
                            is_encrypted=file_obj.is_streaming_encrypted,
                            is_ready=file_obj.is_ready,
                            encryption_status=encryption_task.status.value
                            if encryption_task
                            else "not_started",
                            progress_percentage=encryption_task.progress_percentage
                            if encryption_task
                            else 0,
                            error_message=encryption_task.error_message
                            if encryption_task
                            else None,
                        )
                    )

        # Calculate overall status
        total_files = len(files_status)
        encrypted_files = sum(1 for f in files_status if f.is_encrypted)
        processing_files = sum(
            1 for f in files_status if f.encryption_status in ["processing"]
        )
        failed_files = sum(1 for f in files_status if f.encryption_status == "failed")

        overall_status = "completed"
        if processing_files > 0:
            overall_status = "processing"
        elif failed_files > 0:
            overall_status = "partial_failure"
        elif encrypted_files == 0:
            overall_status = "not_started"

        return EncryptionStatusResponse(
            content_id=content_id,
            title=content.title,
            content_type=content.content_type.value,
            overall_status=overall_status,
            total_files=total_files,
            encrypted_files=encrypted_files,
            processing_files=processing_files,
            failed_files=failed_files,
            files=files_status,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting streaming encryption status: {str(e)}",
        )
