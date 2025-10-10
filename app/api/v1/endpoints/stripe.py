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
async def create_checkout_session_simple():
    """Create a simple checkout session (for testing without auth)"""
    try:
        # Get price_id from environment variable
        price_id = os.getenv('STRIPE_PRICE_ID_PREMIUM')
        if not price_id:
            raise HTTPException(status_code=500, detail="STRIPE_PRICE_ID_PREMIUM not configured")

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
            customer_email=None,  # Let user enter email on Stripe checkout
            metadata={
                'app_name': 'Cup Streaming'
            }
        )

        return RedirectResponse(url=checkout_session.url, status_code=303)
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
        
        if session.payment_status != 'paid':
            return RedirectResponse(url="/api/v1/stripe/cancel")
        
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
        
        # Check if subscription already exists
        existing_result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == session.subscription
            )
        )
        existing_subscription = existing_result.scalar_one_or_none()
        
        if existing_subscription:
            return f'Subscription already exists! (User: {user.email}, Plan: {existing_subscription.plan})'
        
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
        await db.commit()
        await db.refresh(subscription)
        
        return f'''
        <h1>🎉 Subscription Created Successfully!</h1>
        <p><strong>User:</strong> {user.email}</p>
        <p><strong>Plan:</strong> {subscription.plan}</p>
        <p><strong>Status:</strong> {subscription.status}</p>
        <p><strong>Amount:</strong> ${subscription.amount/100} {subscription.currency.upper()}</p>
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