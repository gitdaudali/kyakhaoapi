"""Cart API endpoints for managing user shopping carts."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.models.cart import Cart, CartItem
from app.models.food import Dish
from app.schemas.cart import CartItemCreate, CartItemOut, CartItemUpdate, CartOut

router = APIRouter(prefix="/users/{user_id}/cart", tags=["Cart"])


async def get_or_create_cart(user_id: uuid.UUID, session: AsyncSession) -> Cart:
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
    cart_id: uuid.UUID, item_id: uuid.UUID, session: AsyncSession
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


def calculate_cart_totals(cart: Cart) -> tuple[float, int]:
    """Calculate total amount and item count for cart."""
    total = sum(item.subtotal for item in cart.items if not item.is_deleted)
    count = sum(item.quantity for item in cart.items if not item.is_deleted)
    return float(total), count


async def update_cart_totals(cart: Cart, session: AsyncSession) -> None:
    """Update cart totals based on items."""
    total, count = calculate_cart_totals(cart)
    cart.total_amount = total
    cart.item_count = count


@router.post("/items", response_model=CartItemOut, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    user_id: uuid.UUID,
    item_data: CartItemCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> CartItemOut:
    """Add an item to the user's cart."""
    # Verify user authorization
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage your own cart",
        )

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
        await session.refresh(existing_item)
        await session.refresh(existing_item.dish)
        return CartItemOut.model_validate(existing_item)

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
    await session.refresh(cart_item)
    await session.refresh(cart_item.dish)

    return CartItemOut.model_validate(cart_item)


@router.get("", response_model=CartOut)
async def get_cart(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> CartOut:
    """Get the user's cart with all items."""
    # Verify user authorization
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own cart",
        )

    # Get cart with items
    result = await session.execute(
        select(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.dish))
        .where(Cart.user_id == user_id, Cart.is_deleted.is_(False))
    )
    cart = result.scalar_one_or_none()

    if not cart:
        # Return empty cart
        cart = Cart(user_id=user_id, total_amount=0.0, item_count=0, items=[])
        return CartOut.model_validate(cart)

    # Filter out deleted items
    active_items = [item for item in cart.items if not item.is_deleted]
    cart.items = active_items

    # Update totals
    await update_cart_totals(cart, session)
    await session.commit()
    await session.refresh(cart)

    return CartOut.model_validate(cart)


@router.put("/items/{item_id}", response_model=CartItemOut)
async def update_cart_item(
    user_id: uuid.UUID,
    item_id: uuid.UUID,
    item_data: CartItemUpdate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> CartItemOut:
    """Update a cart item (quantity or instructions)."""
    # Verify user authorization
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage your own cart",
        )

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
    await session.refresh(item)
    await session.refresh(item.dish)

    return CartItemOut.model_validate(item)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_cart_item(
    user_id: uuid.UUID,
    item_id: uuid.UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Response:
    """Remove an item from the cart."""
    # Verify user authorization
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage your own cart",
        )

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
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Response:
    """Clear all items from the cart."""
    # Verify user authorization
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage your own cart",
        )

    # Get cart with items
    result = await session.execute(
        select(Cart)
        .options(selectinload(Cart.items))
        .where(Cart.user_id == user_id, Cart.is_deleted.is_(False))
    )
    cart = result.scalar_one_or_none()
    if not cart:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # Soft delete all items
    for item in cart.items:
        item.is_deleted = True

    await update_cart_totals(cart, session)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

