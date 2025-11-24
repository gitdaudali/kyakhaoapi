"""Membership endpoints - unified subscription flow."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.core.response_handler import success_response
from app.models.membership import MembershipPlan, Subscription, SubscriptionStatus
from app.schemas.membership import (
    MembershipPlanOut,
    MembershipSubscribeRequest,
    SubscriptionOut,
)
from app.utils.membership_utils import (
    get_active_membership_plan,
    start_subscription,
    tokenize_card,
)

router = APIRouter(tags=["Membership"])

# Public endpoint - no auth required (for getting plan details)
public_router = APIRouter(tags=["Membership"])


@public_router.get("/plan")
async def get_active_plan(session: AsyncSession = Depends(get_db)) -> Any:
    """
    Get the active membership plan (to display price on payment form).
    
    Returns:
        Active membership plan wrapped in success response
    """
    plan = await get_active_membership_plan(session)
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No active membership plan found"
        )
    
    plan_out = MembershipPlanOut.model_validate(plan)
    return success_response(
        message="Membership plan retrieved successfully",
        data=plan_out.model_dump(),
        use_body=True
    )


@router.post("/subscribe")
async def subscribe_to_membership(
    request: MembershipSubscribeRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """
    Subscribe to membership - unified endpoint for payment form.
    
    This endpoint handles:
    1. Card tokenization
    2. Terms validation
    3. Payment processing
    4. Subscription creation
    
    Args:
        request: Card details and terms acceptance
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        Created subscription details wrapped in success response
    """
    try:
        # Validate terms acceptance
        if not request.terms_accepted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must accept the terms and conditions to start a subscription",
            )
        
        # Step 1: Tokenize card
        tokenize_result = await tokenize_card(
            card_number=request.card_number,
            exp_month=request.exp_month,
            exp_year=request.exp_year,
            cvv=request.cvv,
            name_on_card=request.name_on_card,
        )
        payment_token = tokenize_result["token"]
        
        # Step 2: Start subscription (handles payment and subscription creation)
        subscription = await start_subscription(
            session=session, user_id=current_user.id, payment_token=payment_token
        )
        
        # Load plan data
        plan_query = select(MembershipPlan).where(MembershipPlan.id == subscription.plan_id)
        plan_result = await session.execute(plan_query)
        plan = plan_result.scalar_one()
        
        subscription_out = SubscriptionOut.model_validate(subscription)
        subscription_out.plan = MembershipPlanOut.model_validate(plan)
        
        return success_response(
            message="Membership subscription started successfully",
            data=subscription_out.model_dump(),
            status_code=status.HTTP_201_CREATED,
            use_body=True
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start subscription: {str(e)}",
        )

