from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.listing import Listing, ListingSection, ListingSectionMap
from app.models.rent_category import RentCategoryGroup
from app.models.listing_inquiry import ListingInquiry
from app.schemas.listing import HomeResponse, HomeSectionResponse, ListingCard
from app.schemas.rent_category import RentCategoriesResponse, RentCategoryGroupResponse, RentCategoryItem
from app.schemas.rent_home import RentInquiryRequest, RentInquiryResponse

router = APIRouter()


SECTION_META: Dict[ListingSection, str] = {
    ListingSection.POPULAR: "Popular in {city}",
    ListingSection.DEALS: "Best Deals",
    ListingSection.PETS: "Pet Friendly Rentals",
}


async def _get_listings_for_section(
    db: AsyncSession, city_lower: str, section: ListingSection
) -> List[ListingCard]:
    stmt = (
        select(Listing)
        .join(ListingSectionMap, ListingSectionMap.listing_id == Listing.id)
        .where(func.lower(Listing.city) == city_lower)
        .where(ListingSectionMap.section_name == section)
        .order_by(Listing.created_at.desc())
    )
    result = await db.execute(stmt)
    listings = result.scalars().all()

    return [
        ListingCard(
            id=listing.id,
            title=listing.title,
            price=listing.price,
            bedrooms=listing.bedrooms,
            bathrooms=listing.bathrooms,
            image_url=listing.image_url,
            city=listing.city,
        )
        for listing in listings
    ]


@router.get(
    "/rent-home",
    response_model=HomeResponse,
    summary="Get rental home screen sections",
    tags=["rent-home"],
)
async def get_rent_home_sections(
    city: str = Query(..., min_length=1, description="City to filter rental listings by"),
    db: AsyncSession = Depends(get_db),
) -> HomeResponse:
    sections: List[HomeSectionResponse] = []
    normalized_city = city.strip()
    if not normalized_city:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="City must be a non-empty string",
        )
    normalized_city_lower = normalized_city.lower()
    display_city = normalized_city.title()

    for section in ListingSection:
        section_listings = await _get_listings_for_section(
            db, normalized_city_lower, section
        )
        section_title_template = SECTION_META[section]
        section_title = (
            section_title_template.format(city=display_city)
            if "{city}" in section_title_template
            else section_title_template
        )
        sections.append(
            HomeSectionResponse(
                section_title=section_title,
                section_key=section.value,
                listings=section_listings,
            )
        )

    return HomeResponse(city=display_city, sections=sections)


@router.get(
    "/rent-home/categories",
    response_model=RentCategoriesResponse,
    summary="Get rental category menus for the given city",
    tags=["rent-home"],
)
async def get_rent_home_categories(
    city: str = Query("Lahore", min_length=1, description="City to filter rental categories by"),
    db: AsyncSession = Depends(get_db),
) -> RentCategoriesResponse:
    normalized_city = city.strip()
    if not normalized_city:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="City must be a non-empty string",
        )
    normalized_city_lower = normalized_city.lower()
    display_city = normalized_city.title()

    stmt = (
        select(RentCategoryGroup)
        .where(func.lower(RentCategoryGroup.city) == normalized_city_lower)
        .order_by(RentCategoryGroup.display_order.asc(), RentCategoryGroup.title.asc())
    )
    result = await db.execute(stmt)
    groups = result.scalars().unique().all()

    group_responses: List[RentCategoryGroupResponse] = []
    for group in groups:
        sorted_items = sorted(
            group.categories,
            key=lambda c: (c.display_order, c.title.lower()),
        )
        group_responses.append(
            RentCategoryGroupResponse(
                group_title=group.title,
                display_order=group.display_order,
                items=[
                    RentCategoryItem(
                        title=item.title,
                        slug=item.slug,
                        url_path=item.url_path,
                        display_order=item.display_order,
                    )
                    for item in sorted_items
                ],
            )
        )

    return RentCategoriesResponse(city=display_city, groups=group_responses)


@router.post(
    "/rent-home/message",
    response_model=RentInquiryResponse,
    summary="Send a message about a rental listing",
    status_code=status.HTTP_201_CREATED,
)
async def send_rent_home_message(
    payload: RentInquiryRequest,
    db: AsyncSession = Depends(get_db),
) -> RentInquiryResponse:
    listing_exists = await db.scalar(
        select(Listing.id).where(Listing.id == payload.listing_id)
    )
    if not listing_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )

    inquiry = ListingInquiry(
        listing_id=payload.listing_id,
        message=payload.message,
        preferred_move_in_date=(
            payload.preferred_move_in_date.isoformat()
            if payload.preferred_move_in_date
            else None
        ),
        contact_name=payload.contact_name,
    )
    db.add(inquiry)
    await db.commit()
    await db.refresh(inquiry)

    return RentInquiryResponse(
        inquiry_id=inquiry.id,
        listing_id=inquiry.listing_id,
        message=inquiry.message,
        preferred_move_in_date=payload.preferred_move_in_date,
        contact_name=inquiry.contact_name,
    )

