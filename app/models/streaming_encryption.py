"""
Streaming Encryption Models
Database models for streaming encryption
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel, TimestampMixin


class StreamingEncryptionStatus(str, Enum):
    """Status of streaming encryption"""

    NOT_STARTED = "not_started"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class StreamingEncryptionKey(BaseModel, TimestampMixin, table=True):
    """
    Stores streaming encryption keys for content files.
    Each key is associated with a specific content file (MovieFile or EpisodeQuality).
    """

    __tablename__ = "streaming_encryption_keys"

    file_id: UUID = Field(
        nullable=False, index=True, description="ID of the MovieFile or EpisodeQuality"
    )
    file_type: str = Field(
        nullable=False, description="Type of file (movie_file or episode_quality)"
    )
    encrypted_key: str = Field(
        nullable=False, description="The encrypted file key (base64)"
    )
    key_id: str = Field(
        nullable=False, unique=True, index=True, description="Unique ID for the key"
    )
    expires_at: Optional[datetime] = Field(
        default=None, description="When the key expires"
    )
    usage_count: int = Field(
        default=0, description="How many times this key has been used"
    )
    max_usage: Optional[int] = Field(
        default=None, description="Maximum number of times this key can be used"
    )
    is_active: bool = Field(default=True, description="Whether the key is active")


class StreamingEncryptionTask(BaseModel, TimestampMixin, table=True):
    """
    Tracks streaming encryption tasks for files.
    """

    __tablename__ = "streaming_encryption_tasks"

    file_id: UUID = Field(
        nullable=False, index=True, description="ID of the MovieFile or EpisodeQuality"
    )
    file_type: str = Field(
        nullable=False, description="Type of file (movie_file or episode_quality)"
    )
    status: StreamingEncryptionStatus = Field(
        default=StreamingEncryptionStatus.NOT_STARTED, description="Encryption status"
    )
    progress_percentage: int = Field(
        default=0, description="Progress percentage (0-100)"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if encryption failed"
    )
    started_at: Optional[datetime] = Field(
        default=None, description="When encryption started"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="When encryption completed"
    )
    chunk_size: int = Field(
        default=1048576, description="Chunk size used for encryption (1MB)"
    )
    total_chunks: int = Field(default=0, description="Total number of chunks")


class StreamingChunkAccess(BaseModel, TimestampMixin, table=True):
    """
    Tracks access to streaming chunks for analytics and security.
    """

    __tablename__ = "streaming_chunk_access"

    file_id: UUID = Field(
        nullable=False, index=True, description="ID of the MovieFile or EpisodeQuality"
    )
    chunk_index: int = Field(
        nullable=False, description="Chunk index that was accessed"
    )
    user_id: Optional[UUID] = Field(
        default=None, index=True, description="User who accessed the chunk"
    )
    ip_address: Optional[str] = Field(
        default=None, description="IP address of the request"
    )
    user_agent: Optional[str] = Field(
        default=None, description="User agent of the request"
    )
    access_time: datetime = Field(
        default_factory=datetime.utcnow, description="When the chunk was accessed"
    )
