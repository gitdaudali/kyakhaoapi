"""Membership utilities for plans, payments, and subscriptions."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import (
    MembershipPlan,
    Payment,
    PaymentStatus,
    Subscription,
    SubscriptionStatus,
)
from app.models.user import User


async def get_active_membership_plan(
    session: AsyncSession,
) -> Optional[MembershipPlan]:
    """
    Get the active membership plan.
    
    Args:
        session: Database session
        
    Returns:
        Active membership plan or None if not found
    """
    result = await session.execute(
        select(MembershipPlan).where(
            MembershipPlan.is_active == True, MembershipPlan.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


async def get_membership_plan_by_id(
    session: AsyncSession, plan_id: UUID, include_deleted: bool = False
) -> Optional[MembershipPlan]:
    """
    Get membership plan by ID.
    
    Args:
        session: Database session
        plan_id: Plan UUID
        include_deleted: Whether to include soft-deleted plans
        
    Returns:
        Membership plan or None if not found
    """
    query = select(MembershipPlan).where(MembershipPlan.id == plan_id)
    if not include_deleted:
        query = query.where(MembershipPlan.is_deleted == False)
    
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def tokenize_card(
    card_number: str, exp_month: int, exp_year: int, cvv: str, name_on_card: str
) -> Dict[str, str]:
    """
    Simulate card tokenization (Stripe-like).
    
    In production, this would call Stripe API:
    stripe.Token.create(card={
        'number': card_number,
        'exp_month': exp_month,
        'exp_year': exp_year,
        'cvv': cvv,
        'name': name_on_card,
    })
    
    Args:
        card_number: Card number
        exp_month: Expiration month (1-12)
        exp_year: Expiration year
        cvv: CVV code
        name_on_card: Name on card
        
    Returns:
        Dictionary with token key
    """
    # Simulate token generation
    # In production, replace with actual Stripe API call
    token = f"tok_{secrets.token_urlsafe(32)}"
    
    return {"token": token}


async def charge(amount: float, token: str) -> Dict[str, str]:
    """
    Simulate charging a card using a token.
    
    In production, this would call Stripe API:
    stripe.Charge.create(
        amount=int(amount * 100),  # Convert to cents
        currency='pkr',
        source=token,
    )
    
    Args:
        amount: Amount to charge
        token: Payment token from tokenize_card
        
    Returns:
        Dictionary with transaction_id and status
    """
    # Simulate charge processing
    # In production, replace with actual Stripe API call
    transaction_id = f"txn_{secrets.token_urlsafe(32)}"
    
    # Simulate successful charge (in production, check Stripe response)
    return {
        "transaction_id": transaction_id,
        "status": PaymentStatus.COMPLETED.value,
    }


async def start_subscription(
    session: AsyncSession, user_id: UUID, payment_token: str
) -> Subscription:
    """
    Start a new subscription for a user.
    
    Args:
        session: Database session
        user_id: User ID
        payment_token: Payment token from tokenization
        
    Returns:
        Created subscription
        
    Raises:
        ValueError: If no active plan found or user not found
    """
    # Fetch active membership plan
    plan_result = await session.execute(
        select(MembershipPlan).where(
            MembershipPlan.is_active == True, MembershipPlan.is_deleted == False
        )
    )
    plan = plan_result.scalar_one_or_none()
    
    if not plan:
        raise ValueError("No active membership plan found")
    
    # Fetch user
    user_result = await session.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise ValueError("User not found")
    
    # Charge the user
    charge_result = await charge(plan.price, payment_token)
    
    if charge_result["status"] != "completed":
        raise ValueError(f"Payment failed: {charge_result.get('status', 'unknown')}")
    
    # Calculate renewal date (30 days from now for monthly)
    now = datetime.now(timezone.utc)
    renewal_date = now + timedelta(days=30)
    
    # Create subscription
    subscription = Subscription(
        user_id=user_id,
        plan_id=plan.id,
        status=SubscriptionStatus.ACTIVE,
        start_date=now,
        renewal_date=renewal_date,
        payment_token=payment_token,
    )
    
    session.add(subscription)
    await session.flush()
    
    # Create payment record
    payment = Payment(
        subscription_id=subscription.id,
        amount=plan.price,
        status=PaymentStatus.COMPLETED,
        transaction_id=charge_result.get("transaction_id"),
        created_at=now,
    )
    
    session.add(payment)
    await session.flush()
    
    # Update user premium status
    user.is_premium = True
    session.add(user)
    
    await session.commit()
    
    # Refresh subscription to load relationships
    await session.refresh(subscription)
    
    return subscription


async def cancel_subscription(session: AsyncSession, user_id: UUID) -> Optional[Subscription]:
    """
    Cancel a user's active subscription.
    
    Args:
        session: Database session
        user_id: User ID
        
    Returns:
        Cancelled subscription or None if not found
    """
    # Find active subscription
    result = await session.execute(
        select(Subscription)
        .where(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.is_deleted == False,
        )
        .order_by(Subscription.created_at.desc())
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        return None
    
    # Cancel subscription
    subscription.status = SubscriptionStatus.CANCELLED
    subscription.end_date = datetime.now(timezone.utc)
    session.add(subscription)
    
    # Update user premium status
    user_result = await session.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    
    if user:
        user.is_premium = False
        session.add(user)
    
    await session.commit()
    await session.refresh(subscription)
    
    return subscription


async def handle_renewals(session: AsyncSession) -> int:
    """
    Handle subscription renewals for subscriptions due for renewal.
    
    This should be called by a scheduled task (e.g., Celery beat).
    
    Args:
        session: Database session
        
    Returns:
        Number of subscriptions renewed
    """
    now = datetime.now(timezone.utc)
    
    # Find subscriptions due for renewal
    result = await session.execute(
        select(Subscription)
        .where(
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.renewal_date <= now,
            Subscription.is_deleted == False,
        )
    )
    subscriptions = result.scalars().all()
    
    renewed_count = 0
    
    for subscription in subscriptions:
        try:
            # Load plan relationship
            await session.refresh(subscription, ["plan"])
            
            # Attempt to charge for renewal
            charge_result = await charge(subscription.plan.price, subscription.payment_token)
            
            if charge_result["status"] == "completed":
                # Update renewal date
                subscription.renewal_date = now + timedelta(days=30)
                session.add(subscription)
                
                # Create payment record for renewal
                payment = Payment(
                    subscription_id=subscription.id,
                    amount=subscription.plan.price,
                    status=PaymentStatus.COMPLETED,
                    transaction_id=charge_result.get("transaction_id"),
                    created_at=now,
                )
                session.add(payment)
                
                renewed_count += 1
            else:
                # Mark as expired if payment fails
                subscription.status = SubscriptionStatus.EXPIRED
                subscription.end_date = now
                session.add(subscription)
                
                # Create failed payment record
                payment = Payment(
                    subscription_id=subscription.id,
                    amount=subscription.plan.price,
                    status=PaymentStatus.FAILED,
                    transaction_id=charge_result.get("transaction_id"),
                    created_at=now,
                )
                session.add(payment)
                
                # Update user premium status
                user_result = await session.execute(
                    select(User).where(User.id == subscription.user_id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    user.is_premium = False
                    session.add(user)
        except Exception:
            # Mark as expired on any error
            subscription.status = SubscriptionStatus.EXPIRED
            subscription.end_date = now
            session.add(subscription)
            
            # Create failed payment record
            try:
                await session.refresh(subscription, ["plan"])
                payment = Payment(
                    subscription_id=subscription.id,
                    amount=subscription.plan.price,
                    status=PaymentStatus.FAILED,
                    created_at=now,
                )
                session.add(payment)
            except Exception:
                pass  # Ignore payment creation errors
    
    await session.commit()
    
    return renewed_count


async def get_user_payments(
    session: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Payment], int]:
    """
    Get all payments for a user's subscriptions.
    
    Args:
        session: Database session
        user_id: User UUID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        Tuple of (list of payments, total count)
    """
    # Get user's subscription IDs
    subscriptions_result = await session.execute(
        select(Subscription.id).where(
            Subscription.user_id == user_id,
            Subscription.is_deleted == False,
        )
    )
    subscription_ids = [sub.id for sub in subscriptions_result.scalars().all()]
    
    if not subscription_ids:
        return [], 0
    
    # Get total count
    count_query = select(Payment).where(Payment.subscription_id.in_(subscription_ids))
    total_result = await session.execute(select(func.count()).select_from(count_query.subquery()))
    total = total_result.scalar() or 0
    
    # Get payments
    payments_query = (
        select(Payment)
        .where(Payment.subscription_id.in_(subscription_ids))
        .order_by(Payment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    payments_result = await session.execute(payments_query)
    payments = payments_result.scalars().all()
    
    return list(payments), total


async def get_user_subscriptions(
    session: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Subscription], int]:
    """
    Get all subscriptions for a user (including cancelled/expired).
    
    Args:
        session: Database session
        user_id: User UUID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        Tuple of (list of subscriptions, total count)
    """
    # Get total count
    count_query = select(func.count()).select_from(Subscription).where(
        Subscription.user_id == user_id,
        Subscription.is_deleted == False,
    )
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get subscriptions
    subscriptions_query = (
        select(Subscription)
        .where(Subscription.user_id == user_id, Subscription.is_deleted == False)
        .order_by(Subscription.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    subscriptions_result = await session.execute(subscriptions_query)
    subscriptions = subscriptions_result.scalars().all()
    
    return list(subscriptions), total


async def retry_failed_payment(
    session: AsyncSession,
    payment_id: UUID,
    user_id: UUID,
) -> Payment:
    """
    Retry a failed payment.
    
    Args:
        session: Database session
        payment_id: Payment UUID
        user_id: User UUID (for security)
        
    Returns:
        Updated payment
        
    Raises:
        ValueError: If payment not found or not failed
    """
    # Get payment and verify it belongs to user
    payment_result = await session.execute(
        select(Payment)
        .join(Subscription)
        .where(
            Payment.id == payment_id,
            Subscription.user_id == user_id,
            Payment.status == PaymentStatus.FAILED,
        )
    )
    payment = payment_result.scalar_one_or_none()
    
    if not payment:
        raise ValueError("Failed payment not found or does not belong to user")
    
    # Get subscription
    subscription_result = await session.execute(
        select(Subscription).where(Subscription.id == payment.subscription_id)
    )
    subscription = subscription_result.scalar_one()
    
    if not subscription.payment_token:
        raise ValueError("No payment token available for retry")
    
    # Retry charge
    charge_result = await charge(payment.amount, subscription.payment_token)
    
    if charge_result["status"] == "completed":
        payment.status = PaymentStatus.COMPLETED
        payment.transaction_id = charge_result.get("transaction_id")
        
        # Reactivate subscription if expired
        if subscription.status == SubscriptionStatus.EXPIRED:
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.renewal_date = datetime.now(timezone.utc) + timedelta(days=30)
            subscription.end_date = None
            
            # Update user premium status
            user_result = await session.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one()
            user.is_premium = True
            session.add(user)
    else:
        payment.status = PaymentStatus.FAILED
    
    session.add(payment)
    session.add(subscription)
    await session.commit()
    await session.refresh(payment)
    
    return payment