from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlmodel import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.subscription import Subscription
from app.schemas.subscription import (
    SubscriptionResponse,
    SubscriptionWithPayments,
    UserSubscriptionInfo,
    CancelSubscriptionRequest,
    UpdateSubscriptionRequest,
    SubscriptionCreate,
)
from app.utils.subscription_utils import SubscriptionService

router = APIRouter()


@router.get("/my-subscription", response_model=UserSubscriptionInfo)
async def get_my_subscription_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription information"""
    subscription_service = SubscriptionService(db)
    subscription_info = subscription_service.get_subscription_info(str(current_user.id))
    return UserSubscriptionInfo(**subscription_info)


@router.get("/my-subscriptions", response_model=List[SubscriptionResponse])
async def get_my_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all subscriptions for current user"""
    subscription_service = SubscriptionService(db)
    subscriptions = subscription_service.get_user_subscriptions(str(current_user.id))
    return subscriptions


@router.get("/active", response_model=Optional[SubscriptionWithPayments])
async def get_active_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active subscription for current user"""
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_user_subscription(str(current_user.id))
    return subscription


@router.post("/create", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new subscription for current user"""
    subscription_service = SubscriptionService(db)
    
    # Check if user already has an active subscription
    existing_subscription = subscription_service.get_user_subscription(current_user.id)
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active subscription"
        )
    
    try:
        subscription = subscription_service.create_subscription(current_user, subscription_data)
        return subscription
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/cancel/{subscription_id}")
async def cancel_subscription(
    subscription_id: int,
    cancel_data: CancelSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a subscription"""
    subscription_service = SubscriptionService(db)
    
    # Verify subscription belongs to user
    statement = select(Subscription).where(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    )
    subscription = db.exec(statement).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    try:
        updated_subscription = subscription_service.cancel_subscription(
            subscription_id, 
            cancel_data.cancel_at_period_end
        )
        return {"message": "Subscription canceled successfully", "subscription": updated_subscription}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/update/{subscription_id}")
async def update_subscription(
    subscription_id: int,
    update_data: UpdateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a subscription (change plan)"""
    subscription_service = SubscriptionService(db)
    
    # Verify subscription belongs to user
    statement = select(Subscription).where(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    )
    subscription = db.exec(statement).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    try:
        # Update subscription in Stripe
        import stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            items=[{
                'id': subscription.stripe_subscription_id,
                'price': update_data.new_price_id,
            }],
            proration_behavior=update_data.proration_behavior
        )
        
        # Update local subscription
        subscription.price_id = update_data.new_price_id
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return {"message": "Subscription updated successfully", "subscription": subscription}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/check-access")
async def check_subscription_access(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user has access to premium features"""
    subscription_service = SubscriptionService(db)
    subscription_info = subscription_service.get_subscription_info(str(current_user.id))
    
    has_access = subscription_info['has_active_subscription']
    plan = subscription_info['current_plan']
    
    return {
        "has_premium_access": has_access,
        "current_plan": plan,
        "subscription_status": subscription_info['subscription_status'],
        "trial_ends_at": subscription_info['trial_ends_at'],
        "current_period_end": subscription_info['current_period_end']
    }
