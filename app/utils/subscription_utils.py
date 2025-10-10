import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

import stripe
from sqlalchemy.orm import Session
from sqlmodel import select

from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionPlan
from app.models.user import User
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

    def create_stripe_customer(self, user: User) -> str:
        """Create a Stripe customer for the user"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}".strip() if user.first_name or user.last_name else None,
                metadata={
                    'user_id': str(user.id),
                    'app_name': 'Cup Streaming'
                }
            )
            return customer.id
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create Stripe customer: {str(e)}")

    def create_subscription(self, user: User, subscription_data: SubscriptionCreate) -> Subscription:
        """Create a new subscription for a user"""
        # Create Stripe customer if not exists
        stripe_customer_id = subscription_data.stripe_customer_id
        if not stripe_customer_id:
            stripe_customer_id = self.create_stripe_customer(user)

        # Create Stripe subscription
        try:
            stripe_subscription = stripe.Subscription.create(
                customer=stripe_customer_id,
                items=[{'price': subscription_data.price_id}],
                metadata={
                    'user_id': str(user.id),
                    'plan': subscription_data.plan.value
                }
            )
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create Stripe subscription: {str(e)}")

        # Create local subscription record
        subscription = Subscription(
            user_id=str(user.id),
            stripe_subscription_id=stripe_subscription.id,
            stripe_customer_id=stripe_customer_id,
            plan=subscription_data.plan,
            status=SubscriptionStatus.ACTIVE,
            price_id=subscription_data.price_id,
            amount=stripe_subscription.items.data[0].price.unit_amount,
            currency=stripe_subscription.currency,
            current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
            current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end),
            trial_start=datetime.fromtimestamp(stripe_subscription.trial_start) if stripe_subscription.trial_start else None,
            trial_end=datetime.fromtimestamp(stripe_subscription.trial_end) if stripe_subscription.trial_end else None,
        )

        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get the active subscription for a user"""
        statement = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status.in_([
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.TRIALING,
                SubscriptionStatus.PAST_DUE
            ])
        )
        return self.db.exec(statement).first()

    def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """Get all subscriptions for a user"""
        statement = select(Subscription).where(Subscription.user_id == user_id)
        return list(self.db.exec(statement).all())

    def update_subscription_from_stripe(self, stripe_subscription_id: str) -> Optional[Subscription]:
        """Update local subscription from Stripe data"""
        try:
            stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)
        except stripe.error.StripeError:
            return None

        # Find local subscription
        statement = select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
        subscription = self.db.exec(statement).first()
        
        if not subscription:
            return None

        # Update subscription data
        subscription.status = self._map_stripe_status(stripe_subscription.status)
        subscription.current_period_start = datetime.fromtimestamp(stripe_subscription.current_period_start)
        subscription.current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
        subscription.trial_start = datetime.fromtimestamp(stripe_subscription.trial_start) if stripe_subscription.trial_start else None
        subscription.trial_end = datetime.fromtimestamp(stripe_subscription.trial_end) if stripe_subscription.trial_end else None
        subscription.canceled_at = datetime.fromtimestamp(stripe_subscription.canceled_at) if stripe_subscription.canceled_at else None
        subscription.cancel_at_period_end = stripe_subscription.cancel_at_period_end

        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def cancel_subscription(self, subscription_id: int, cancel_at_period_end: bool = True) -> Optional[Subscription]:
        """Cancel a subscription"""
        statement = select(Subscription).where(Subscription.id == subscription_id)
        subscription = self.db.exec(statement).first()
        
        if not subscription:
            return None

        try:
            if cancel_at_period_end:
                # Cancel at period end
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                subscription.cancel_at_period_end = True
            else:
                # Cancel immediately
                stripe.Subscription.delete(subscription.stripe_subscription_id)
                subscription.status = SubscriptionStatus.CANCELED
                subscription.canceled_at = datetime.utcnow()
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to cancel subscription: {str(e)}")

        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def get_subscription_info(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive subscription info for a user"""
        subscription = self.get_user_subscription(user_id)
        
        if not subscription:
            return {
                'has_active_subscription': False,
                'current_plan': None,
                'subscription_status': None,
                'trial_ends_at': None,
                'current_period_end': None,
                'cancel_at_period_end': False
            }

        return {
            'has_active_subscription': subscription.status in [
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.TRIALING
            ],
            'current_plan': subscription.plan,
            'subscription_status': subscription.status,
            'trial_ends_at': subscription.trial_end,
            'current_period_end': subscription.current_period_end,
            'cancel_at_period_end': subscription.cancel_at_period_end
        }

    def _map_stripe_status(self, stripe_status: str) -> SubscriptionStatus:
        """Map Stripe subscription status to our enum"""
        status_mapping = {
            'active': SubscriptionStatus.ACTIVE,
            'canceled': SubscriptionStatus.CANCELED,
            'incomplete': SubscriptionStatus.INACTIVE,
            'incomplete_expired': SubscriptionStatus.INACTIVE,
            'past_due': SubscriptionStatus.PAST_DUE,
            'trialing': SubscriptionStatus.TRIALING,
            'unpaid': SubscriptionStatus.UNPAID,
        }
        return status_mapping.get(stripe_status, SubscriptionStatus.INACTIVE)

    def create_checkout_session(self, user: User, price_id: str, success_url: str, cancel_url: str) -> Dict[str, str]:
        """Create a Stripe checkout session for subscription"""
        # Get or create Stripe customer
        stripe_customer_id = None
        existing_subscription = self.get_user_subscription(str(user.id))
        if existing_subscription and existing_subscription.stripe_customer_id:
            stripe_customer_id = existing_subscription.stripe_customer_id
        else:
            stripe_customer_id = self.create_stripe_customer(user)

        try:
            session = stripe.checkout.Session.create(
                customer=stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': str(user.id),
                    'app_name': 'Cup Streaming'
                }
            )
            return {
                'session_id': session.id,
                'session_url': session.url,
                'customer_id': stripe_customer_id
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create checkout session: {str(e)}")

    def handle_webhook_event(self, event: Dict[str, Any]) -> bool:
        """Handle Stripe webhook events"""
        event_type = event.get('type')
        
        if event_type == 'customer.subscription.created':
            return self._handle_subscription_created(event)
        elif event_type == 'customer.subscription.updated':
            return self._handle_subscription_updated(event)
        elif event_type == 'customer.subscription.deleted':
            return self._handle_subscription_deleted(event)
        elif event_type == 'invoice.payment_succeeded':
            return self._handle_payment_succeeded(event)
        elif event_type == 'invoice.payment_failed':
            return self._handle_payment_failed(event)
        
        return True  # Event not handled but not an error

    def _handle_subscription_created(self, event: Dict[str, Any]) -> bool:
        """Handle subscription created webhook"""
        # This is typically handled by the checkout session completion
        return True

    def _handle_subscription_updated(self, event: Dict[str, Any]) -> bool:
        """Handle subscription updated webhook"""
        stripe_subscription_id = event['data']['object']['id']
        self.update_subscription_from_stripe(stripe_subscription_id)
        return True

    def _handle_subscription_deleted(self, event: Dict[str, Any]) -> bool:
        """Handle subscription deleted webhook"""
        stripe_subscription_id = event['data']['object']['id']
        statement = select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
        subscription = self.db.exec(statement).first()
        
        if subscription:
            subscription.status = SubscriptionStatus.CANCELED
            subscription.canceled_at = datetime.utcnow()
            self.db.add(subscription)
            self.db.commit()
        
        return True

    def _handle_payment_succeeded(self, event: Dict[str, Any]) -> bool:
        """Handle successful payment webhook"""
        # Update subscription status if needed
        invoice = event['data']['object']
        if invoice.get('subscription'):
            self.update_subscription_from_stripe(invoice['subscription'])
        return True

    def _handle_payment_failed(self, event: Dict[str, Any]) -> bool:
        """Handle failed payment webhook"""
        # Update subscription status if needed
        invoice = event['data']['object']
        if invoice.get('subscription'):
            self.update_subscription_from_stripe(invoice['subscription'])
        return True
