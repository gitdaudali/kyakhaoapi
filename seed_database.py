#!/usr/bin/env python3
"""
Database Seeder for Cup Streaming FastAPI Application

This script loads JSON fixtures and populates the database with sample data
for users, genres, people, content, and all related models with proper relationships.
"""

import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.auth import get_password_hash
from app.core.database import AsyncSessionLocal
from app.models import (
    Content,
    ContentCast,
    ContentCrew,
    ContentGenre,
    ContentReview,
    ContentView,
    Episode,
    EpisodeQuality,
    EpisodeView,
    Genre,
    MovieFile,
    Person,
    Season,
    StreamingChannel,
    User,
    UserContentInteraction,
    UserWatchHistory,
    WatchSession,
)


class DatabaseSeeder:
    def __init__(self):
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        self.session: AsyncSession = None

    async def load_json_fixture(self, file_path: str) -> List[Dict[str, Any]]:
        """Load JSON fixture file and return parsed data."""
        full_path = self.fixtures_dir / file_path
        if not full_path.exists():
            print(f"⚠️  Fixture file not found: {full_path}")
            return []

        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} records from {file_path}")
        return data

    async def seed_users(self) -> Dict[str, str]:
        """Seed users and return mapping of email to user ID."""
        users_data = await self.load_json_fixture("users/users.json")
        user_mapping = {}

        for user_data in users_data:
            # Hash the password
            user_data["password"] = get_password_hash(user_data["password"])

            # Create user instance
            user = User(**user_data)
            self.session.add(user)
            user_mapping[user_data["email"]] = user_data["id"]

        await self.session.commit()
        print(f"✅ Seeded {len(users_data)} users")
        return user_mapping

    async def seed_genres(self) -> Dict[str, str]:
        """Seed genres and return mapping of slug to genre ID."""
        genres_data = await self.load_json_fixture("genres/genres.json")
        genre_mapping = {}

        for genre_data in genres_data:
            # Handle parent genre reference
            if genre_data.get("parent_genre_id"):
                parent_slug = next(
                    (
                        g["slug"]
                        for g in genres_data
                        if g["id"] == genre_data["parent_genre_id"]
                    ),
                    None,
                )
                if parent_slug and parent_slug in genre_mapping:
                    genre_data["parent_genre_id"] = genre_mapping[parent_slug]
                else:
                    genre_data["parent_genre_id"] = None

            genre = Genre(**genre_data)
            self.session.add(genre)
            genre_mapping[genre_data["slug"]] = genre_data["id"]

        await self.session.commit()
        print(f"✅ Seeded {len(genres_data)} genres")
        return genre_mapping

    async def seed_people(self) -> Dict[str, str]:
        """Seed people and return mapping of slug to person ID."""
        people_data = await self.load_json_fixture("people/people.json")
        person_mapping = {}

        for person_data in people_data:
            # Convert string dates to date objects
            if person_data.get("birth_date"):
                person_data["birth_date"] = datetime.strptime(
                    person_data["birth_date"], "%Y-%m-%d"
                ).date()
            if person_data.get("death_date"):
                person_data["death_date"] = datetime.strptime(
                    person_data["death_date"], "%Y-%m-%d"
                ).date()

            person = Person(**person_data)
            self.session.add(person)
            person_mapping[person_data["slug"]] = person_data["id"]

        await self.session.commit()
        print(f"✅ Seeded {len(people_data)} people")
        return person_mapping

    async def seed_content(self) -> Dict[str, str]:
        """Seed content and return mapping of slug to content ID."""
        content_data = await self.load_json_fixture("content/content.json")
        content_mapping = {}

        for content_item in content_data:
            # Convert string dates to date objects
            if content_item.get("release_date"):
                content_item["release_date"] = datetime.strptime(
                    content_item["release_date"], "%Y-%m-%d"
                ).date()
            if content_item.get("premiere_date"):
                content_item["premiere_date"] = datetime.strptime(
                    content_item["premiere_date"], "%Y-%m-%d"
                ).date()
            if content_item.get("end_date"):
                content_item["end_date"] = datetime.strptime(
                    content_item["end_date"], "%Y-%m-%d"
                ).date()
            if content_item.get("next_episode_date"):
                content_item["next_episode_date"] = datetime.strptime(
                    content_item["next_episode_date"], "%Y-%m-%d"
                ).date()

            # Convert datetime strings to datetime objects
            if content_item.get("available_from"):
                content_item["available_from"] = datetime.fromisoformat(
                    content_item["available_from"].replace("Z", "+00:00")
                )
            if content_item.get("available_until"):
                content_item["available_until"] = datetime.fromisoformat(
                    content_item["available_until"].replace("Z", "+00:00")
                )

            content = Content(**content_item)
            self.session.add(content)
            content_mapping[content_item["slug"]] = content_item["id"]

        await self.session.commit()
        print(f"✅ Seeded {len(content_data)} content items")
        return content_mapping

    async def seed_content_genres(
        self, content_mapping: Dict[str, str], genre_mapping: Dict[str, str]
    ):
        """Seed content-genre relationships."""
        content_genres_data = await self.load_json_fixture(
            "content/content_genres.json"
        )

        for cg_data in content_genres_data:
            # Map content and genre IDs
            content_slug = next(
                (
                    slug
                    for slug, cid in content_mapping.items()
                    if cid == cg_data["content_id"]
                ),
                None,
            )
            genre_slug = next(
                (
                    slug
                    for slug, gid in genre_mapping.items()
                    if gid == cg_data["genre_id"]
                ),
                None,
            )

            if content_slug and genre_slug:
                cg_data["content_id"] = content_mapping[content_slug]
                cg_data["genre_id"] = genre_mapping[genre_slug]
                content_genre = ContentGenre(**cg_data)
                self.session.add(content_genre)

        await self.session.commit()
        print(f"✅ Seeded {len(content_genres_data)} content-genre relationships")

    async def seed_content_cast(
        self, content_mapping: Dict[str, str], person_mapping: Dict[str, str]
    ):
        """Seed content cast relationships."""
        cast_data = await self.load_json_fixture("content/content_cast.json")

        for cast_item in cast_data:
            # Map content and person IDs
            content_slug = next(
                (
                    slug
                    for slug, cid in content_mapping.items()
                    if cid == cast_item["content_id"]
                ),
                None,
            )
            person_slug = next(
                (
                    slug
                    for slug, pid in person_mapping.items()
                    if pid == cast_item["person_id"]
                ),
                None,
            )

            if content_slug and person_slug:
                cast_item["content_id"] = content_mapping[content_slug]
                cast_item["person_id"] = person_mapping[person_slug]
                cast = ContentCast(**cast_item)
                self.session.add(cast)

        await self.session.commit()
        print(f"✅ Seeded {len(cast_data)} cast relationships")

    async def seed_content_crew(
        self, content_mapping: Dict[str, str], person_mapping: Dict[str, str]
    ):
        """Seed content crew relationships."""
        crew_data = await self.load_json_fixture("content/content_crew.json")

        for crew_item in crew_data:
            # Map content and person IDs
            content_slug = next(
                (
                    slug
                    for slug, cid in content_mapping.items()
                    if cid == crew_item["content_id"]
                ),
                None,
            )
            person_slug = next(
                (
                    slug
                    for slug, pid in person_mapping.items()
                    if pid == crew_item["person_id"]
                ),
                None,
            )

            if content_slug and person_slug:
                crew_item["content_id"] = content_mapping[content_slug]
                crew_item["person_id"] = person_mapping[person_slug]
                crew = ContentCrew(**crew_item)
                self.session.add(crew)

        await self.session.commit()
        print(f"✅ Seeded {len(crew_data)} crew relationships")

    async def seed_movie_files(self, content_mapping: Dict[str, str]):
        """Seed movie files for movie content."""
        movie_files_data = await self.load_json_fixture("content/movie_files.json")

        for movie_file_data in movie_files_data:
            # Map content ID
            content_slug = next(
                (
                    slug
                    for slug, cid in content_mapping.items()
                    if cid == movie_file_data["content_id"]
                ),
                None,
            )

            if content_slug:
                movie_file_data["content_id"] = content_mapping[content_slug]
                movie_file = MovieFile(**movie_file_data)
                self.session.add(movie_file)

        await self.session.commit()
        print(f"✅ Seeded {len(movie_files_data)} movie files")

    async def seed_seasons(self, content_mapping: Dict[str, str]) -> Dict[str, str]:
        """Seed seasons and return mapping of season ID to content ID."""
        seasons_data = await self.load_json_fixture("episodes/seasons.json")
        season_mapping = {}

        for season_data in seasons_data:
            # Map content ID
            content_slug = next(
                (
                    slug
                    for slug, cid in content_mapping.items()
                    if cid == season_data["content_id"]
                ),
                None,
            )

            if content_slug:
                season_data["content_id"] = content_mapping[content_slug]

                # Convert string dates to date objects
                if season_data.get("air_date"):
                    season_data["air_date"] = datetime.strptime(
                        season_data["air_date"], "%Y-%m-%d"
                    ).date()
                if season_data.get("end_date"):
                    season_data["end_date"] = datetime.strptime(
                        season_data["end_date"], "%Y-%m-%d"
                    ).date()

                season = Season(**season_data)
                self.session.add(season)
                season_mapping[season_data["id"]] = season_data["content_id"]

        await self.session.commit()
        print(f"✅ Seeded {len(seasons_data)} seasons")
        return season_mapping

    async def seed_episodes(
        self, content_mapping: Dict[str, str], season_mapping: Dict[str, str]
    ):
        """Seed episodes."""
        episodes_data = await self.load_json_fixture("episodes/episodes.json")

        for episode_data in episodes_data:
            # Map content and season IDs
            content_slug = next(
                (
                    slug
                    for slug, cid in content_mapping.items()
                    if cid == episode_data["content_id"]
                ),
                None,
            )

            if content_slug:
                episode_data["content_id"] = content_mapping[content_slug]

                # Map season ID if it exists
                if (
                    episode_data.get("season_id")
                    and episode_data["season_id"] in season_mapping
                ):
                    episode_data["season_id"] = episode_data[
                        "season_id"
                    ]  # Keep original season ID

                # Convert string dates to date objects
                if episode_data.get("air_date"):
                    episode_data["air_date"] = datetime.strptime(
                        episode_data["air_date"], "%Y-%m-%d"
                    ).date()

                # Convert datetime strings to datetime objects
                if episode_data.get("available_from"):
                    episode_data["available_from"] = datetime.fromisoformat(
                        episode_data["available_from"].replace("Z", "+00:00")
                    )
                if episode_data.get("available_until"):
                    episode_data["available_until"] = datetime.fromisoformat(
                        episode_data["available_until"].replace("Z", "+00:00")
                    )

                episode = Episode(**episode_data)
                self.session.add(episode)

        await self.session.commit()
        print(f"✅ Seeded {len(episodes_data)} episodes")

    async def seed_episode_qualities(self):
        """Seed episode qualities."""
        episode_qualities_data = await self.load_json_fixture(
            "episodes/episode_qualities.json"
        )

        for quality_data in episode_qualities_data:
            episode_quality = EpisodeQuality(**quality_data)
            self.session.add(episode_quality)

        await self.session.commit()
        print(f"✅ Seeded {len(episode_qualities_data)} episode qualities")

    async def seed_streaming_channels(self):
        """Seed streaming channels."""
        streaming_channels_data = await self.load_json_fixture("streaming/streaming_channels.json")

        for channel_data in streaming_channels_data:
            # Convert category string to enum if it exists
            if channel_data.get("category"):
                from app.models.streaming import StreamingChannelCategory
                try:
                    channel_data["category"] = StreamingChannelCategory(channel_data["category"])
                except ValueError:
                    # If category is not a valid enum value, set to None
                    channel_data["category"] = None

            streaming_channel = StreamingChannel(**channel_data)
            self.session.add(streaming_channel)

        await self.session.commit()
        print(f"✅ Seeded {len(streaming_channels_data)} streaming channels")

    async def seed_user_interactions(
        self, user_mapping: Dict[str, str], content_mapping: Dict[str, str]
    ):
        """Seed user content interactions."""
        interactions_data = await self.load_json_fixture(
            "interactions/user_interactions.json"
        )

        for interaction_data in interactions_data:
            # Map user and content IDs
            user_email = next(
                (
                    email
                    for email, uid in user_mapping.items()
                    if uid == interaction_data["user_id"]
                ),
                None,
            )
            content_slug = next(
                (
                    slug
                    for slug, cid in content_mapping.items()
                    if cid == interaction_data["content_id"]
                ),
                None,
            )

            if user_email and content_slug:
                interaction_data["user_id"] = user_mapping[user_email]
                interaction_data["content_id"] = content_mapping[content_slug]
                interaction = UserContentInteraction(**interaction_data)
                self.session.add(interaction)

        await self.session.commit()
        print(f"✅ Seeded {len(interactions_data)} user interactions")

    async def seed_content_reviews(
        self, user_mapping: Dict[str, str], content_mapping: Dict[str, str]
    ):
        """Seed content reviews."""
        reviews_data = await self.load_json_fixture("interactions/content_reviews.json")

        for review_data in reviews_data:
            # Map user and content IDs
            user_email = next(
                (
                    email
                    for email, uid in user_mapping.items()
                    if uid == review_data["user_id"]
                ),
                None,
            )
            content_slug = next(
                (
                    slug
                    for slug, cid in content_mapping.items()
                    if cid == review_data["content_id"]
                ),
                None,
            )

            if user_email and content_slug:
                review_data["user_id"] = user_mapping[user_email]
                review_data["content_id"] = content_mapping[content_slug]
                review = ContentReview(**review_data)
                self.session.add(review)

        await self.session.commit()
        print(f"✅ Seeded {len(reviews_data)} content reviews")

    async def seed_sample_views_and_sessions(
        self, user_mapping: Dict[str, str], content_mapping: Dict[str, str]
    ):
        """Seed sample content views and watch sessions."""
        # Sample content views
        content_views = []
        for i, (content_slug, content_id) in enumerate(
            list(content_mapping.items())[:3]
        ):
            for j, (user_email, user_id) in enumerate(list(user_mapping.items())[:2]):
                content_views.append(
                    {
                        "content_id": content_id,
                        "viewer_id": user_id,
                    }
                )

        for view_data in content_views:
            view = ContentView(**view_data)
            self.session.add(view)

        # Sample watch sessions
        watch_sessions = []
        for i, (user_email, user_id) in enumerate(list(user_mapping.items())[:2]):
            for j, (content_slug, content_id) in enumerate(
                list(content_mapping.items())[:2]
            ):
                watch_sessions.append(
                    {
                        "user_id": user_id,
                        "content_id": content_id,
                        "session_id": f"session_{user_id}_{content_id}_{i}_{j}",
                        "device_type": "desktop",
                        "quality_setting": "1080p",
                    }
                )

        for session_data in watch_sessions:
            session = WatchSession(**session_data)
            self.session.add(session)

        # Sample watch history
        watch_history = []
        for i, (user_email, user_id) in enumerate(list(user_mapping.items())[:2]):
            for j, (content_slug, content_id) in enumerate(
                list(content_mapping.items())[:2]
            ):
                watch_history.append(
                    {
                        "user_id": user_id,
                        "content_id": content_id,
                        "current_position_seconds": 1200 + (i * 300),
                        "total_episodes_watched": 1 + j,
                        "is_completed": j == 0,
                        "is_currently_watching": j == 1,
                        "first_watched_at": datetime.now(timezone.utc),
                        "last_watched_at": datetime.now(timezone.utc),
                        "preferred_quality": "1080p",
                        "preferred_subtitle_language": "en",
                        "preferred_audio_language": "en",
                    }
                )

        for history_data in watch_history:
            history = UserWatchHistory(**history_data)
            self.session.add(history)

        await self.session.commit()
        print(
            f"✅ Seeded {len(content_views)} content views, {len(watch_sessions)} watch sessions, {len(watch_history)} watch history records"
        )

    async def run_seeder(self):
        """Run the complete database seeding process."""
        print("🌱 Starting database seeding process...")

        # Create tables first
        from sqlmodel import SQLModel

        from app.core.database import engine

        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        print("✅ Database tables created")

        self.session = AsyncSessionLocal()

        try:
            # Seed core data
            print("\n📊 Seeding core data...")
            user_mapping = await self.seed_users()
            genre_mapping = await self.seed_genres()
            person_mapping = await self.seed_people()
            content_mapping = await self.seed_content()

            # Seed relationships
            print("\n🔗 Seeding relationships...")
            await self.seed_content_genres(content_mapping, genre_mapping)
            await self.seed_content_cast(content_mapping, person_mapping)
            await self.seed_content_crew(content_mapping, person_mapping)
            await self.seed_movie_files(content_mapping)

            # Seed episodes and seasons
            print("\n📺 Seeding episodes and seasons...")
            season_mapping = await self.seed_seasons(content_mapping)
            await self.seed_episodes(content_mapping, season_mapping)
            await self.seed_episode_qualities()

            # Seed streaming channels
            print("\n📡 Seeding streaming channels...")
            await self.seed_streaming_channels()

            # Seed user interactions
            print("\n👤 Seeding user interactions...")
            await self.seed_user_interactions(user_mapping, content_mapping)
            await self.seed_content_reviews(user_mapping, content_mapping)

            # Seed sample analytics data
            print("\n📈 Seeding analytics data...")
            await self.seed_sample_views_and_sessions(user_mapping, content_mapping)

            print("\n🎉 Database seeding completed successfully!")
            print(f"   - Users: {len(user_mapping)}")
            print(f"   - Genres: {len(genre_mapping)}")
            print(f"   - People: {len(person_mapping)}")
            print(f"   - Content: {len(content_mapping)}")
            print(f"   - Seasons: {len(season_mapping)}")

        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            await self.session.rollback()
            raise
        finally:
            await self.session.close()


async def main():
    """Main entry point for the seeder."""
    seeder = DatabaseSeeder()
    await seeder.run_seeder()


if __name__ == "__main__":
    asyncio.run(main())
