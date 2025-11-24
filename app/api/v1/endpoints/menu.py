"""Menu API endpoints for browsing menu by categories."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.food import Dish, Restaurant
from app.schemas.dish import DishFilterParams, DishOut
from app.schemas.menu import (
    MenuCategoryOut,
    MenuCategoryWithDishesOut,
    MenuOut,
    MenuStructureOut,
    MenuSummaryOut,
)
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.utils.pagination import paginate

router = APIRouter(prefix="/menu", tags=["Menu"])


def extract_category_from_restaurant_name(restaurant_name: str) -> str:
    """Extract category name from restaurant name (e.g., 'Appetizers Kitchen' -> 'appetizers')."""
    if restaurant_name.lower().endswith(" kitchen"):
        category = restaurant_name[:-8].lower().replace(" ", "_")
        return category
    return restaurant_name.lower().replace(" ", "_")


def format_category_display_name(category_name: str) -> str:
    """Format category name for display (e.g., 'mains_teppanyaki' -> 'Mains Teppanyaki')."""
    return category_name.replace("_", " ").title()


async def get_all_categories_with_counts(session: AsyncSession) -> List[dict]:
    """Get all menu categories with dish counts from restaurants."""
    # Get all restaurants that have dishes
    stmt = (
        select(
            Restaurant.name,
            func.count(Dish.id).label("dish_count"),
            Restaurant.description,
        )
        .join(Dish, Restaurant.id == Dish.restaurant_id)
        .where(Restaurant.is_deleted.is_(False), Dish.is_deleted.is_(False))
        .group_by(Restaurant.id, Restaurant.name, Restaurant.description)
        .order_by(Restaurant.name)
    )

    result = await session.execute(stmt)
    categories_data = []

    for row in result.all():
        category_name = extract_category_from_restaurant_name(row.name)
        categories_data.append(
            {
                "name": category_name,
                "display_name": format_category_display_name(category_name),
                "dish_count": row.dish_count,
                "description": row.description,
                "restaurant_name": row.name,
            }
        )

    return categories_data


async def get_restaurant_by_category(category_name: str, session: AsyncSession) -> Restaurant | None:
    """Get restaurant by category name."""
    # Try different variations of the restaurant name
    possible_names = [
        f"{category_name.replace('_', ' ').title()} Kitchen",
        f"{category_name.title()} Kitchen",
        category_name.replace("_", " ").title(),
    ]

    for name in possible_names:
        result = await session.execute(
            select(Restaurant).where(
                func.lower(Restaurant.name) == name.lower(),
                Restaurant.is_deleted.is_(False),
            )
        )
        restaurant = result.scalar_one_or_none()
        if restaurant:
            return restaurant

    return None


@router.get("/categories", response_model=List[MenuCategoryOut])
async def list_menu_categories(
    session: AsyncSession = Depends(get_db),
) -> List[MenuCategoryOut]:
    """List all menu categories with dish counts."""
    categories_data = await get_all_categories_with_counts(session)

    return [
        MenuCategoryOut(
            name=cat["name"],
            display_name=cat["display_name"],
            dish_count=cat["dish_count"],
            description=cat["description"],
        )
        for cat in categories_data
    ]


@router.get("/categories/{category_name}", response_model=MenuCategoryWithDishesOut)
async def get_category_with_dishes(
    category_name: str,
    params: PaginationParams = Depends(),
    filters: DishFilterParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> MenuCategoryWithDishesOut:
    """Get a specific menu category with its dishes."""
    restaurant = await get_restaurant_by_category(category_name, session)

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu category '{category_name}' not found",
        )

    # Build query for dishes in this category
    stmt = (
        select(Dish)
        .options(selectinload(Dish.moods))
        .where(Dish.restaurant_id == restaurant.id, Dish.is_deleted.is_(False))
    )

    # Apply additional filters
    if filters.cuisine_id:
        stmt = stmt.where(Dish.cuisine_id == filters.cuisine_id)
    if filters.mood_id:
        from app.models.food import Mood

        stmt = stmt.join(Dish.moods).where(Mood.id == filters.mood_id)
    if filters.min_rating is not None:
        stmt = stmt.where(Dish.rating.isnot(None), Dish.rating >= filters.min_rating)
    if filters.max_price is not None:
        stmt = stmt.where(Dish.price.isnot(None), Dish.price <= filters.max_price)
    if filters.is_featured is not None:
        stmt = stmt.where(Dish.is_featured == filters.is_featured)

    # Order by rating then name
    stmt = stmt.order_by(Dish.rating.desc().nullslast(), Dish.name.asc())

    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await session.execute(count_stmt)
    total = total_result.scalar() or 0

    # Apply pagination
    stmt = stmt.limit(params.limit).offset(params.offset)

    result = await session.execute(stmt)
    dishes = result.scalars().all()

    return MenuCategoryWithDishesOut(
        name=category_name,
        display_name=format_category_display_name(category_name),
        dish_count=total,
        description=restaurant.description,
        dishes=[DishOut.model_validate(dish) for dish in dishes],
    )


@router.get("/categories/{category_name}/dishes", response_model=PaginatedResponse[DishOut])
async def get_dishes_by_category(
    category_name: str,
    params: PaginationParams = Depends(),
    filters: DishFilterParams = Depends(),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[DishOut]:
    """Get paginated dishes in a specific menu category."""
    restaurant = await get_restaurant_by_category(category_name, session)

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu category '{category_name}' not found",
        )

    stmt = (
        select(Dish)
        .options(selectinload(Dish.moods))
        .where(Dish.restaurant_id == restaurant.id, Dish.is_deleted.is_(False))
    )

    # Apply filters
    if filters.cuisine_id:
        stmt = stmt.where(Dish.cuisine_id == filters.cuisine_id)
    if filters.mood_id:
        from app.models.food import Mood

        stmt = stmt.join(Dish.moods).where(Mood.id == filters.mood_id)
    if filters.min_rating is not None:
        stmt = stmt.where(Dish.rating.isnot(None), Dish.rating >= filters.min_rating)
    if filters.max_price is not None:
        stmt = stmt.where(Dish.price.isnot(None), Dish.price <= filters.max_price)
    if filters.is_featured is not None:
        stmt = stmt.where(Dish.is_featured == filters.is_featured)

    # Order by rating then name
    stmt = stmt.order_by(Dish.rating.desc().nullslast(), Dish.name.asc())

    return await paginate(session, stmt, params, mapper=lambda d: DishOut.model_validate(d))


@router.get("", response_model=MenuOut)
async def get_complete_menu(
    include_dishes: bool = Query(
        default=True, description="Include dishes in response (set to false for lightweight response)"
    ),
    session: AsyncSession = Depends(get_db),
) -> MenuOut:
    """Get complete menu organized by all categories."""
    categories_data = await get_all_categories_with_counts(session)

    categories_with_dishes = []
    total_dishes = 0

    for cat_data in categories_data:
        restaurant = await get_restaurant_by_category(cat_data["name"], session)
        if not restaurant:
            continue

        dishes = []
        if include_dishes:
            stmt = (
                select(Dish)
                .options(selectinload(Dish.moods))
                .where(Dish.restaurant_id == restaurant.id, Dish.is_deleted.is_(False))
                .order_by(Dish.rating.desc().nullslast(), Dish.name.asc())
            )
            result = await session.execute(stmt)
            dishes = [DishOut.model_validate(dish) for dish in result.scalars().all()]

        categories_with_dishes.append(
            MenuCategoryWithDishesOut(
                name=cat_data["name"],
                display_name=cat_data["display_name"],
                dish_count=cat_data["dish_count"],
                description=cat_data["description"],
                dishes=dishes,
            )
        )
        total_dishes += cat_data["dish_count"]

    return MenuOut(
        categories=categories_with_dishes,
        total_dishes=total_dishes,
        total_categories=len(categories_with_dishes),
    )


@router.get("/summary", response_model=MenuSummaryOut)
async def get_menu_summary(
    session: AsyncSession = Depends(get_db),
) -> MenuSummaryOut:
    """Get menu summary with category overview (lightweight)."""
    categories_data = await get_all_categories_with_counts(session)

    categories = [
        MenuCategoryOut(
            name=cat["name"],
            display_name=cat["display_name"],
            dish_count=cat["dish_count"],
            description=cat["description"],
        )
        for cat in categories_data
    ]

    total_dishes = sum(cat["dish_count"] for cat in categories_data)

    return MenuSummaryOut(
        categories=categories,
        total_dishes=total_dishes,
        total_categories=len(categories),
    )


@router.get("/structure", response_model=MenuStructureOut)
async def get_menu_structure(
    session: AsyncSession = Depends(get_db),
) -> MenuStructureOut:
    """Get menu structure/hierarchy information."""
    categories_data = await get_all_categories_with_counts(session)

    categories = [
        MenuCategoryOut(
            name=cat["name"],
            display_name=cat["display_name"],
            dish_count=cat["dish_count"],
            description=cat["description"],
        )
        for cat in categories_data
    ]

    total_dishes = sum(cat["dish_count"] for cat in categories_data)

    return MenuStructureOut(
        categories=categories,
        total_dishes=total_dishes,
        total_categories=len(categories),
    )

