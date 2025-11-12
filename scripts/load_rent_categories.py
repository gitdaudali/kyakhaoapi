from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.rent_category import RentCategory, RentCategoryGroup

logger = logging.getLogger("rent_categories_loader")


async def _upsert_group(session: AsyncSession, city: str, group_data: Dict[str, Any]) -> RentCategoryGroup:
    title = group_data["title"]
    display_order = group_data.get("display_order", 0)

    stmt = select(RentCategoryGroup).where(
        RentCategoryGroup.city == city,
        RentCategoryGroup.title == title,
        RentCategoryGroup.is_deleted == False,  # noqa: E712
    )
    result = await session.execute(stmt)
    group = result.scalar_one_or_none()

    if group:
        group.display_order = display_order
    else:
        group = RentCategoryGroup(
            title=title,
            city=city,
            display_order=display_order,
        )
        session.add(group)
        await session.flush()

    # replace existing categories for this group
    await session.execute(
        delete(RentCategory).where(
            RentCategory.group_id == group.id,
        )
    )

    for category in group_data.get("categories", []):
        item = RentCategory(
            title=category["title"],
            slug=category["slug"],
            url_path=category.get("url_path"),
            display_order=category.get("display_order", 0),
            group_id=group.id,
        )
        session.add(item)

    return group


async def load_categories(path: Path) -> None:
    with path.open("r", encoding="utf-8") as fp:
        payload = json.load(fp)

    city = payload.get("city", "Lahore")
    groups = payload.get("groups", [])

    if not groups:
        logger.warning("No groups found in %s", path)
        return

    async with AsyncSessionLocal() as session:
        for group_data in groups:
            group = await _upsert_group(session, city, group_data)
            logger.info("Loaded group %s for %s", group.title, city)
        await session.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load rent categories fixture.")
    parser.add_argument(
        "fixture_path",
        type=Path,
        help="Path to the rent categories JSON fixture.",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    if not args.fixture_path.exists():
        raise SystemExit(f"Fixture not found: {args.fixture_path}")
    asyncio.run(load_categories(args.fixture_path))


if __name__ == "__main__":
    main()



