"""
Database seeding script from JSON fixtures.
This script reads JSON fixture files and seeds the database with initial data.

Usage:
    python seed_database.py

The script will automatically discover and seed all fixture files in the fixtures/ directory.
"""
from __future__ import annotations

import asyncio
import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_password_hash
from app.core.database import AsyncSessionLocal
from app.models.food import Cuisine, Dish, Mood, Restaurant
from app.models.user import ProfileStatus, User, UserRole

FIXTURES_ROOT = Path(__file__).parent / "fixtures"
DISH_FIXTURES_DIR = FIXTURES_ROOT / "dishes"


def load_json_fixture(file_path: Path) -> Any:
    """Load JSON fixture file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading fixture {file_path}: {str(e)}")
        raise


async def get_or_create_cuisine(session: AsyncSession, name: str) -> Cuisine:
    normalized = name.strip()
    result = await session.execute(
        select(Cuisine).where(func.lower(Cuisine.name) == normalized.lower(), Cuisine.is_deleted.is_(False))
    )
    cuisine = result.scalar_one_or_none()
    if cuisine:
        return cuisine

    cuisine = Cuisine(name=normalized, description=f"Auto-generated cuisine for {normalized}")
    session.add(cuisine)
    await session.flush()
    return cuisine


async def get_or_create_mood(session: AsyncSession, name: str) -> Mood:
    normalized = name.strip()
    result = await session.execute(
        select(Mood).where(func.lower(Mood.name) == normalized.lower(), Mood.is_deleted.is_(False))
    )
    mood = result.scalar_one_or_none()
    if mood:
        return mood

    mood = Mood(name=normalized, description=f"Auto-generated mood for {normalized}")
    session.add(mood)
    await session.flush()
    return mood


async def get_or_create_restaurant(session: AsyncSession, category: str) -> Restaurant:
    restaurant_name = f"{category.title().replace('_', ' ')} Kitchen"
    result = await session.execute(
        select(Restaurant).where(
            func.lower(Restaurant.name) == restaurant_name.lower(),
            Restaurant.is_deleted.is_(False),
        )
    )
    restaurant = result.scalar_one_or_none()
    if restaurant:
        return restaurant

    restaurant = Restaurant(
        name=restaurant_name,
        description=f"Signature dishes from the {category.replace('_', ' ')} collection.",
        city="Virtual",
        country="Global",
        rating=4.5,
    )
    session.add(restaurant)
    await session.flush()
    return restaurant


async def dish_exists(session: AsyncSession, name: str, restaurant_id) -> bool:
    result = await session.execute(
        select(Dish).where(
            func.lower(Dish.name) == name.lower(),
            Dish.restaurant_id == restaurant_id,
            Dish.is_deleted.is_(False),
        )
    )
    return result.scalar_one_or_none() is not None


async def seed_dish_fixtures(session: AsyncSession) -> int:
    if not DISH_FIXTURES_DIR.exists():
        print(f"⚠️  No dishes fixtures directory found at {DISH_FIXTURES_DIR}")
        return 0

    total_seeded = 0
    json_files = sorted(DISH_FIXTURES_DIR.glob("*.json"))

    if not json_files:
        print(f"⚠️  No JSON fixtures found in {DISH_FIXTURES_DIR}")
        return 0

    for json_file in json_files:
        with json_file.open("r", encoding="utf-8") as handle:
            payload: List[Dict[str, object]] = json.load(handle)

        category = json_file.stem
        restaurant = await get_or_create_restaurant(session, category)

        for entry in payload:
            name = str(entry.get("name", "")).strip()
            if not name:
                continue

            if await dish_exists(session, name, restaurant.id):
                continue

            cuisine_name = str(entry.get("cuisine", "Uncategorized"))
            mood_name = str(entry.get("mood", "Anytime"))

            cuisine = await get_or_create_cuisine(session, cuisine_name)
            mood = await get_or_create_mood(session, mood_name)

            price_raw = entry.get("price")
            try:
                price = Decimal(str(price_raw)) if price_raw is not None else None
            except (ValueError, ArithmeticError):
                price = None

            rating_raw = entry.get("rating")
            try:
                rating = float(rating_raw) if rating_raw is not None else None
            except (ValueError, TypeError):
                rating = None

            dish = Dish(
                name=name,
                description=str(entry.get("description", "")).strip(),
                price=price,
                rating=rating,
                is_featured=bool(entry.get("is_featured", False)),
                cuisine_id=cuisine.id,
                restaurant_id=restaurant.id,
            )
            # Ensure relationship list exists before assignment
            dish.moods = [mood]
            session.add(dish)
            total_seeded += 1

    if total_seeded:
        await session.commit()
        print(f"✅ Seeded {total_seeded} dishes from fixtures in {DISH_FIXTURES_DIR}")
    else:
        await session.rollback()

    return total_seeded


async def seed_users(db: AsyncSession, fixture_data: Any) -> int:
    """
    Seed users from fixture data.
    
    Args:
        db: Database session
        fixture_data: Dictionary containing user data (can be single user or list)
    
    Returns:
        Number of users created
    """
    created_count = 0
    
    # Handle both single user object and list of users
    users_data = fixture_data if isinstance(fixture_data, list) else [fixture_data]
    
    for user_data in users_data:
        email = user_data.get("email")
        if not email:
            print("⚠️  Skipping user: missing email")
            continue
        
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == email, User.is_deleted == False)
        )
        existing_user = result.scalar_one_or_none()
        
        # Hash password if provided (used for both create and update)
        password = user_data.get("password", "")
        hashed_password = get_password_hash(password) if password else None

        # Map role string to UserRole enum
        role_str = user_data.get("role", "user").lower()
        role_map = {
            "user": UserRole.USER,
            "admin": UserRole.ADMIN,
            "super_admin": UserRole.SUPER_ADMIN,
        }
        role = role_map.get(role_str, UserRole.USER)

        if existing_user:
            print(f"🔄 Updating existing user '{email}' with fixture settings...")
            existing_user.first_name = user_data.get("first_name", existing_user.first_name)
            existing_user.last_name = user_data.get("last_name", existing_user.last_name)
            existing_user.is_active = user_data.get("is_active", existing_user.is_active)
            existing_user.is_staff = user_data.get("is_staff", existing_user.is_staff)
            existing_user.is_superuser = user_data.get("is_superuser", existing_user.is_superuser)
            existing_user.role = role
            if hashed_password:
                existing_user.password = hashed_password
            created_count += 0
            continue

        # Prepare user data for creation
        user_id = user_data.get("id")
        if user_id:
            try:
                user_id = UUID(user_id)
            except ValueError:
                print(f"⚠️  Invalid UUID '{user_id}' for user '{email}', generating new one...")
                user_id = None

        new_user = User(
            id=user_id,
            email=email,
            password=hashed_password,
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            is_active=user_data.get("is_active", True),
            is_staff=user_data.get("is_staff", False),
            is_superuser=user_data.get("is_superuser", False),
            role=role,
            profile_status=ProfileStatus.ACTIVE,  # Set to ACTIVE so admin can login immediately
        )

        db.add(new_user)
        created_count += 1
        print(f"✅ Created user: {email} (Role: {role.value}, Staff: {new_user.is_staff}, Superuser: {new_user.is_superuser})")
    
    return created_count


async def seed_database():
    """Main function to seed database from fixtures."""
    if not FIXTURES_ROOT.exists():
        print(f"❌ Fixtures directory not found: {FIXTURES_ROOT}")
        return
    
    print("🚀 Starting database seeding...")
    print(f"📁 Fixtures directory: {FIXTURES_ROOT}\n")
    
    # Track seeding statistics
    stats = {
        "users": 0,
        "dishes": 0,
    }
    
    async with AsyncSessionLocal() as db:
        try:
            # Seed users
            users_fixture = FIXTURES_ROOT / "users" / "users.json"
            if users_fixture.exists():
                print("📝 Seeding users...")
                users_data = load_json_fixture(users_fixture)
                created = await seed_users(db, users_data)
                stats["users"] = created
                await db.commit()
                print(f"✅ Users seeding complete: {created} user(s) created\n")
            else:
                print("⚠️  No users fixture found, skipping...\n")
            
            # Seed dishes
            dishes_created = await seed_dish_fixtures(db)
            stats["dishes"] = dishes_created
            
            print("=" * 50)
            print("📊 Seeding Summary:")
            print(f"   Users created: {stats['users']}")
            print(f"   Dishes created: {stats['dishes']}")
            print("=" * 50)
            print("\n✅ Database seeding completed successfully!")
            
        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error during seeding: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


def main():
    """Entry point for the seeding script."""
    try:
        asyncio.run(seed_database())
    except KeyboardInterrupt:
        print("\n⚠️  Seeding interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

