"""
Video processing utilities for content management
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.messages import FILE_PROCESSING_FAILED, FILE_PROCESSING_STARTED
from app.models.content import Content, Episode, EpisodeQuality, MovieFile, WatchQuality

logger = logging.getLogger(__name__)


class VideoProcessingTask:
    """Background task for video processing and transcoding"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_content_video(
        self,
        content_id: UUID,
        video_url: str,
        original_filename: str,
        file_size_bytes: Optional[int] = None,
    ) -> Dict[str, any]:
        """
        Process video for content (movie or TV series)

        Args:
            content_id: Content ID
            video_url: URL of uploaded video
            original_filename: Original filename
            file_size_bytes: File size in bytes

        Returns:
            Dict with processing results
        """
        try:
            # Get content from database
            content = await self._get_content(content_id)
            if not content:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
                )

            # Start processing
            logger.info(f"Starting video processing for content {content_id}")

            # For movies, create MovieFile entries
            if content.content_type.value == "movie":
                return await self._process_movie_video(
                    content, video_url, original_filename, file_size_bytes
                )

            # For TV series, this would typically be an episode
            # We'll handle this case separately
            else:
                return await self._process_series_video(
                    content, video_url, original_filename, file_size_bytes
                )

        except Exception as e:
            logger.error(f"Error processing video for content {content_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Video processing failed: {str(e)}",
            )

    async def process_episode_video(
        self,
        episode_id: UUID,
        video_url: str,
        original_filename: str,
        file_size_bytes: Optional[int] = None,
    ) -> Dict[str, any]:
        """
        Process video for episode

        Args:
            episode_id: Episode ID
            video_url: URL of uploaded video
            original_filename: Original filename
            file_size_bytes: File size in bytes

        Returns:
            Dict with processing results
        """
        try:
            # Get episode from database
            episode = await self._get_episode(episode_id)
            if not episode:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found"
                )

            # Start processing
            logger.info(f"Starting video processing for episode {episode_id}")

            # Update episode with video URL
            episode.video_file_url = video_url
            episode.processing_status = "processing"
            if file_size_bytes:
                episode.file_size_bytes = file_size_bytes

            await self.db.commit()
            await self.db.refresh(episode)

            # Simulate video processing (in real implementation, this would call FFmpeg)
            processing_results = await self._simulate_video_processing(
                video_url, original_filename
            )

            # Create quality versions
            quality_versions = await self._create_episode_quality_versions(
                episode, processing_results
            )

            # Update episode processing status
            episode.processing_status = "completed"
            await self.db.commit()

            return {
                "message": FILE_PROCESSING_STARTED,
                "episode_id": str(episode_id),
                "video_url": video_url,
                "quality_versions": quality_versions,
                "processing_results": processing_results,
            }

        except Exception as e:
            logger.error(f"Error processing video for episode {episode_id}: {str(e)}")
            # Update episode status to failed
            if episode:
                episode.processing_status = "failed"
                await self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Video processing failed: {str(e)}",
            )

    async def _get_content(self, content_id: UUID) -> Optional[Content]:
        """Get content by ID"""
        result = await self.db.execute(select(Content).where(Content.id == content_id))
        return result.scalar_one_or_none()

    async def _get_episode(self, episode_id: UUID) -> Optional[Episode]:
        """Get episode by ID"""
        result = await self.db.execute(select(Episode).where(Episode.id == episode_id))
        return result.scalar_one_or_none()

    async def _process_movie_video(
        self,
        content: Content,
        video_url: str,
        original_filename: str,
        file_size_bytes: Optional[int] = None,
    ) -> Dict[str, any]:
        """Process video for movie content"""

        # Simulate video processing
        processing_results = await self._simulate_video_processing(
            video_url, original_filename
        )

        # Create movie file entries for different qualities
        movie_files = await self._create_movie_file_versions(
            content, video_url, processing_results, file_size_bytes
        )

        return {
            "message": FILE_PROCESSING_STARTED,
            "content_id": str(content.id),
            "content_type": content.content_type.value,
            "video_url": video_url,
            "movie_files": movie_files,
            "processing_results": processing_results,
        }

    async def _process_series_video(
        self,
        content: Content,
        video_url: str,
        original_filename: str,
        file_size_bytes: Optional[int] = None,
    ) -> Dict[str, any]:
        """Process video for TV series content"""

        # For TV series, we typically don't upload videos directly to content
        # Videos are uploaded to episodes
        logger.warning(
            f"Video upload to TV series content {content.id} - should be episode-specific"
        )

        return {
            "message": "Video uploaded to TV series content - consider uploading to specific episodes",
            "content_id": str(content.id),
            "content_type": content.content_type.value,
            "video_url": video_url,
            "note": "For TV series, upload videos to specific episodes instead",
        }

    async def _simulate_video_processing(
        self, video_url: str, original_filename: str
    ) -> Dict[str, any]:
        """
        Simulate video processing (in real implementation, this would use FFmpeg)

        This is a placeholder for actual video processing logic
        """
        # Simulate processing delay
        await asyncio.sleep(2)

        # Mock processing results
        return {
            "duration_seconds": 7200,  # 2 hours
            "resolution_width": 1920,
            "resolution_height": 1080,
            "bitrate_kbps": 5000,
            "video_codec": "h264",
            "audio_codec": "aac",
            "container_format": "mp4",
            "frame_rate": 24.0,
            "processing_time_seconds": 2,
            "original_filename": original_filename,
            "processed_qualities": ["1080p", "720p", "480p", "360p"],
        }

    async def _create_movie_file_versions(
        self,
        content: Content,
        video_url: str,
        processing_results: Dict[str, any],
        file_size_bytes: Optional[int] = None,
    ) -> List[Dict[str, any]]:
        """Create movie file entries for different quality versions"""

        movie_files = []
        qualities = [
            (WatchQuality.QUALITY_1080P, 1920, 1080),
            (WatchQuality.QUALITY_720P, 1280, 720),
            (WatchQuality.QUALITY_480P, 854, 480),
            (WatchQuality.QUALITY_360P, 640, 360),
        ]

        for quality, width, height in qualities:
            # Create movie file entry
            movie_file = MovieFile(
                content_id=content.id,
                quality_level=quality,
                resolution_width=width,
                resolution_height=height,
                file_url=video_url,  # In real implementation, this would be different URLs
                file_size_bytes=file_size_bytes,
                duration_seconds=processing_results["duration_seconds"],
                bitrate_kbps=processing_results["bitrate_kbps"],
                video_codec=processing_results["video_codec"],
                audio_codec=processing_results["audio_codec"],
                container_format=processing_results["container_format"],
                is_ready=True,  # In real implementation, this would be False initially
            )

            self.db.add(movie_file)
            movie_files.append(
                {
                    "quality": quality.value,
                    "resolution": f"{width}x{height}",
                    "file_url": video_url,
                    "is_ready": True,
                }
            )

        await self.db.commit()
        return movie_files

    async def _create_episode_quality_versions(
        self,
        episode: Episode,
        processing_results: Dict[str, any],
    ) -> List[Dict[str, any]]:
        """Create episode quality versions"""

        quality_versions = []
        qualities = [
            (WatchQuality.QUALITY_1080P, 1920, 1080),
            (WatchQuality.QUALITY_720P, 1280, 720),
            (WatchQuality.QUALITY_480P, 854, 480),
            (WatchQuality.QUALITY_360P, 640, 360),
        ]

        for quality, width, height in qualities:
            # Create episode quality entry
            episode_quality = EpisodeQuality(
                episode_id=episode.id,
                quality_level=quality,
                resolution_width=width,
                resolution_height=height,
                file_url=episode.video_file_url,  # In real implementation, this would be different URLs
                file_size_bytes=episode.file_size_bytes,
                duration_seconds=processing_results["duration_seconds"],
                bitrate_kbps=processing_results["bitrate_kbps"],
                video_codec=processing_results["video_codec"],
                is_ready=True,  # In real implementation, this would be False initially
            )

            self.db.add(episode_quality)
            quality_versions.append(
                {
                    "quality": quality.value,
                    "resolution": f"{width}x{height}",
                    "file_url": episode.video_file_url,
                    "is_ready": True,
                }
            )

        await self.db.commit()
        return quality_versions


async def start_video_processing_task(
    db: AsyncSession,
    content_id: Optional[UUID] = None,
    episode_id: Optional[UUID] = None,
    video_url: str = "",
    original_filename: str = "",
    file_size_bytes: Optional[int] = None,
) -> Dict[str, any]:
    """
    Start background video processing task

    Args:
        db: Database session
        content_id: Content ID (for movie content)
        episode_id: Episode ID (for episode content)
        video_url: URL of uploaded video
        original_filename: Original filename
        file_size_bytes: File size in bytes

    Returns:
        Dict with processing results
    """
    processor = VideoProcessingTask(db)

    if content_id:
        return await processor.process_content_video(
            content_id, video_url, original_filename, file_size_bytes
        )
    elif episode_id:
        return await processor.process_episode_video(
            episode_id, video_url, original_filename, file_size_bytes
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either content_id or episode_id must be provided",
        )
