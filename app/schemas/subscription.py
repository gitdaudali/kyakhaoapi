from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from sqlmodel import SQLModel

from app.models.subscription import (
    SubscriptionStatus,
    SubscriptionPlan,
    PaymentStatus,
)


# Base schemas
class SubscriptionBase(SQLModel):
    plan: SubscriptionPlan
    status: SubscriptionStatus
    price_id: Optional[str] = None
    amount: Optional[int] = None
    currency: str = "usd"
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    cancel_at_period_end: bool = False


class SubscriptionCreate(SQLModel):
    plan: SubscriptionPlan
    price_id: str
    stripe_customer_id: Optional[str] = None


class SubscriptionUpdate(SQLModel):
    plan: Optional[SubscriptionPlan] = None
    status: Optional[SubscriptionStatus] = None
    price_id: Optional[str] = None
    amount: Optional[int] = None
    currency: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    cancel_at_period_end: Optional[bool] = None


class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    billing_cycle_anchor: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionPaymentBase(SQLModel):
    amount: int
    currency: str = "usd"
    status: PaymentStatus
    paid_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    description: Optional[str] = None
    receipt_url: Optional[str] = None


class SubscriptionPaymentResponse(SubscriptionPaymentBase):
    id: int
    subscription_id: int
    stripe_payment_intent_id: Optional[str] = None
    stripe_invoice_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionWithPayments(SubscriptionResponse):
    payments: List[SubscriptionPaymentResponse] = []


# Stripe-specific schemas
class StripeCheckoutSessionCreate(SQLModel):
    price_id: str
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class StripeCheckoutSessionResponse(SQLModel):
    session_id: str
    session_url: str
    customer_id: Optional[str] = None


class StripeCustomerCreate(SQLModel):
    email: str
    name: Optional[str] = None


class StripeCustomerResponse(SQLModel):
    id: str
    email: str
    name: Optional[str] = None
    created: int


# Webhook schemas
class WebhookEventBase(SQLModel):
    event_type: str
    processed: bool = False


class WebhookEventCreate(WebhookEventBase):
    stripe_event_id: str
    data: Optional[str] = None


class WebhookEventResponse(WebhookEventBase):
    id: int
    stripe_event_id: str
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# User subscription info
class UserSubscriptionInfo(SQLModel):
    has_active_subscription: bool
    current_plan: Optional[SubscriptionPlan] = None
    subscription_status: Optional[SubscriptionStatus] = None
    trial_ends_at: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False


# Subscription management
class CancelSubscriptionRequest(SQLModel):
    cancel_at_period_end: bool = True
    reason: Optional[str] = None


class UpdateSubscriptionRequest(SQLModel):
    new_price_id: str
    proration_behavior: str = "create_prorations"  # or "none", "always_invoice"


# Analytics and reporting
class SubscriptionAnalytics(SQLModel):
    total_subscriptions: int
    active_subscriptions: int
    canceled_subscriptions: int
    trial_subscriptions: int
    total_revenue: int  # in cents
    monthly_revenue: int  # in cents
    churn_rate: float  # percentage


class SubscriptionStats(SQLModel):
    plan_distribution: dict[str, int]
    status_distribution: dict[str, int]
    revenue_by_plan: dict[str, int]
    average_subscription_value: float
