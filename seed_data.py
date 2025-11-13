from __future__ import annotations

import asyncio
import json
from decimal import Decimal
from pathlib import Path
from typing import Dict, Iterable, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.food import Cuisine, Dish, Mood, Restaurant

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "dishes"


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
        select(Restaurant).where(func.lower(Restaurant.name) == restaurant_name.lower(), Restaurant.is_deleted.is_(False))
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
    if not FIXTURES_DIR.exists():
        print(f"No fixtures directory found at {FIXTURES_DIR}")
        return 0

    total_seeded = 0
    json_files = sorted(FIXTURES_DIR.glob("*.json"))

    if not json_files:
        print(f"No JSON fixtures found in {FIXTURES_DIR}")
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

            cuisine_name = str(entry.get("cuisine", "Uncategorized") )
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
            dish.moods = [mood]
            session.add(dish)
            total_seeded += 1

    if total_seeded:
        await session.commit()
    else:
        await session.rollback()

    return total_seeded


async def main() -> None:
    async with AsyncSessionLocal() as session:
        inserted = await seed_dish_fixtures(session)

    print(f"✅ Seed completed. Inserted {inserted} new dishes from fixtures.")


if __name__ == "__main__":
    asyncio.run(main())
