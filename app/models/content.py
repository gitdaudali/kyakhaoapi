import uuid
from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class ContentType(str, Enum):
    MOVIE = "movie"
    TV_SERIES = "tv_series"
    DOCUMENTARY = "documentary"
    ANIME = "anime"
    SHORT_FILM = "short_film"
    MINI_SERIES = "mini_series"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    PUBLISHED = "published"
    COMING_SOON = "coming_soon"
    ARCHIVED = "archived"
    BLOCKED = "blocked"


class ContentRating(str, Enum):
    G = "G"
    PG = "PG"
    PG_13 = "PG-13"
    R = "R"
    NC_17 = "NC-17"
    TV_Y = "TV-Y"
    TV_Y7 = "TV-Y7"
    TV_G = "TV-G"
    TV_PG = "TV-PG"
    TV_14 = "TV-14"
    TV_MA = "TV-MA"
    UNRATED = "unrated"


class DeviceType(str, Enum):
    MOBILE = "mobile"
    DESKTOP = "desktop"
    TABLET = "tablet"
    SMART_TV = "smart_tv"
    GAMING_CONSOLE = "gaming_console"
    STREAMING_DEVICE = "streaming_device"


class InteractionType(str, Enum):
    LIKE = "like"
    FAVORITE = "favorite"
    WATCHLIST = "watchlist"
    DISLIKE = "dislike"
    SHARE = "share"


class WatchQuality(str, Enum):
    AUTO = "auto"
    QUALITY_240P = "240p"
    QUALITY_360P = "360p"
    QUALITY_480P = "480p"
    QUALITY_720P = "720p"
    QUALITY_1080P = "1080p"
    QUALITY_1440P = "1440p"
    QUALITY_4K = "4k"
    QUALITY_8K = "8k"


class Content(BaseModel, TimestampMixin, table=True):
    """Main content model for movies, TV series, documentaries, etc."""

    __tablename__ = "contents"

    # Basic Information
    title: str = Field(sa_type=String(255), nullable=False, index=True)
    slug: str = Field(sa_type=String(300), unique=True, index=True)
    description: Optional[str] = Field(sa_type=Text, default=None)
    tagline: Optional[str] = Field(sa_type=String(500), default=None)

    # Content Classification
    content_type: ContentType = Field(sa_type=String(20), nullable=False, index=True)
    status: ContentStatus = Field(
        sa_type=String(20), default=ContentStatus.DRAFT, index=True
    )
    content_rating: Optional[ContentRating] = Field(sa_type=String(10), default=None)

    # Visual Assets
    poster_url: Optional[str] = Field(sa_type=String(500), default=None)
    backdrop_url: Optional[str] = Field(sa_type=String(500), default=None)
    trailer_url: Optional[str] = Field(sa_type=String(500), default=None)
    logo_url: Optional[str] = Field(sa_type=String(500), default=None)
    thumbnail_grid: Optional[str] = Field(
        sa_type=Text, default=None
    )  # JSON array of thumbnail URLs

    # Release Information
    release_date: Optional[date] = Field(sa_type=Date, default=None, index=True)
    premiere_date: Optional[date] = Field(sa_type=Date, default=None)
    end_date: Optional[date] = Field(
        sa_type=Date, default=None
    )  # For series that ended

    # Ratings from External Sources
    imdb_rating: Optional[float] = Field(sa_type=Float, default=None)
    imdb_votes: Optional[int] = Field(sa_type=Integer, default=None)
    stream_vibe: Optional[float] = Field(sa_type=Float, default=None)
    stream_vibe_votes: Optional[int] = Field(sa_type=Integer, default=None)

    # Platform Rating
    platform_rating: Optional[float] = Field(sa_type=Float, default=None, index=True)
    platform_votes: int = Field(sa_type=Integer, default=0)

    # Technical Information
    runtime: Optional[int] = Field(sa_type=Integer, default=None)
    language: str = Field(sa_type=String(10), default="en", index=True)
    original_language: Optional[str] = Field(sa_type=String(10), default=None)
    spoken_languages: Optional[str] = Field(sa_type=Text, default=None)  # JSON array

    # Series-specific Information
    total_seasons: int = Field(sa_type=Integer, default=0)
    total_episodes: int = Field(sa_type=Integer, default=0)
    is_ongoing: bool = Field(sa_type=Boolean, default=False)
    next_episode_date: Optional[date] = Field(sa_type=Date, default=None)

    # Platform Features
    is_featured: bool = Field(sa_type=Boolean, default=False, index=True)
    is_trending: bool = Field(sa_type=Boolean, default=False, index=True)
    is_new_release: bool = Field(sa_type=Boolean, default=False, index=True)
    is_premium: bool = Field(sa_type=Boolean, default=False, index=True)

    # Availability
    available_from: Optional[datetime] = Field(
        sa_type=DateTime(timezone=True), default=None
    )
    available_until: Optional[datetime] = Field(
        sa_type=DateTime(timezone=True), default=None
    )
    geographic_restrictions: Optional[str] = Field(sa_type=Text, default=None)

    # Engagement Metrics (denormalized for performance)
    total_views: int = Field(sa_type=Integer, default=0, index=True)
    likes_count: int = Field(sa_type=Integer, default=0, index=True)
    reviews_count: int = Field(sa_type=Integer, default=0, index=True)

    # Quality Metrics
    average_completion_rate: Optional[float] = Field(sa_type=Float, default=None)
    average_rating: Optional[float] = Field(sa_type=Float, default=None)

    # Discovery
    keywords: Optional[str] = Field(sa_type=Text, default=None)
    search_keywords: Optional[str] = Field(sa_type=Text, default=None)

    # Relationships
    genres: List["Genre"] = Relationship(
        back_populates="contents",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "secondary": "content_genres",
        },
    )
    seasons: List["Season"] = Relationship(
        back_populates="content",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan",
            "order_by": "Season.season_number",
        },
    )
    episodes: List["Episode"] = Relationship(
        back_populates="content",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )
    reviews: List["ContentReview"] = Relationship(
        back_populates="content",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )
    interactions: List["UserContentInteraction"] = Relationship(
        back_populates="content",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )
    watch_sessions: List["WatchSession"] = Relationship(
        back_populates="content",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )
    content_views: List["ContentView"] = Relationship(
        back_populates="content",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )
    watch_history: List["UserWatchHistory"] = Relationship(
        back_populates="content",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )
    # Movie files relationship
    movie_files: List["MovieFile"] = Relationship(
        back_populates="content",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan",
            "order_by": "MovieFile.quality_level.desc()",
        },
    )
    # People relationships
    cast: List["ContentCast"] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan",
            "order_by": "ContentCast.cast_order",
        },
    )
    crew: List["ContentCrew"] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan",
            "order_by": "ContentCrew.credit_order",
        },
    )

    def __repr__(self):
        return (
            f"<Content(id={self.id}, title='{self.title}', type='{self.content_type}')>"
        )


class Season(BaseModel, TimestampMixin, table=True):
    """Seasons for TV series content"""

    __tablename__ = "seasons"

    content_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="contents.id",
        nullable=False,
        index=True,
    )
    season_number: int = Field(sa_type=Integer, nullable=False, index=True)
    title: Optional[str] = Field(sa_type=String(255), default=None)
    description: Optional[str] = Field(sa_type=Text, default=None)

    # Visual Assets
    poster_url: Optional[str] = Field(sa_type=String(500), default=None)
    backdrop_url: Optional[str] = Field(sa_type=String(500), default=None)

    # Air Dates
    air_date: Optional[date] = Field(sa_type=Date, default=None, index=True)
    end_date: Optional[date] = Field(sa_type=Date, default=None)

    # Season Metrics
    episode_count: int = Field(sa_type=Integer, default=0)

    # Status
    is_complete: bool = Field(sa_type=Boolean, default=False)

    # Relationships
    content: "Content" = Relationship(back_populates="seasons")
    episodes: List["Episode"] = Relationship(
        back_populates="season",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan",
            "order_by": "Episode.episode_number",
        },
    )

    __table_args__ = (
        UniqueConstraint("content_id", "season_number", name="unique_content_season"),
    )

    def __repr__(self):
        return f"<Season(id={self.id}, content_id={self.content_id}, season={self.season_number})>"


class Episode(BaseModel, TimestampMixin, table=True):
    """Individual episodes for TV series"""

    __tablename__ = "episodes"

    content_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="contents.id",
        nullable=False,
        index=True,
    )
    season_id: Optional[uuid.UUID] = Field(
        sa_type=UUID(as_uuid=True), foreign_key="seasons.id", default=None, index=True
    )
    episode_number: int = Field(sa_type=Integer, nullable=False, index=True)
    title: str = Field(sa_type=String(255), nullable=False)
    slug: str = Field(sa_type=String(300), index=True)
    description: Optional[str] = Field(sa_type=Text, default=None)
    tag_line: Optional[str] = Field(sa_type=Text, default=None)

    # Technical Information
    runtime: Optional[int] = Field(sa_type=Integer, default=None)

    # Air Information
    air_date: Optional[date] = Field(sa_type=Date, default=None, index=True)

    # Video Files and Storage
    video_file_url: str = Field(sa_type=String(500), nullable=False)
    thumbnail_url: Optional[str] = Field(sa_type=String(500), default=None)
    preview_url: Optional[str] = Field(
        sa_type=String(500), default=None
    )  # Short preview clip

    # File Technical Details
    file_size_bytes: Optional[int] = Field(sa_type=Integer, default=None)
    video_codec: Optional[str] = Field(sa_type=String(50), default=None)
    audio_codec: Optional[str] = Field(sa_type=String(50), default=None)
    container_format: Optional[str] = Field(
        sa_type=String(20), default=None
    )  # mp4, mkv, webm
    bitrate_kbps: Optional[int] = Field(sa_type=Integer, default=None)
    frame_rate: Optional[float] = Field(sa_type=Float, default=None)

    # Cloud Storage Information
    storage_bucket: Optional[str] = Field(sa_type=String(255), default=None)
    storage_key: Optional[str] = Field(sa_type=String(500), default=None)
    storage_region: Optional[str] = Field(sa_type=String(50), default=None)
    cdn_url: Optional[str] = Field(sa_type=String(500), default=None)

    # Processing Status
    processing_status: str = Field(sa_type=String(20), default="pending", index=True)

    # Subtitles and Audio Tracks
    subtitle_tracks: Optional[str] = Field(sa_type=Text, default=None)
    audio_tracks: Optional[str] = Field(sa_type=Text, default=None)
    available_languages: Optional[str] = Field(sa_type=Text, default=None)

    # Episode-specific Metrics
    views_count: int = Field(sa_type=Integer, default=0, index=True)
    average_completion_rate: Optional[float] = Field(sa_type=Float, default=None)

    # Availability
    is_available: bool = Field(sa_type=Boolean, default=True, index=True)
    available_from: Optional[datetime] = Field(
        sa_type=DateTime(timezone=True), default=None
    )
    available_until: Optional[datetime] = Field(
        sa_type=DateTime(timezone=True), default=None
    )

    # Relationships
    content: "Content" = Relationship(back_populates="episodes")
    season: Optional["Season"] = Relationship(back_populates="episodes")
    episode_views: List["EpisodeView"] = Relationship(
        back_populates="episode",
        sa_relationship_kwargs={
            "lazy": "dynamic",
            "cascade": "all, delete-orphan",
            "foreign_keys": "[EpisodeView.episode_id]",
        },
    )
    quality_versions: List["EpisodeQuality"] = Relationship(
        back_populates="episode",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )

    __table_args__ = (
        UniqueConstraint(
            "content_id", "season_id", "episode_number", name="unique_season_episode"
        ),
        UniqueConstraint("content_id", "slug", name="unique_content_episode_slug"),
    )

    def __repr__(self):
        return f"<Episode(id={self.id}, title='{self.title}', S{self.season_id}E{self.episode_number})>"


# =============================================================================
# VIDEO QUALITY AND VERSIONS
# =============================================================================


class EpisodeQuality(BaseModel, TimestampMixin, table=True):
    """Different quality versions of episodes"""

    __tablename__ = "episode_qualities"

    episode_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="episodes.id",
        nullable=False,
        index=True,
    )
    quality_level: WatchQuality = Field(sa_type=String(10), nullable=False)
    resolution_width: int = Field(sa_type=Integer, nullable=False)
    resolution_height: int = Field(sa_type=Integer, nullable=False)

    # File Information
    file_url: str = Field(sa_type=String(500), nullable=False)
    file_size_bytes: Optional[int] = Field(sa_type=Integer, default=None)
    bitrate_kbps: Optional[int] = Field(sa_type=Integer, default=None)
    video_codec: Optional[str] = Field(sa_type=String(50), default=None)

    # Storage Information
    storage_bucket: Optional[str] = Field(sa_type=String(255), default=None)
    storage_key: Optional[str] = Field(sa_type=String(500), default=None)
    cdn_url: Optional[str] = Field(sa_type=String(500), default=None)

    # Processing Status
    is_ready: bool = Field(sa_type=Boolean, default=False, index=True)

    # Relationships
    episode: "Episode" = Relationship(back_populates="quality_versions")

    __table_args__ = (
        UniqueConstraint("episode_id", "quality_level", name="unique_episode_quality"),
    )


class MovieFile(BaseModel, TimestampMixin, table=True):
    """Movie files for movie-type content"""

    __tablename__ = "movie_files"

    content_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="contents.id",
        nullable=False,
        index=True,
    )
    quality_level: WatchQuality = Field(sa_type=String(10), nullable=False)
    resolution_width: int = Field(sa_type=Integer, nullable=False)
    resolution_height: int = Field(sa_type=Integer, nullable=False)

    # File Information
    file_url: str = Field(sa_type=String(500), nullable=False)
    file_size_bytes: Optional[int] = Field(sa_type=BigInteger, default=None)
    duration_seconds: float = Field(sa_type=Float, nullable=False)
    bitrate_kbps: Optional[int] = Field(sa_type=Integer, default=None)
    video_codec: Optional[str] = Field(sa_type=String(50), default=None)
    audio_codec: Optional[str] = Field(sa_type=String(50), default=None)
    container_format: Optional[str] = Field(sa_type=String(20), default=None)

    # Storage Information
    storage_bucket: Optional[str] = Field(sa_type=String(255), default=None)
    storage_key: Optional[str] = Field(sa_type=String(500), default=None)
    storage_region: Optional[str] = Field(sa_type=String(50), default=None)
    cdn_url: Optional[str] = Field(sa_type=String(500), default=None)

    # Processing Status
    is_ready: bool = Field(sa_type=Boolean, default=False, index=True)

    # Subtitle and Audio Information
    subtitle_tracks: Optional[str] = Field(sa_type=Text, default=None)  # JSON
    audio_tracks: Optional[str] = Field(sa_type=Text, default=None)  # JSON
    available_languages: Optional[str] = Field(sa_type=Text, default=None)  # JSON

    # Relationships
    content: "Content" = Relationship(back_populates="movie_files")

    __table_args__ = (
        UniqueConstraint("content_id", "quality_level", name="unique_movie_quality"),
    )


class Genre(BaseModel, TimestampMixin, table=True):
    """Content genres for categorization"""

    __tablename__ = "genres"

    name: str = Field(sa_type=String(100), unique=True, index=True)
    slug: str = Field(sa_type=String(120), unique=True, index=True)
    description: Optional[str] = Field(sa_type=Text, default=None)

    # Visual Elements
    icon_name: Optional[str] = Field(sa_type=String(100), default=None)
    cover_image_url: Optional[str] = Field(sa_type=String(500), default=None)

    # Hierarchy (for sub-genres)
    parent_genre_id: Optional[uuid.UUID] = Field(
        sa_type=UUID(as_uuid=True), foreign_key="genres.id", default=None
    )

    # Status and Ordering
    is_active: bool = Field(sa_type=Boolean, default=True, index=True)
    is_featured: bool = Field(sa_type=Boolean, default=False)
    sort_order: int = Field(sa_type=Integer, default=0)

    # Analytics
    content_count: int = Field(sa_type=Integer, default=0)

    # Relationships
    contents: List["Content"] = Relationship(
        back_populates="genres",
        sa_relationship_kwargs={
            "lazy": "dynamic",
            "secondary": "content_genres",
        },
    )
    parent_genre: Optional["Genre"] = Relationship(
        sa_relationship_kwargs={"remote_side": "Genre.id"}
    )
    sub_genres: List["Genre"] = Relationship(
        sa_relationship_kwargs={"remote_side": "Genre.id", "overlaps": "parent_genre"},
    )

    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"


class ContentGenre(BaseModel, table=True):
    """Many-to-many relationship between content and genres"""

    __tablename__ = "content_genres"

    content_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="contents.id", primary_key=True
    )
    genre_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="genres.id", primary_key=True
    )
    is_primary: bool = Field(sa_type=Boolean, default=False)
    relevance_score: Optional[float] = Field(sa_type=Float, default=None)


class Person(BaseModel, TimestampMixin, table=True):
    """People involved in content (actors, directors, writers, etc.)"""

    __tablename__ = "people"

    name: str = Field(sa_type=String(255), nullable=False, index=True)
    slug: str = Field(sa_type=String(300), unique=True, index=True)
    biography: Optional[str] = Field(sa_type=Text, default=None)

    # Personal Information
    birth_date: Optional[date] = Field(sa_type=Date, default=None)
    death_date: Optional[date] = Field(sa_type=Date, default=None)
    birth_place: Optional[str] = Field(sa_type=String(255), default=None)
    nationality: Optional[str] = Field(sa_type=String(100), default=None)
    gender: Optional[str] = Field(sa_type=String(20), default=None)

    # Visual Assets
    profile_image_url: Optional[str] = Field(sa_type=String(500), default=None)
    cover_image_url: Optional[str] = Field(sa_type=String(500), default=None)

    # Career Information
    known_for_department: Optional[str] = Field(
        sa_type=String(100), default=None
    )  # Acting, Directing, Writing

    # Status
    is_verified: bool = Field(sa_type=Boolean, default=False)
    is_featured: bool = Field(sa_type=Boolean, default=False)

    def __repr__(self):
        return f"<Person(id={self.id}, name='{self.name}')>"


class ContentCast(BaseModel, table=True):
    """Cast members for content"""

    __tablename__ = "content_cast"

    content_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="contents.id", primary_key=True
    )
    person_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="people.id", primary_key=True
    )
    character_name: Optional[str] = Field(sa_type=String(255), default=None)
    cast_order: int = Field(sa_type=Integer, default=0)  # Billing order
    is_main_cast: bool = Field(sa_type=Boolean, default=False)
    character_image_url: Optional[str] = Field(sa_type=String(500), default=None)

    # Relationships
    content: "Content" = Relationship()
    person: "Person" = Relationship()


class ContentCrew(BaseModel, table=True):
    """Crew members for content"""

    __tablename__ = "content_crew"

    content_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="contents.id", primary_key=True
    )
    person_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="people.id", primary_key=True
    )
    job_title: str = Field(
        sa_type=String(100), nullable=False
    )  # Director, Producer, Writer, etc.
    department: str = Field(
        sa_type=String(100), nullable=False
    )  # Directing, Production, Writing, etc.
    credit_order: int = Field(sa_type=Integer, default=0)

    # Relationships
    content: "Content" = Relationship()
    person: "Person" = Relationship()


class UserContentInteraction(BaseModel, TimestampMixin, table=True):
    """User interactions with content (likes, favorites, watchlist)"""

    __tablename__ = "user_content_interactions"

    user_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="users.id", nullable=False, index=True
    )
    content_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="contents.id",
        nullable=False,
        index=True,
    )
    interaction_type: InteractionType = Field(
        sa_type=String(20), nullable=False, index=True
    )

    # Additional context
    note: Optional[str] = Field(sa_type=Text, default=None)  # User's personal note
    priority: Optional[int] = Field(
        sa_type=Integer, default=None
    )  # For watchlist ordering

    # Relationships
    user: "User" = Relationship(back_populates="user_content_interactions")
    content: "Content" = Relationship(back_populates="interactions")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "content_id",
            "interaction_type",
            name="unique_user_content_interaction",
        ),
    )


class ContentReview(BaseModel, TimestampMixin, table=True):
    """User reviews for content"""

    __tablename__ = "content_reviews"

    content_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="contents.id",
        nullable=False,
        index=True,
    )
    user_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="users.id", nullable=False, index=True
    )

    # Review Content
    rating: float = Field(sa_type=Float, nullable=False)  # 1.0 - 5.0 scale
    title: Optional[str] = Field(sa_type=String(255), default=None)
    review_text: Optional[str] = Field(sa_type=Text, default=None)

    # Review Metadata
    language: str = Field(sa_type=String(10), default="en")

    # Moderation
    status: str = Field(
        sa_type=String(20), default="published", index=True
    )  # published, hidden, flagged
    is_featured: bool = Field(sa_type=Boolean, default=False)

    # Engagement
    helpful_votes: int = Field(sa_type=Integer, default=0)
    total_votes: int = Field(sa_type=Integer, default=0)

    # Review Updates
    is_edited: bool = Field(sa_type=Boolean, default=False)
    last_edited_at: Optional[datetime] = Field(
        sa_type=DateTime(timezone=True), default=None
    )

    # Relationships
    content: "Content" = Relationship(back_populates="reviews")
    user: "User" = Relationship(back_populates="content_reviews")

    __table_args__ = (
        UniqueConstraint("content_id", "user_id", name="unique_user_content_review"),
    )


class ContentView(BaseModel, TimestampMixin, table=True):
    """High-level content view tracking"""

    __tablename__ = "content_views"

    content_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="contents.id",
        nullable=False,
        index=True,
    )
    viewer_id: Optional[uuid.UUID] = Field(
        sa_type=UUID(as_uuid=True), foreign_key="users.id", default=None, index=True
    )

    # Relationships
    content: "Content" = Relationship(back_populates="content_views")
    viewer: Optional["User"] = Relationship()


class EpisodeView(BaseModel, TimestampMixin, table=True):
    """episode viewing analytics"""

    __tablename__ = "episode_views"

    episode_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="episodes.id",
        nullable=False,
        index=True,
    )
    viewer_id: Optional[uuid.UUID] = Field(
        sa_type=UUID(as_uuid=True), foreign_key="users.id", default=None, index=True
    )

    # Quality and Performance
    quality_watched: Optional[WatchQuality] = Field(sa_type=String(10), default=None)

    # Session Context
    session_id: Optional[str] = Field(sa_type=String(255), default=None, index=True)
    device_type: Optional[DeviceType] = Field(sa_type=String(20), default=None)

    # Viewing Context
    is_binge_watch: bool = Field(
        sa_type=Boolean, default=False
    )  # Part of consecutive episode viewing
    came_from_episode_id: Optional[uuid.UUID] = Field(
        sa_type=UUID(as_uuid=True), foreign_key="episodes.id", default=None
    )

    # Audio/Video Settings
    subtitle_language: Optional[str] = Field(sa_type=String(10), default=None)
    audio_language: Optional[str] = Field(sa_type=String(10), default=None)

    # Relationships
    episode: "Episode" = Relationship(
        back_populates="episode_views",
        sa_relationship_kwargs={"foreign_keys": "[EpisodeView.episode_id]"},
    )
    viewer: Optional["User"] = Relationship()


class WatchSession(BaseModel, TimestampMixin, table=True):
    """User watch sessions for progress tracking"""

    __tablename__ = "watch_sessions"

    user_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="users.id", nullable=False, index=True
    )
    content_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="contents.id",
        nullable=False,
        index=True,
    )
    episode_id: Optional[uuid.UUID] = Field(
        sa_type=UUID(as_uuid=True), foreign_key="episodes.id", default=None, index=True
    )

    # Session Details
    session_id: str = Field(sa_type=String(255), nullable=False, index=True)
    device_type: Optional[DeviceType] = Field(sa_type=String(20), default=None)

    # Quality Settings
    quality_setting: Optional[WatchQuality] = Field(sa_type=String(10), default=None)

    # Relationships
    user: "User" = Relationship(back_populates="watch_sessions")
    content: "Content" = Relationship(back_populates="watch_sessions")


class UserWatchHistory(BaseModel, TimestampMixin, table=True):
    """User's comprehensive watch history with resume points"""

    __tablename__ = "user_watch_history"

    user_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="users.id", nullable=False, index=True
    )
    content_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="contents.id",
        nullable=False,
        index=True,
    )

    # Current Progress
    current_episode_id: Optional[uuid.UUID] = Field(
        sa_type=UUID(as_uuid=True), foreign_key="episodes.id", default=None
    )
    current_position_seconds: int = Field(sa_type=Integer, default=0)

    # Overall Progress
    total_episodes_watched: int = Field(sa_type=Integer, default=0)

    # Status
    is_completed: bool = Field(sa_type=Boolean, default=False)
    is_currently_watching: bool = Field(sa_type=Boolean, default=False)

    # Timestamps
    first_watched_at: datetime = Field(
        sa_type=DateTime(timezone=True), default_factory=datetime.utcnow
    )
    last_watched_at: datetime = Field(
        sa_type=DateTime(timezone=True), default_factory=datetime.utcnow, index=True
    )
    completed_at: Optional[datetime] = Field(
        sa_type=DateTime(timezone=True), default=None
    )

    # Preferences for this content
    preferred_quality: Optional[WatchQuality] = Field(sa_type=String(10), default=None)
    preferred_subtitle_language: Optional[str] = Field(sa_type=String(10), default=None)
    preferred_audio_language: Optional[str] = Field(sa_type=String(10), default=None)

    # Relationships
    user: "User" = Relationship(back_populates="watch_history")
    content: "Content" = Relationship(back_populates="watch_history")

    __table_args__ = (
        UniqueConstraint("user_id", "content_id", name="unique_user_content_history"),
    )


# =============================================================================
# COLLECTIONS AND PLAYLISTS
# =============================================================================


# class Collection(BaseModel, TimestampMixin, table=True):
#     """collections of content"""

#     __tablename__ = "collections"

#     name: str = Field(sa_type=String(255), nullable=False, index=True)
#     slug: str = Field(sa_type=String(300), unique=True, index=True)
#     description: Optional[str] = Field(sa_type=Text, default=None)

#     # Visual Assets
#     cover_image_url: Optional[str] = Field(sa_type=String(500), default=None)
#     backdrop_url: Optional[str] = Field(sa_type=String(500), default=None)
#     logo_url: Optional[str] = Field(sa_type=String(500), default=None)

#     # Collection Properties
#     collection_type: str = Field(
#         sa_type=String(50), default="manual"
#     )  # manual, auto, featured
#     is_featured: bool = Field(sa_type=Boolean, default=False, index=True)
#     is_public: bool = Field(sa_type=Boolean, default=True, index=True)

#     # Ordering and Display
#     sort_order: int = Field(sa_type=Integer, default=0)
#     display_style: Optional[str] = Field(
#         sa_type=String(50), default=None
#     )  # carousel, grid, list

#     # Auto-collection rules (for algorithmic collections)
#     auto_rules: Optional[str] = Field(
#         sa_type=Text, default=None
#     )  # JSON rules for auto-collections

#     # Creator Information
#     created_by_id: Optional[uuid.UUID] = Field(
#         sa_type=UUID(as_uuid=True), foreign_key="users.id", default=None
#     )

#     # Statistics
#     content_count: int = Field(sa_type=Integer, default=0)
#     view_count: int = Field(sa_type=Integer, default=0)


# class CollectionContent(BaseModel, TimestampMixin, table=True):
#     """Content items in collections"""

#     __tablename__ = "collection_contents"

#     collection_id: uuid.UUID = Field(
#         sa_type=UUID(as_uuid=True),
#         foreign_key="collections.id",
#         nullable=False,
#         index=True,
#     )
#     content_id: uuid.UUID = Field(
#         sa_type=UUID(as_uuid=True),
#         foreign_key="contents.id",
#         nullable=False,
#         index=True,
#     )

#     # Ordering and Display
#     sort_order: int = Field(sa_type=Integer, default=0, index=True)
#     added_at: datetime = Field(
#         sa_type=DateTime(timezone=True), default_factory=datetime.utcnow
#     )

#     # Editorial Notes
#     editorial_note: Optional[str] = Field(sa_type=Text, default=None)
#     is_featured_in_collection: bool = Field(sa_type=Boolean, default=False)


#     __table_args__ = (
#         UniqueConstraint(
#             "collection_id", "content_id", name="unique_collection_content"
#         ),
#     )


# =============================================================================
# SEARCH AND RECOMMENDATIONS
# =============================================================================


# class SearchQuery(BaseModel, TimestampMixin, table=True):
#     """Search analytics and improvement"""

#     __tablename__ = "search_queries"

#     query_text: str = Field(sa_type=String(500), nullable=False, index=True)
#     normalized_query: str = Field(sa_type=String(500), nullable=False, index=True)

#     # User Context
#     user_id: Optional[uuid.UUID] = Field(
#         sa_type=UUID(as_uuid=True), foreign_key="users.id", default=None, index=True
#     )
#     session_id: Optional[str] = Field(sa_type=String(255), default=None, index=True)


#     # Applied Filters
#     filters_applied: Optional[str] = Field(sa_type=Text, default=None)  # JSON
#     sort_method: Optional[str] = Field(sa_type=String(50), default=None)

#     # Performance
#     response_time_ms: Optional[int] = Field(sa_type=Integer, default=None)

#     # Context
#     device_type: Optional[DeviceType] = Field(sa_type=String(20), default=None)
#     ip_address: Optional[str] = Field(sa_type=String(45), default=None)

#     # Relationships
#     user: Optional["User"] = Relationship()


# class ContentRecommendation(BaseModel, TimestampMixin, table=True):
#     """AI/ML generated content recommendations"""

#     __tablename__ = "content_recommendations"

#     user_id: uuid.UUID = Field(
#         sa_type=UUID(as_uuid=True), foreign_key="users.id", nullable=False, index=True
#     )
#     content_id: uuid.UUID = Field(
#         sa_type=UUID(as_uuid=True),
#         foreign_key="contents.id",
#         nullable=False,
#         index=True,
#     )

#     # Recommendation Details
#     recommendation_score: float = Field(sa_type=Float, nullable=False)  # 0.0 - 1.0
#     recommendation_type: str = Field(
#         sa_type=String(50), nullable=False, index=True
#     )  # homepage, similar, trending
#     algorithm_version: str = Field(sa_type=String(50), default="v1.0")

#     # Context
#     reason_tags: Optional[str] = Field(
#         sa_type=Text, default=None
#     )  # JSON array of reasons
#     explanation: Optional[str] = Field(sa_type=String(500), default=None)

#     # Positioning
#     position_in_list: Optional[int] = Field(sa_type=Integer, default=None)
#     recommendation_group: Optional[str] = Field(sa_type=String(100), default=None)

#     # Interaction Tracking
#     was_shown: bool = Field(sa_type=Boolean, default=False)
#     shown_at: Optional[datetime] = Field(sa_type=DateTime(timezone=True), default=None)
#     was_clicked: bool = Field(sa_type=Boolean, default=False)
#     clicked_at: Optional[datetime] = Field(
#         sa_type=DateTime(timezone=True), default=None
#     )

#     # Expiry
#     expires_at: Optional[datetime] = Field(
#         sa_type=DateTime(timezone=True), default=None
#     )

#     # Relationships
#     user: "User" = Relationship()
#     content: "Content" = Relationship()

#     __table_args__ = (
#         UniqueConstraint(
#             "user_id",
#             "content_id",
#             "recommendation_type",
#             name="unique_user_content_recommendation",
#         ),
#     )


# =============================================================================
# USER PREFERENCES AND SETTINGS
# =============================================================================


# class UserPreference(BaseModel, TimestampMixin, table=True):
#     """User preferences and settings"""

#     __tablename__ = "user_preferences"

#     user_id: uuid.UUID = Field(
#         sa_type=UUID(as_uuid=True),
#         foreign_key="users.id",
#         nullable=False,
#         primary_key=True,
#     )

#     # Language and Localization
#     preferred_language: str = Field(sa_type=String(10), default="en")
#     preferred_country: Optional[str] = Field(sa_type=String(2), default=None)
#     timezone: Optional[str] = Field(sa_type=String(50), default=None)

#     # Content Preferences
#     preferred_genres: Optional[str] = Field(sa_type=Text, default=None)  # JSON array
#     blocked_genres: Optional[str] = Field(sa_type=Text, default=None)  # JSON array
#     content_rating_limit: Optional[ContentRating] = Field(
#         sa_type=String(10), default=None
#     )

#     # Viewing Preferences
#     default_quality: WatchQuality = Field(sa_type=String(10), default=WatchQuality.AUTO)
#     preferred_subtitle_language: Optional[str] = Field(sa_type=String(10), default=None)
#     preferred_audio_language: str = Field(sa_type=String(10), default="en")
#     autoplay_enabled: bool = Field(sa_type=Boolean, default=True)
#     autoplay_previews: bool = Field(sa_type=Boolean, default=True)
#     skip_intro_enabled: bool = Field(sa_type=Boolean, default=True)
#     skip_credits_enabled: bool = Field(sa_type=Boolean, default=False)

#     # Parental Controls
#     parental_controls_enabled: bool = Field(sa_type=Boolean, default=False)
#     parental_pin: Optional[str] = Field(sa_type=String(255), default=None)  # Hashed PIN
#     restricted_content_types: Optional[str] = Field(
#         sa_type=Text, default=None
#     )  # JSON array

#     # Privacy Settings
#     watch_history_enabled: bool = Field(sa_type=Boolean, default=True)
#     recommendations_enabled: bool = Field(sa_type=Boolean, default=True)
#     data_collection_consent: bool = Field(sa_type=Boolean, default=False)

#     # Notification Preferences
#     email_notifications: bool = Field(sa_type=Boolean, default=True)
#     push_notifications: bool = Field(sa_type=Boolean, default=True)
#     new_episodes_notifications: bool = Field(sa_type=Boolean, default=True)
#     recommendations_notifications: bool = Field(sa_type=Boolean, default=False)
#     marketing_notifications: bool = Field(sa_type=Boolean, default=False)

#     # Accessibility
#     closed_captions_enabled: bool = Field(sa_type=Boolean, default=False)
#     audio_descriptions_enabled: bool = Field(sa_type=Boolean, default=False)
#     high_contrast_mode: bool = Field(sa_type=Boolean, default=False)
#     font_size: str = Field(sa_type=String(20), default="medium")  # small, medium, large

#     # Relationships
#     user: "User" = Relationship()
