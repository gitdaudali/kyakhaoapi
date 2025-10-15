import os
from datetime import datetime, timedelta
from typing import Optional

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from app.schemas.subscription import StripeCheckoutSessionCreate, StripeCheckoutSessionResponse
from app.utils.subscription_utils import SubscriptionService

load_dotenv()
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

router = APIRouter()
templates = Jinja2Templates(directory="static")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Display the home page with purchase form"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/checkout", response_model=StripeCheckoutSessionResponse)
async def create_checkout_session(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe checkout session for subscription"""
    try:
        # Get price_id from environment variable
        price_id = os.getenv('STRIPE_PRICE_ID_PREMIUM')
        if not price_id:
            raise HTTPException(status_code=500, detail="STRIPE_PRICE_ID_PREMIUM not configured")

        # Create subscription service
        subscription_service = SubscriptionService(db)
        
        # Create checkout session
        base_url = os.getenv('BASE_URL', 'http://localhost:8000')
        success_url = f"{base_url}/api/v1/stripe/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{base_url}/api/v1/stripe/cancel"
        
        session_data = subscription_service.create_checkout_session(
            user=current_user,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url
        )

        return StripeCheckoutSessionResponse(**session_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/checkout-simple")
async def create_checkout_session_simple(
    request: dict,
    db: Session = Depends(get_db)
):
    """Create a simple checkout session (for testing without auth) - CHECKS FOR EXISTING SUBSCRIPTION FIRST"""
    try:
        # Get user email and plan type from request
        user_email = request.get('user_email')
        plan_type = request.get('plan_type', 'premium_monthly')  # Default to premium monthly
        
        if not user_email:
            raise HTTPException(status_code=400, detail="user_email is required")
        
        # Find user by email
        from sqlmodel import select
        from app.models.user import User
        
        statement = select(User).where(User.email == user_email)
        result = await db.execute(statement)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # ⚠️ CHECK FOR EXISTING ACTIVE SUBSCRIPTION BEFORE CREATING STRIPE SESSION
        existing_subscription_result = await db.execute(
            select(Subscription).where(
                Subscription.user_id == user.id,
                Subscription.status.in_(['active', 'trialing'])
            )
        )
        existing_subscription = existing_subscription_result.scalar_one_or_none()
        
        if existing_subscription:
            raise HTTPException(
                status_code=400, 
                detail=f"User already has an active {existing_subscription.plan} subscription. Please cancel it before purchasing a new one."
            )
        
        # Get price_id based on plan type
        price_id_map = {
            'basic': os.getenv('STRIPE_PRICE_ID_BASIC'),
            'premium_monthly': os.getenv('STRIPE_PRICE_ID_PREMIUM_PER_MONTH'),
            'premium_yearly': os.getenv('STRIPE_PRICE_ID_PREMIUM_PER_YEAR')
        }
        
        price_id = price_id_map.get(plan_type)
        if not price_id:
            raise HTTPException(status_code=500, detail=f"Price ID for {plan_type} not configured in .env file")

        # Now create Stripe session (user doesn't have active subscription)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1
                }
            ],
            mode='subscription',
            success_url=f"{os.getenv('BASE_URL', 'http://localhost:8000')}/api/v1/stripe/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('BASE_URL', 'http://localhost:8000')}/api/v1/stripe/cancel",
            customer_email=user.email,  # Pre-fill user's email
            metadata={
                'app_name': 'Cup Streaming',
                'user_id': str(user.id),
                'user_email': user.email,
                'plan_type': plan_type,
                'price_id': price_id
            }
        )

        return {"checkout_url": checkout_session.url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/success")
async def success(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Handle successful payment and create subscription record"""
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")
    
    try:
        # Get Stripe session details
        session = stripe.checkout.Session.retrieve(session_id)

        # 🔒 SECURITY CHECK 1: Payment must be completed
        if session.payment_status != 'paid':
            return f'''
            <h1>❌ Payment Not Completed</h1>
            <p>The payment was not successful. No subscription has been created.</p>
            <p><strong>Payment Status:</strong> {session.payment_status}</p>
            <br>
            <a href="/static/test-subscription.html">← Try Again</a>
            '''
        
        # 🔒 SECURITY CHECK 2: Subscription must exist in Stripe
        if not session.subscription:
            return f'''
            <h1>❌ No Subscription Created</h1>
            <p>Payment was received but no subscription was created by Stripe.</p>
            <p>Please contact support with session ID: {session_id}</p>
            <br>
            <a href="/static/test-subscription.html">← Back</a>
            '''
        
        # Get customer email from session
        customer_email = session.customer_details.email
        
        # Find user by email using async session
        from sqlmodel import select
        from app.models.user import User
        
        statement = select(User).where(User.email == customer_email)
        result = await db.execute(statement)
        user = result.scalar_one_or_none()
        
        if not user:
            return f'Payment successful but user not found! (Email: {customer_email})'
        
        # Check if subscription already exists for this Stripe subscription ID
        existing_result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == session.subscription
            )
        )
        existing_subscription = existing_result.scalar_one_or_none()
        
        if existing_subscription:
            return f'''
            <h1>⚠️ Subscription Already Processed!</h1>
            <p><strong>User:</strong> {user.email}</p>
            <p><strong>Plan:</strong> {existing_subscription.plan}</p>
            <p><strong>Status:</strong> {existing_subscription.status}</p>
            <p>This subscription has already been added to the database.</p>
            <br>
            <a href="/static/test-subscription.html">← Back to Test Page</a>
            '''
        
        # Check if user already has an active subscription
        active_subscription_result = await db.execute(
            select(Subscription).where(
                Subscription.user_id == user.id,
                Subscription.status.in_(['active', 'trialing'])
            )
        )
        active_subscription = active_subscription_result.scalar_one_or_none()
        
        if active_subscription:
            return f'''
            <h1>⚠️ User Already Has Active Subscription!</h1>
            <p><strong>User:</strong> {user.email}</p>
            <p><strong>Existing Plan:</strong> {active_subscription.plan}</p>
            <p><strong>Status:</strong> {active_subscription.status}</p>
            <p><strong>Period End:</strong> {active_subscription.current_period_end}</p>
            <p>Please cancel your existing subscription before purchasing a new one.</p>
            <br>
            <a href="/static/test-subscription.html">← Back to Test Page</a>
            '''
        
        # Determine plan type based on metadata from session
        plan_type = session.metadata.get('plan_type', 'premium_monthly') if hasattr(session, 'metadata') else 'premium_monthly'
        
        plan_type_to_enum = {
            'basic': SubscriptionPlan.BASIC,
            'premium_monthly': SubscriptionPlan.PREMIUM_MONTHLY,
            'premium_yearly': SubscriptionPlan.PREMIUM_YEARLY
        }
        
        plan = plan_type_to_enum.get(plan_type, SubscriptionPlan.PREMIUM_MONTHLY)
        
        # Create subscription record
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id=session.subscription,
            stripe_customer_id=session.customer,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            price_id=session.metadata.get('price_id') if hasattr(session, 'metadata') else None,
            amount=session.amount_total // 100,  # Convert cents to dollars
            currency=session.currency,
            current_period_start=datetime.fromtimestamp(session.created),
            current_period_end=datetime.fromtimestamp(session.created) + timedelta(days=30),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)
        
        return f'''
        <h1>🎉 Subscription Created Successfully!</h1>
        <p><strong>User:</strong> {user.email}</p>
        <p><strong>Plan:</strong> {subscription.plan}</p>
        <p><strong>Status:</strong> {subscription.status}</p>
        <p><strong>Amount:</strong> ${subscription.amount} {subscription.currency.upper()}</p>
        <p><strong>Subscription ID:</strong> {subscription.id}</p>
        <p><strong>Stripe Session:</strong> {session_id}</p>
        <br>
        <a href="/static/test-subscription.html">← Back to Test Page</a>
        '''
        
    except Exception as e:
        return f'Error creating subscription: {str(e)}'


@router.get("/cancel")
async def cancel():
    """Handle canceled payment"""
    return "Payment canceled!"


@router.post("/create-subscription")
async def create_subscription_manually(
    user_email: str,
    stripe_session_id: str,
    db: Session = Depends(get_db)
):
    """Manually create subscription record for testing"""
    try:
        # Get user by email
        from sqlmodel import select
        from app.models.user import User
        
        statement = select(User).where(User.email == user_email)
        user = db.exec(statement).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get Stripe session details
        session = stripe.checkout.Session.retrieve(stripe_session_id)
        
        if session.payment_status != 'paid':
            raise HTTPException(status_code=400, detail="Payment not completed")
        
        # Create subscription record
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id=session.subscription,
            stripe_customer_id=session.customer,
            plan=SubscriptionPlan.PREMIUM,
            status=SubscriptionStatus.ACTIVE,
            price_id=os.getenv('STRIPE_PRICE_ID_PREMIUM'),
            amount=session.amount_total,
            currency=session.currency,
            current_period_start=datetime.fromtimestamp(session.created),
            current_period_end=datetime.fromtimestamp(session.created) + timedelta(days=30),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return {
            "message": "Subscription created successfully",
            "subscription_id": subscription.id,
            "user_id": str(user.id),
            "plan": subscription.plan,
            "status": subscription.status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_publishable_key():
    """Get Stripe publishable key for frontend"""
    publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
    if not publishable_key:
        raise HTTPException(status_code=500, detail="STRIPE_PUBLISHABLE_KEY not configured")
    return {"publishable_key": publishable_key}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="STRIPE_WEBHOOK_SECRET not configured")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event using subscription service
    subscription_service = SubscriptionService(db)
    try:
        subscription_service.handle_webhook_event(event)
    except Exception as e:
        print(f"Error handling webhook event: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")
    
    return {"status": "success"}