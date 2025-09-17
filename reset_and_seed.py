#!/usr/bin/env python3
"""
Database Reset and Seed Script for Cup Streaming FastAPI Application

This script will:
1. Drop all existing database tables
2. Run Alembic migrations to recreate tables
3. Seed the database with updated fixture data

Usage:
    python reset_and_seed.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from app.core.config import settings
from seed_database import DatabaseSeeder


async def drop_all_tables():
    """Drop all existing database tables."""
    print("🗑️  Dropping all existing database tables...")

    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False,
    )

    try:
        async with engine.begin() as conn:
            # Get all table names
            result = await conn.execute(text("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename NOT LIKE 'alembic%'
            """))
            tables = [row[0] for row in result.fetchall()]

            if tables:
                print(f"   Found {len(tables)} tables to drop: {', '.join(tables)}")

                # Drop all tables with CASCADE to handle foreign key constraints
                for table in tables:
                    await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                    print(f"   ✅ Dropped table: {table}")
            else:
                print("   ℹ️  No tables found to drop")

        print("✅ All tables dropped successfully!")

    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        raise
    finally:
        await engine.dispose()


async def run_migrations():
    """Run Alembic migrations to recreate tables."""
    print("\n🔄 Running Alembic migrations...")

    import subprocess

    try:
        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )

        print("✅ Migrations completed successfully!")
        if result.stdout:
            print(f"   Output: {result.stdout}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running migrations: {e}")
        print(f"   Error output: {e.stderr}")
        raise
    except FileNotFoundError:
        print("❌ Alembic not found. Make sure it's installed and in your PATH")
        raise


async def seed_database():
    """Seed the database with fixture data."""
    print("\n🌱 Seeding database with updated fixture data...")

    seeder = DatabaseSeeder()
    await seeder.run_seeder()


async def main():
    """Main entry point for the reset and seed process."""
    print("🚀 Starting database reset and seed process...")
    print("=" * 60)

    try:
        # Step 1: Drop all tables
        await drop_all_tables()

        # Step 2: Run migrations
        await run_migrations()

        # Step 3: Seed database
        await seed_database()

        print("\n" + "=" * 60)
        print("🎉 Database reset and seed completed successfully!")
        print("   - All tables dropped")
        print("   - Migrations applied")
        print("   - Database seeded with updated fixture data")

    except Exception as e:
        print(f"\n❌ Process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
