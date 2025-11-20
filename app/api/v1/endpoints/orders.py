"""Order API endpoints for creating and tracking orders."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.models.cart import Cart, CartItem, Order, OrderItem, OrderStatus
from app.models.food import Dish
from app.schemas.cart import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["Orders"])


def generate_order_number() -> str:
    """Generate unique order number."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"ORD-{timestamp}-{unique_id}"


async def get_cart_with_items(
    user_id: uuid.UUID, session: AsyncSession
) -> Cart | None:
    """Get user's cart with all active items."""
    result = await session.execute(
        select(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.dish))
        .where(Cart.user_id == user_id, Cart.is_deleted.is_(False))
    )
    cart = result.scalar_one_or_none()
    if cart:
        # Filter out deleted items
        cart.items = [item for item in cart.items if not item.is_deleted]
    return cart


async def get_order_or_404(
    order_id: uuid.UUID, user_id: uuid.UUID, session: AsyncSession
) -> Order:
    """Get order or raise 404, with authorization check."""
    result = await session.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id, Order.is_deleted.is_(False))
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    # Verify user owns this order
    if order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own orders",
        )

    return order


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> OrderOut:
    """
    Create an order from the user's cart.
    
    **Request Body Examples:**
    
    **1. Order from Specific Cart Items:**
    ```json
    {
      "customer_name": "John Doe",
      "customer_email": "john.doe@example.com",
      "customer_phone": "+1234567890",
      "delivery_address": "123 Main Street, Apt 4B",
      "delivery_city": "New York",
      "delivery_notes": "Please ring doorbell twice",
      "delivery_fee": 5.00,
      "tax_amount": 2.50,
      "discount_amount": 0.00,
      "cart_item_ids": [
        "550e8400-e29b-41d4-a716-446655440000",
        "550e8400-e29b-41d4-a716-446655440001"
      ]
    }
    ```
    
    **2. Order from All Cart Items (omit cart_item_ids or set to null):**
    ```json
    {
      "customer_name": "Jane Smith",
      "customer_email": "jane.smith@example.com",
      "customer_phone": "+1987654321",
      "delivery_address": "456 Oak Avenue",
      "delivery_city": "Los Angeles",
      "delivery_notes": "Leave at front door",
      "delivery_fee": 7.50,
      "tax_amount": 3.75,
      "discount_amount": 5.00,
      "cart_item_ids": null
    }
    ```
    
    **3. Minimal Request (all cart items):**
    ```json
    {
      "customer_name": "Bob Johnson",
      "customer_email": "bob@example.com"
    }
    ```
    
    **Notes:**
    - If `cart_item_ids` is provided, only those specific cart items will be ordered
    - If `cart_item_ids` is null or omitted, ALL items in the cart will be ordered
    - Cart must not be empty
    - All dishes must still be available and have valid prices
    - Total amount = subtotal + tax_amount + delivery_fee - discount_amount
    """
    # Get user's cart
    cart = await get_cart_with_items(current_user.id, session)

    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty. Add items to cart before creating an order.",
        )

    # Filter cart items if specific IDs are provided
    items_to_order = cart.items
    if order_data.cart_item_ids:
        # Filter to only include specified cart item IDs
        items_to_order = [
            item for item in cart.items 
            if item.id in order_data.cart_item_ids
        ]
        
        if not items_to_order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid cart items found for the provided cart_item_ids.",
            )
        
        # Validate all provided IDs exist in cart
        provided_ids = set(order_data.cart_item_ids)
        found_ids = {item.id for item in items_to_order}
        missing_ids = provided_ids - found_ids
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cart item IDs not found in your cart: {list(missing_ids)}",
            )

    # Verify all dishes still exist and have prices
    for item in items_to_order:
        dish_result = await session.execute(
            select(Dish).where(Dish.id == item.dish_id, Dish.is_deleted.is_(False))
        )
        dish = dish_result.scalar_one_or_none()
        if not dish:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dish {item.dish.name} is no longer available",
            )
        if dish.price is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dish {item.dish.name} does not have a price",
            )

    # Calculate totals from selected items only
    subtotal = sum(float(item.subtotal) for item in items_to_order)
    total = subtotal + order_data.tax_amount + order_data.delivery_fee - order_data.discount_amount

    if total < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total amount cannot be negative",
        )

    # Create order
    order = Order(
        user_id=current_user.id,
        order_number=generate_order_number(),
        status=OrderStatus.PENDING.value,
        subtotal=subtotal,
        tax_amount=order_data.tax_amount,
        delivery_fee=order_data.delivery_fee,
        discount_amount=order_data.discount_amount,
        total_amount=total,
        customer_name=order_data.customer_name,
        customer_email=order_data.customer_email,
        customer_phone=order_data.customer_phone,
        delivery_address=order_data.delivery_address,
        delivery_city=order_data.delivery_city,
        delivery_notes=order_data.delivery_notes,
        confirmed_at=datetime.now(timezone.utc),
    )

    session.add(order)
    await session.flush()

    # Create order items from selected cart items
    order_items = []
    for cart_item in items_to_order:
        dish_result = await session.execute(
            select(Dish).where(Dish.id == cart_item.dish_id)
        )
        dish = dish_result.scalar_one_or_none()

        order_item = OrderItem(
            order_id=order.id,
            dish_id=cart_item.dish_id,
            dish_name=dish.name if dish else cart_item.dish.name,
            quantity=cart_item.quantity,
            unit_price=float(cart_item.unit_price),
            subtotal=float(cart_item.subtotal),
            special_instructions=cart_item.special_instructions,
        )
        order_items.append(order_item)
        session.add(order_item)

    await session.flush()

    # Clear only the ordered items from cart (soft delete)
    for cart_item in items_to_order:
        cart_item.is_deleted = True

    # Recalculate cart totals based on remaining items
    remaining_items = [item for item in cart.items if not item.is_deleted]
    cart.total_amount = sum(float(item.subtotal) for item in remaining_items)
    cart.item_count = sum(item.quantity for item in remaining_items)

    await session.commit()
    await session.refresh(order)

    # Reload order with items
    result = await session.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order.id)
    )
    order = result.scalar_one()

    return OrderOut.model_validate(order)


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: uuid.UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> OrderOut:
    """Get order details and track order status."""
    order = await get_order_or_404(order_id, current_user.id, session)
    return OrderOut.model_validate(order)


@router.get("", response_model=list[OrderOut])
async def list_user_orders(
    current_user: CurrentUser,
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
) -> list[OrderOut]:
    """List all orders for the current user."""
    result = await session.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == current_user.id, Order.is_deleted.is_(False))
        .order_by(Order.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    orders = result.scalars().all()
    return [OrderOut.model_validate(order) for order in orders]

