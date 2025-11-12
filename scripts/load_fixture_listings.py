from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import httpx
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.listing import Listing, ListingSection, ListingSectionMap

logger = logging.getLogger("fixture_loader")


async def _download_image(image_url: str, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(image_url)
        response.raise_for_status()
    destination.write_bytes(response.content)
    logger.info("Saved image %s", destination)
    return str(destination)


def _coerce_uuid(value: Optional[str]) -> UUID:
    if not value:
        return uuid4()
    return UUID(value)


async def _apply_sections(
    session: AsyncSession, listing_id: UUID, sections: List[str]
) -> None:
    await session.execute(
        delete(ListingSectionMap).where(ListingSectionMap.listing_id == listing_id)
    )
    for section in sections:
        section_enum = ListingSection(section)
        session.add(
            ListingSectionMap(
                listing_id=listing_id,
                section_name=section_enum,
            )
        )


async def _upsert_listing(
    session: AsyncSession,
    listing_data: Dict[str, Any],
    images_dir: Path,
    download_images: bool,
) -> Listing:
    listing_id = _coerce_uuid(listing_data.get("id"))
    title = listing_data["title"]
    city = listing_data["city"]

    stmt = (
        select(Listing)
        .where(Listing.id == listing_id)
        .union_all(
            select(Listing).where(
                func.lower(Listing.city) == city.lower(),
                Listing.title == title,
            )
        )
    )
    existing = (await session.execute(stmt)).scalars().first()

    image_url = listing_data.get("image_url")
    image_filename = listing_data.get("image_filename")
    if download_images and image_url and image_filename:
        local_path = await _download_image(image_url, images_dir / image_filename)
        image_url = local_path.replace("\\", "/")

    if existing:
        existing.price = listing_data["price"]
        existing.bedrooms = listing_data.get("bedrooms")
        existing.bathrooms = listing_data.get("bathrooms")
        existing.is_pet_friendly = listing_data.get("is_pet_friendly", False)
        existing.image_url = image_url
        listing = existing
    else:
        listing = Listing(
            id=listing_id,
            title=title,
            city=city,
            price=listing_data["price"],
            bedrooms=listing_data.get("bedrooms"),
            bathrooms=listing_data.get("bathrooms"),
            is_pet_friendly=listing_data.get("is_pet_friendly", False),
            image_url=image_url,
        )
        session.add(listing)

    await session.flush()
    await _apply_sections(session, listing.id, listing_data.get("sections", []))
    return listing


async def load_fixture(fixture_path: Path, images_dir: Path, download_images: bool):
    with fixture_path.open("r", encoding="utf-8") as fp:
        payload = json.load(fp)

    listings: List[Dict[str, Any]] = payload.get("listings", [])
    if not listings:
        logger.warning("No listings found in fixture %s", fixture_path)
        return

    async with AsyncSessionLocal() as session:
        for listing_data in listings:
            listing = await _upsert_listing(session, listing_data, images_dir, download_images)
            logger.info("Upserted listing %s (%s)", listing.title, listing.id)
        await session.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load demo listings and section mappings from a JSON fixture."
    )
    parser.add_argument(
        "fixture_path",
        type=Path,
        help="Path to the JSON fixture.",
    )
    parser.add_argument(
        "--images-dir",
        type=Path,
        default=Path("fixtures/home/images"),
        help="Directory for downloaded images.",
    )
    parser.add_argument(
        "--download-images",
        action="store_true",
        help="Download remote images referenced in the fixture.",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    if not args.fixture_path.exists():
        raise SystemExit(f"Fixture not found: {args.fixture_path}")
    asyncio.run(load_fixture(args.fixture_path, args.images_dir, args.download_images))


if __name__ == "__main__":
    main()

