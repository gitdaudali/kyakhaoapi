from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

try:
    from .load_fixture_listings import load_fixture as load_rent_listings
    from .load_rent_categories import load_categories as load_rent_categories
except ImportError:  # pragma: no cover - allows direct script execution
    from load_fixture_listings import load_fixture as load_rent_listings
    from load_rent_categories import load_categories as load_rent_categories

LOGGER = logging.getLogger("seed_database")


async def seed_all(fixtures_base: Path, download_images: bool) -> None:
    listings_fixture = fixtures_base / "home" / "listings_lahore.json"
    categories_fixture = fixtures_base / "rent_categories_lahore.json"
    images_dir = fixtures_base / "home" / "images"

    LOGGER.info("Seeding rental listings from %s", listings_fixture)
    await load_rent_listings(
        listings_fixture,
        images_dir,
        download_images,
    )

    LOGGER.info("Seeding rent categories from %s", categories_fixture)
    await load_rent_categories(categories_fixture)

    LOGGER.info("Database seeding complete.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed demo data into the database.")
    parser.add_argument(
        "--fixtures-base",
        type=Path,
        default=Path("fixtures"),
        help="Base directory for fixture files.",
    )
    parser.add_argument(
        "--download-images",
        action="store_true",
        help="Download remote images referenced in listing fixtures.",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    fixtures_base = args.fixtures_base.resolve()
    if not fixtures_base.exists():
        raise SystemExit(f"Fixture directory not found: {fixtures_base}")

    asyncio.run(seed_all(fixtures_base, args.download_images))


if __name__ == "__main__":
    main()

