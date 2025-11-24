"""Membership models for subscription and payment management."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field

from app.models.base import BaseModel, TimestampMixin


class BillingCycle(str, Enum):
    """Billing cycle enumeration."""

    MONTHLY = "monthly"
    YEARLY = "yearly"


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration."""

    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class PaymentStatus(str, Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class MembershipPlan(BaseModel, TimestampMixin, table=True):
    """Membership plan model."""

    __tablename__ = "membership_plans"

    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None)
    price: float = Field(sa_type=Numeric(10, 2))
    currency: str = Field(max_length=10, default="PKR")
    billing_cycle: BillingCycle = Field(sa_type=String(20), default=BillingCycle.MONTHLY)
    is_active: bool = Field(default=True, index=True)

    # Relationships
    # Note: Relationship removed to avoid SQLModel relationship resolution issues
    # Access subscriptions via plan_id foreign key when needed using queries
    # subscriptions: List["Subscription"] = Relationship(...)  # Commented out due to SQLModel issues

    def __repr__(self):
        return f"<MembershipPlan(id={self.id}, name='{self.name}', price={self.price})>"


class Subscription(BaseModel, TimestampMixin, table=True):
    """Subscription model."""

    __tablename__ = "subscriptions"

    user_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True), foreign_key="users.id", nullable=False, index=True
    )
    plan_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="membership_plans.id",
        nullable=False,
        index=True,
    )
    status: SubscriptionStatus = Field(
        sa_type=String(20), default=SubscriptionStatus.ACTIVE, index=True
    )
    start_date: datetime = Field(
        sa_type=DateTime(timezone=True), default_factory=lambda: datetime.now()
    )
    renewal_date: datetime = Field(sa_type=DateTime(timezone=True))
    end_date: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True), nullable=True
    )
    payment_token: Optional[str] = Field(default=None, max_length=255)

    # Relationships
    # Note: Relationships removed to avoid SQLModel relationship resolution issues
    # Access user via user_id foreign key when needed
    # Access plan via plan_id foreign key when needed
    # plan: "MembershipPlan" = Relationship(...)  # Commented out due to SQLModel issues
    # Note: Relationship removed to avoid SQLModel relationship resolution issues
    # Access payments via subscription_id foreign key when needed using queries
    # payments: List["Payment"] = Relationship(...)  # Commented out due to SQLModel issues

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, status='{self.status}')>"


class Payment(BaseModel, TimestampMixin, table=True):
    """Payment model."""

    __tablename__ = "payments"

    subscription_id: uuid.UUID = Field(
        sa_type=UUID(as_uuid=True),
        foreign_key="subscriptions.id",
        nullable=False,
        index=True,
    )
    amount: float = Field(sa_type=Numeric(10, 2))
    status: PaymentStatus = Field(
        sa_type=String(20), default=PaymentStatus.PENDING, index=True
    )
    transaction_id: Optional[str] = Field(default=None, max_length=255, index=True)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True), default_factory=lambda: datetime.now()
    )

    # Relationships
    # Note: Relationship removed to avoid SQLModel relationship resolution issues
    # Access subscription via subscription_id foreign key when needed using queries
    # subscription: "Subscription" = Relationship(...)  # Commented out due to SQLModel issues

    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status='{self.status}')>"
