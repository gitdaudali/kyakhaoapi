"""Subscription endpoints."""

from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.core.response_handler import success_response
from app.models.membership import MembershipPlan, Payment, Subscription, SubscriptionStatus
from app.schemas.membership import (
    ChangePlanRequest,
    InvoiceOut,
    MembershipPlanOut,
    PaymentListResponse,
    PaymentOut,
    SubscriptionListResponse,
    SubscriptionOut,
)
from app.utils.membership_utils import (
    cancel_subscription,
    get_membership_plan_by_id,
    get_user_payments,
    get_user_subscriptions,
    retry_failed_payment,
)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/me")
async def get_user_subscription(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get current user's active subscription.
    
    Args:
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        User's current subscription wrapped in success response
    """
    result = await session.execute(
        select(Subscription)
        .where(
            Subscription.user_id == current_user.id,
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.is_deleted == False,
        )
        .order_by(Subscription.created_at.desc())
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found for this user",
        )
    
    # Load plan data via query since relationship is commented out
    plan_query = select(MembershipPlan).where(MembershipPlan.id == subscription.plan_id)
    plan_result = await session.execute(plan_query)
    plan = plan_result.scalar_one()
    
    subscription_out = SubscriptionOut.model_validate(subscription)
    subscription_out.plan = MembershipPlanOut.model_validate(plan)
    
    return success_response(
        message="Subscription retrieved successfully",
        data=subscription_out.model_dump(),
        use_body=True
    )


@router.get("/all")
async def get_all_user_subscriptions(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all user subscriptions (including cancelled/expired).
    
    Args:
        current_user: Current authenticated user
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of all subscriptions wrapped in success response
    """
    subscriptions_list, total = await get_user_subscriptions(
        session, current_user.id, skip=skip, limit=limit
    )
    
    # Load plan data for each subscription
    subscription_outs = []
    for sub in subscriptions_list:
        plan_query = select(MembershipPlan).where(MembershipPlan.id == sub.plan_id)
        plan_result = await session.execute(plan_query)
        plan = plan_result.scalar_one()
        
        sub_out = SubscriptionOut.model_validate(sub)
        sub_out.plan = MembershipPlanOut.model_validate(plan)
        subscription_outs.append(sub_out)
    
    subscription_list_response = SubscriptionListResponse(
        subscriptions=subscription_outs, total=total
    )
    
    return success_response(
        message="Subscriptions retrieved successfully",
        data=subscription_list_response.model_dump(),
        use_body=True
    )


@router.get("/payments")
async def get_payment_history(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get payment history for current user.
    
    Args:
        current_user: Current authenticated user
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        Payment history wrapped in success response
    """
    payments_list, total = await get_user_payments(
        session, current_user.id, skip=skip, limit=limit
    )
    
    payment_outs = [PaymentOut.model_validate(payment) for payment in payments_list]
    payment_list_response = PaymentListResponse(payments=payment_outs, total=total)
    
    return success_response(
        message="Payment history retrieved successfully",
        data=payment_list_response.model_dump(),
        use_body=True
    )


@router.get("/payments/{payment_id}/invoice")
async def get_payment_invoice(
    payment_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get invoice for a specific payment.
    
    Args:
        payment_id: Payment UUID
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        Invoice details wrapped in success response
    """
    # Get payment and verify it belongs to user
    payment_result = await session.execute(
        select(Payment)
        .join(Subscription)
        .where(Payment.id == payment_id, Subscription.user_id == current_user.id)
    )
    payment = payment_result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found or does not belong to user",
        )
    
    # Get subscription and plan
    subscription_result = await session.execute(
        select(Subscription).where(Subscription.id == payment.subscription_id)
    )
    subscription = subscription_result.scalar_one()
    
    plan_query = select(MembershipPlan).where(MembershipPlan.id == subscription.plan_id)
    plan_result = await session.execute(plan_query)
    plan = plan_result.scalar_one()
    
    # Generate invoice (dummy data for now)
    invoice_id = f"INV-{payment.id.hex[:8].upper()}"
    billing_period = f"{payment.created_at.strftime('%B %Y')}"
    
    invoice = InvoiceOut(
        invoice_id=invoice_id,
        payment_id=payment.id,
        subscription_id=subscription.id,
        amount=payment.amount,
        currency=plan.currency,
        status=payment.status,
        transaction_id=payment.transaction_id,
        invoice_date=payment.created_at,
        plan_name=plan.name,
        billing_period=billing_period,
    )
    
    return success_response(
        message="Invoice retrieved successfully",
        data=invoice.model_dump(),
        use_body=True
    )


@router.post("/payments/{payment_id}/retry")
async def retry_payment(
    payment_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retry a failed payment.
    
    Args:
        payment_id: Payment UUID
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        Updated payment wrapped in success response
    """
    try:
        payment = await retry_failed_payment(session, payment_id, current_user.id)
        payment_out = PaymentOut.model_validate(payment)
        
        return success_response(
            message="Payment retry successful" if payment.status.value == "completed" else "Payment retry failed",
            data=payment_out.model_dump(),
            use_body=True
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry payment: {str(e)}",
        )


@router.post("/change-plan")
async def change_subscription_plan(
    request: ChangePlanRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """
    Change subscription plan (upgrade/downgrade).
    
    Args:
        request: Change plan request
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        Updated subscription wrapped in success response
    """
    try:
        # Validate terms acceptance
        if not request.terms_accepted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must accept the terms and conditions to change plan",
            )
        
        # Get current active subscription
        subscription_result = await session.execute(
            select(Subscription).where(
                Subscription.user_id == current_user.id,
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.is_deleted == False,
            )
        )
        subscription = subscription_result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found",
            )
        
        # Verify new plan exists
        new_plan = await get_membership_plan_by_id(session, request.new_plan_id)
        if not new_plan or not new_plan.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New plan not found or not active",
            )
        
        # If same plan, return current subscription
        if subscription.plan_id == request.new_plan_id:
            plan_query = select(MembershipPlan).where(MembershipPlan.id == subscription.plan_id)
            plan_result = await session.execute(plan_query)
            plan = plan_result.scalar_one()
            
            subscription_out = SubscriptionOut.model_validate(subscription)
            subscription_out.plan = MembershipPlanOut.model_validate(plan)
            
            return success_response(
                message="Subscription plan is already set to this plan",
                data=subscription_out.model_dump(),
                use_body=True
            )
        
        # Update subscription plan
        subscription.plan_id = request.new_plan_id
        session.add(subscription)
        await session.commit()
        await session.refresh(subscription)
        
        # Load plan data
        plan_query = select(MembershipPlan).where(MembershipPlan.id == subscription.plan_id)
        plan_result = await session.execute(plan_query)
        plan = plan_result.scalar_one()
        
        subscription_out = SubscriptionOut.model_validate(subscription)
        subscription_out.plan = MembershipPlanOut.model_validate(plan)
        
        return success_response(
            message="Subscription plan changed successfully",
            data=subscription_out.model_dump(),
            use_body=True
        )
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change plan: {str(e)}",
        )


@router.post("/reactivate")
async def reactivate_subscription(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """
    Reactivate an expired or cancelled subscription.
    
    If subscription has payment token, charges immediately and reactivates.
    Otherwise, returns subscription for payment update.
    
    Args:
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        Reactivated subscription details wrapped in success response
    """
    # Find expired or cancelled subscription
    subscription_result = await session.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status.in_([SubscriptionStatus.EXPIRED, SubscriptionStatus.CANCELLED]),
            Subscription.is_deleted == False,
        )
        .order_by(Subscription.created_at.desc())
    )
    subscription = subscription_result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No expired or cancelled subscription found",
        )
    
    # Get plan
    plan_query = select(MembershipPlan).where(MembershipPlan.id == subscription.plan_id)
    plan_result = await session.execute(plan_query)
    plan = plan_result.scalar_one()
    
    # If payment token exists, try to reactivate immediately
    if subscription.payment_token:
        from app.utils.membership_utils import charge
        from app.models.membership import PaymentStatus
        
        charge_result = await charge(plan.price, subscription.payment_token)
        
        if charge_result["status"] == "completed":
            # Reactivate subscription
            from datetime import datetime, timedelta, timezone
            now = datetime.now(timezone.utc)
            
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.start_date = now
            subscription.renewal_date = now + timedelta(days=30)
            subscription.end_date = None
            session.add(subscription)
            
            # Create payment record
            from app.models.membership import Payment
            payment = Payment(
                subscription_id=subscription.id,
                amount=plan.price,
                status=PaymentStatus.COMPLETED,
                transaction_id=charge_result.get("transaction_id"),
                created_at=now,
            )
            session.add(payment)
            
            # Update user premium status
            from app.models.user import User
            user_result = await session.execute(select(User).where(User.id == current_user.id))
            user = user_result.scalar_one()
            user.is_premium = True
            session.add(user)
            
            await session.commit()
            await session.refresh(subscription)
            
            subscription_out = SubscriptionOut.model_validate(subscription)
            subscription_out.plan = MembershipPlanOut.model_validate(plan)
            
            return success_response(
                message="Subscription reactivated successfully",
                data=subscription_out.model_dump(),
                use_body=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment failed. Please update your payment method and try again.",
            )
    else:
        # No payment token - subscription needs new payment method
        subscription_out = SubscriptionOut.model_validate(subscription)
        subscription_out.plan = MembershipPlanOut.model_validate(plan)
        
        return success_response(
            message="Subscription found. Please update payment method to reactivate.",
            data=subscription_out.model_dump(),
            use_body=True
        )


@router.post("/cancel")
async def cancel_user_subscription(
    current_user: CurrentUser,
    subscription_id: Optional[UUID] = Query(
        None, 
        description="Optional: Specific subscription ID to cancel. If not provided, cancels the most recent active subscription."
    ),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """
    Cancel current user's subscription.
    
    If subscription_id is provided, cancels that specific subscription.
    Otherwise, cancels the most recent active subscription.
    
    Only sets user.is_premium = False if there are no other active subscriptions.
    
    Args:
        subscription_id: Optional specific subscription ID to cancel
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        Cancelled subscription details wrapped in success response
    """
    subscription = await cancel_subscription(
        session=session, 
        user_id=current_user.id,
        subscription_id=subscription_id
    )
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found for this user",
        )
    
    # Load plan data via query since relationship is commented out
    plan_query = select(MembershipPlan).where(MembershipPlan.id == subscription.plan_id)
    plan_result = await session.execute(plan_query)
    plan = plan_result.scalar_one()
    
    subscription_out = SubscriptionOut.model_validate(subscription)
    subscription_out.plan = MembershipPlanOut.model_validate(plan)
    
    return success_response(
        message="Subscription cancelled successfully",
        data=subscription_out.model_dump(),
        use_body=True
    )

