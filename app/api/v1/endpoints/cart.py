"""Cart API endpoints for managing user shopping carts."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.core.response_handler import success_response
from app.models.cart import Cart, CartItem
from app.models.food import Dish
from app.models.user import User  # Import User to ensure SQLModel.metadata is populated
from app.schemas.cart import CartItemCreate, CartItemOut, CartItemUpdate, CartOut

router = APIRouter(prefix="/cart", tags=["Cart"])


async def get_or_create_cart(user_id: UUID, session: AsyncSession) -> Cart:
    """Get existing cart or create a new one for the user."""
    result = await session.execute(
        select(Cart).where(Cart.user_id == user_id, Cart.is_deleted.is_(False))
    )
    cart = result.scalar_one_or_none()

    if not cart:
        cart = Cart(user_id=user_id, total_amount=0.0, item_count=0)
        session.add(cart)
        await session.flush()

    return cart


async def get_cart_item_or_404(
    cart_id: UUID, item_id: UUID, session: AsyncSession
) -> CartItem:
    """Get cart item or raise 404."""
    result = await session.execute(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart_id,
            CartItem.is_deleted.is_(False),
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found"
        )
    return item


async def calculate_cart_totals(cart_id: UUID, session: AsyncSession) -> tuple[float, int]:
    """Calculate total amount and item count for cart by querying items directly."""
    # Query items directly to avoid lazy loading issues
    items_result = await session.execute(
        select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.is_deleted.is_(False)
        )
    )
    items = items_result.scalars().all()
    
    total = sum(float(item.subtotal) for item in items)
    count = sum(item.quantity for item in items)
    return total, count


async def update_cart_totals(cart: Cart, session: AsyncSession) -> None:
    """Update cart totals based on items."""
    total, count = await calculate_cart_totals(cart.id, session)
    cart.total_amount = total
    cart.item_count = count


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    item_data: CartItemCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Add an item to the user's cart."""
    # Use current_user.id directly (no need for user_id in URL)
    user_id = current_user.id

    # Verify dish exists
    dish_result = await session.execute(
        select(Dish).where(Dish.id == item_data.dish_id, Dish.is_deleted.is_(False))
    )
    dish = dish_result.scalar_one_or_none()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found"
        )

    if dish.price is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dish does not have a price",
        )

    # Get or create cart
    cart = await get_or_create_cart(user_id, session)

    # Check if item already exists in cart
    existing_item_result = await session.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.dish_id == item_data.dish_id,
            CartItem.is_deleted.is_(False),
        )
    )
    existing_item = existing_item_result.scalar_one_or_none()

    if existing_item:
        # Update quantity and subtotal
        existing_item.quantity += item_data.quantity
        existing_item.subtotal = float(existing_item.unit_price) * existing_item.quantity
        if item_data.special_instructions:
            existing_item.special_instructions = item_data.special_instructions
        await session.flush()
        await update_cart_totals(cart, session)
        await session.commit()
        
        # Reload cart item with dish and moods eagerly loaded
        item_result = await session.execute(
            select(CartItem)
            .options(selectinload(CartItem.dish).selectinload(Dish.moods))
            .where(CartItem.id == existing_item.id)
        )
        updated_item = item_result.scalar_one()
        cart_item_out = CartItemOut.model_validate(updated_item)
        return success_response(
            message="Cart item updated successfully",
            data=cart_item_out.model_dump(),
            status_code=status.HTTP_200_OK,
            use_body=True
        )

    # Create new cart item
    unit_price = float(dish.price)
    subtotal = unit_price * item_data.quantity

    cart_item = CartItem(
        cart_id=cart.id,
        dish_id=item_data.dish_id,
        quantity=item_data.quantity,
        unit_price=unit_price,
        subtotal=subtotal,
        special_instructions=item_data.special_instructions,
    )

    session.add(cart_item)
    await session.flush()
    await update_cart_totals(cart, session)
    await session.commit()
    
    # Reload cart item with dish and moods eagerly loaded
    item_result = await session.execute(
        select(CartItem)
        .options(selectinload(CartItem.dish).selectinload(Dish.moods))
        .where(CartItem.id == cart_item.id)
    )
    loaded_item = item_result.scalar_one()
    cart_item_out = CartItemOut.model_validate(loaded_item)
    return success_response(
        message="Item added to cart successfully",
        data=cart_item_out.model_dump(),
        status_code=status.HTTP_201_CREATED,
        use_body=True
    )


@router.get("")
async def get_cart(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Get the user's cart with all items."""
    # Use current_user.id directly
    user_id = current_user.id

    # Get cart with items, dishes, and moods eagerly loaded
    result = await session.execute(
        select(Cart)
        .options(
            selectinload(Cart.items)
            .selectinload(CartItem.dish)
            .selectinload(Dish.moods)
        )
        .where(Cart.user_id == user_id, Cart.is_deleted.is_(False))
    )
    cart = result.scalar_one_or_none()

    if not cart:
        # Return empty cart
        cart = Cart(user_id=user_id, total_amount=0.0, item_count=0, items=[])
        cart_out = CartOut.model_validate(cart)
        return success_response(
            message="Cart retrieved successfully",
            data=cart_out.model_dump(),
            use_body=True
        )

    # Filter out deleted items
    active_items = [item for item in cart.items if not item.is_deleted]
    cart.items = active_items

    # Update totals
    await update_cart_totals(cart, session)
    await session.commit()

    cart_out = CartOut.model_validate(cart)
    return success_response(
        message="Cart retrieved successfully",
        data=cart_out.model_dump(),
        use_body=True
    )


@router.put("/items/{item_id}")
async def update_cart_item(
    item_id: UUID,
    item_data: CartItemUpdate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Update a cart item (quantity or instructions)."""
    # Use current_user.id directly
    user_id = current_user.id

    # Get cart
    cart_result = await session.execute(
        select(Cart).where(Cart.user_id == user_id, Cart.is_deleted.is_(False))
    )
    cart = cart_result.scalar_one_or_none()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found"
        )

    # Get cart item
    item = await get_cart_item_or_404(cart.id, item_id, session)

    # Update item
    item.quantity = item_data.quantity
    item.subtotal = float(item.unit_price) * item_data.quantity
    if item_data.special_instructions is not None:
        item.special_instructions = item_data.special_instructions

    await update_cart_totals(cart, session)
    await session.commit()
    
    # Reload cart item with dish and moods eagerly loaded
    item_result = await session.execute(
        select(CartItem)
        .options(selectinload(CartItem.dish).selectinload(Dish.moods))
        .where(CartItem.id == item.id)
    )
    updated_item = item_result.scalar_one()
    cart_item_out = CartItemOut.model_validate(updated_item)
    return success_response(
        message="Cart item updated successfully",
        data=cart_item_out.model_dump(),
        use_body=True
    )


@router.delete("/items/{item_id}")
async def remove_cart_item(
    item_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Remove an item from the cart."""
    # Use current_user.id directly
    user_id = current_user.id

    # Get cart
    cart_result = await session.execute(
        select(Cart).where(Cart.user_id == user_id, Cart.is_deleted.is_(False))
    )
    cart = cart_result.scalar_one_or_none()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found"
        )

    # Get and soft delete cart item
    item = await get_cart_item_or_404(cart.id, item_id, session)
    item.is_deleted = True

    await update_cart_totals(cart, session)
    await session.commit()
    return success_response(
        message="Cart item removed successfully",
        data={"item_id": str(item_id)},
        use_body=True
    )


@router.delete("")
async def clear_cart(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Clear all items from the cart."""
    # Use current_user.id directly
    user_id = current_user.id

    # Get cart with items
    result = await session.execute(
        select(Cart)
        .options(selectinload(Cart.items))
        .where(Cart.user_id == user_id, Cart.is_deleted.is_(False))
    )
    cart = result.scalar_one_or_none()
    if not cart:
        return success_response(
            message="Cart is already empty",
            data={"cart_id": None},
            use_body=True
        )

    # Soft delete all items
    for item in cart.items:
        item.is_deleted = True

    await update_cart_totals(cart, session)
    await session.commit()
    return success_response(
        message="Cart cleared successfully",
        data={"cart_id": str(cart.id)},
        use_body=True
    )

