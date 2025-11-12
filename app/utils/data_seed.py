from __future__ import annotations

import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Iterable

from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.food import Cuisine, Dish, Mood, Reservation, Restaurant

fake = Faker()


async def ensure_seed_data(session: AsyncSession, *, cuisines: int = 6, restaurants: int = 10, dishes: int = 50) -> None:
    existing_cuisines = (await session.execute(select(Cuisine))).scalars().first()
    if existing_cuisines:
        return

    cuisine_objs = [
        Cuisine(name=fake.unique.word().title(), description=fake.sentence())
        for _ in range(cuisines)
    ]
    session.add_all(cuisine_objs)
    await session.flush()

    mood_names = ["Comfort", "Spicy", "Healthy", "Quick Bite", "Dessert", "Brunch"]
    mood_objs = [Mood(name=name, description=fake.sentence()) for name in mood_names]
    session.add_all(mood_objs)
    await session.flush()

    restaurant_objs = []
    for _ in range(restaurants):
        restaurant_objs.append(
            Restaurant(
                name=fake.company(),
                description=fake.paragraph(nb_sentences=2),
                address_line=fake.street_address(),
                city=fake.city(),
                state=fake.state(),
                country="USA",
                postal_code=fake.postcode(),
                phone_number=fake.phone_number(),
                latitude=float(fake.latitude()),
                longitude=float(fake.longitude()),
                rating=round(random.uniform(3.0, 5.0), 1),
                price_level=random.randint(1, 5),
            )
        )
    session.add_all(restaurant_objs)
    await session.flush()

    dishes_objs = []
    for _ in range(dishes):
        restaurant = random.choice(restaurant_objs)
        cuisine = random.choice(cuisine_objs)
        dish = Dish(
            name=fake.unique.catch_phrase(),
            description=fake.paragraph(),
            restaurant_id=restaurant.id,
            cuisine_id=cuisine.id,
            price=round(random.uniform(5.0, 40.0), 2),
            rating=round(random.uniform(3.0, 5.0), 1),
            is_featured=random.choice([True, False]),
            featured_week=datetime.now(timezone.utc).date() if random.random() > 0.7 else None,
            calories=random.randint(200, 1200),
            preparation_time_minutes=random.randint(5, 60),
        )
        dish.moods = random.sample(mood_objs, k=random.randint(1, min(3, len(mood_objs))))
        dishes_objs.append(dish)
    session.add_all(dishes_objs)
    await session.flush()

    reservations = []
    for _ in range(20):
        restaurant = random.choice(restaurant_objs)
        reservations.append(
            Reservation(
                restaurant_id=restaurant.id,
                customer_name=fake.name(),
                customer_email=fake.unique.email(),
                reservation_time=datetime.now(timezone.utc) + timedelta(days=random.randint(0, 14)),
                party_size=random.randint(1, 8),
                special_requests=random.choice([None, fake.sentence()]),
            )
        )
    session.add_all(reservations)

    await session.commit()


async def seed_command() -> None:
    async with AsyncSessionLocal() as session:
        await ensure_seed_data(session)


if __name__ == "__main__":
    asyncio.run(seed_command())
