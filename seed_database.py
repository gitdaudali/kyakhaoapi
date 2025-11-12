"""
Database seeding script from JSON fixtures.
This script reads JSON fixture files and seeds the database with initial data.

Usage:
    python seed_database.py

The script will automatically discover and seed all fixture files in the fixtures/ directory.
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_password_hash
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import ProfileStatus, User, UserRole


def load_json_fixture(file_path: Path) -> Dict[str, Any]:
    """Load JSON fixture file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading fixture {file_path}: {str(e)}")
        raise


async def seed_users(db: AsyncSession, fixture_data: Dict[str, Any]) -> int:
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
        
        if existing_user:
            print(f"⏭️  User '{email}' already exists, skipping...")
            continue
        
        # Prepare user data
        user_id = user_data.get("id")
        if user_id:
            try:
                user_id = UUID(user_id)
            except ValueError:
                print(f"⚠️  Invalid UUID '{user_id}' for user '{email}', generating new one...")
                user_id = None
        
        # Hash password
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
        
        # Create user
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
    fixtures_dir = Path(__file__).parent / "fixtures"
    
    if not fixtures_dir.exists():
        print(f"❌ Fixtures directory not found: {fixtures_dir}")
        return
    
    print("🚀 Starting database seeding...")
    print(f"📁 Fixtures directory: {fixtures_dir}\n")
    
    # Track seeding statistics
    stats = {
        "users": 0,
        "other": 0,
    }
    
    async with AsyncSessionLocal() as db:
        try:
            # Seed users
            users_fixture = fixtures_dir / "users" / "users.json"
            if users_fixture.exists():
                print("📝 Seeding users...")
                users_data = load_json_fixture(users_fixture)
                created = await seed_users(db, users_data)
                stats["users"] = created
                await db.commit()
                print(f"✅ Users seeding complete: {created} user(s) created\n")
            else:
                print("⚠️  No users fixture found, skipping...\n")
            
            # Add more fixture types here as needed
            # Example:
            # categories_fixture = fixtures_dir / "categories" / "categories.json"
            # if categories_fixture.exists():
            #     print("📝 Seeding categories...")
            #     categories_data = load_json_fixture(categories_fixture)
            #     await seed_categories(db, categories_data)
            #     await db.commit()
            #     print("✅ Categories seeding complete\n")
            
            print("=" * 50)
            print("📊 Seeding Summary:")
            print(f"   Users created: {stats['users']}")
            print(f"   Other items created: {stats['other']}")
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

