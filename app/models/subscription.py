import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, String, Text, Boolean, Integer
from sqlmodel import Field, Relationship

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"


class SubscriptionPlan(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM_MONTHLY = "premium_monthly"
    PREMIUM_YEARLY = "premium_yearly"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class Subscription(BaseModel, table=True):
    __tablename__ = "subscriptions"

    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    stripe_subscription_id: Optional[str] = Field(max_length=255, default=None, index=True)
    stripe_customer_id: Optional[str] = Field(max_length=255, default=None, index=True)
    
    # Subscription details
    plan: SubscriptionPlan = Field(sa_type=String(20), default=SubscriptionPlan.FREE, index=True)
    status: SubscriptionStatus = Field(sa_type=String(20), default=SubscriptionStatus.INACTIVE, index=True)
    
    # Pricing
    price_id: Optional[str] = Field(max_length=255, default=None)
    amount: Optional[int] = Field(default=None)  # Amount in cents
    currency: str = Field(max_length=3, default="usd")
    
    # Dates
    current_period_start: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    current_period_end: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    trial_start: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    trial_end: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    canceled_at: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    
    # Billing
    cancel_at_period_end: bool = Field(default=False)
    billing_cycle_anchor: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_type=DateTime(timezone=True)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_type=DateTime(timezone=True)
    )
    
    # Relationships
    user: "User" = Relationship(back_populates="subscriptions")
    payments: List["SubscriptionPayment"] = Relationship(
        back_populates="subscription",
        sa_relationship_kwargs={"lazy": "dynamic", "cascade": "all, delete-orphan"},
    )

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan='{self.plan}', status='{self.status}', amount=${self.amount})>"


class SubscriptionPayment(BaseModel, table=True):
    __tablename__ = "subscription_payments"

    subscription_id: uuid.UUID = Field(foreign_key="subscriptions.id", index=True)
    stripe_payment_intent_id: Optional[str] = Field(max_length=255, default=None, index=True)
    stripe_invoice_id: Optional[str] = Field(max_length=255, default=None, index=True)
    
    # Payment details
    amount: int = Field()  # Amount in cents
    currency: str = Field(max_length=3, default="usd")
    status: PaymentStatus = Field(sa_type=String(20), default=PaymentStatus.PENDING, index=True)
    
    # Dates
    paid_at: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    failed_at: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    
    # Metadata
    description: Optional[str] = Field(max_length=500, default=None)
    receipt_url: Optional[str] = Field(max_length=500, default=None)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_type=DateTime(timezone=True)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_type=DateTime(timezone=True)
    )
    
    # Relationships
    subscription: "Subscription" = Relationship(back_populates="payments")

    def __repr__(self):
        return f"<SubscriptionPayment(id={self.id}, subscription_id={self.subscription_id}, amount={self.amount}, status='{self.status}')>"


class StripeWebhookEvent(BaseModel, table=True):
    __tablename__ = "stripe_webhook_events"

    stripe_event_id: str = Field(max_length=255, unique=True, index=True)
    event_type: str = Field(max_length=100, index=True)
    processed: bool = Field(default=False, index=True)
    
    # Event data
    data: Optional[str] = Field(sa_type=Text, default=None)  # JSON data
    processed_at: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    error_message: Optional[str] = Field(max_length=1000, default=None)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_type=DateTime(timezone=True)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_type=DateTime(timezone=True)
    )

    def __repr__(self):
        return f"<StripeWebhookEvent(id={self.id}, event_type='{self.event_type}', processed={self.processed})>"
