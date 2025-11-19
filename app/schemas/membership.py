"""Schemas for membership, subscription, and payment."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.membership import BillingCycle, PaymentStatus, SubscriptionStatus


class MembershipPlanOut(BaseModel):
    """Membership plan output schema."""

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    price: float
    currency: str
    billing_cycle: BillingCycle
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MembershipSubscribeRequest(BaseModel):
    """Unified request schema for membership subscription (card details + terms)."""

    card_number: str = Field(..., min_length=13, max_length=19)
    exp_month: int = Field(..., ge=1, le=12)
    exp_year: int = Field(..., ge=2024)
    cvv: str = Field(..., min_length=3, max_length=4)
    name_on_card: str = Field(..., min_length=1, max_length=100)
    terms_accepted: bool = Field(..., description="User must accept terms and conditions")


class SubscriptionOut(BaseModel):
    """Subscription output schema."""

    id: uuid.UUID
    user_id: uuid.UUID
    plan_id: uuid.UUID
    status: SubscriptionStatus
    start_date: datetime
    renewal_date: datetime
    end_date: Optional[datetime] = None
    plan: Optional[MembershipPlanOut] = None

    class Config:
        from_attributes = True


class PaymentOut(BaseModel):
    """Payment output schema."""

    id: uuid.UUID
    subscription_id: uuid.UUID
    amount: float
    status: PaymentStatus
    transaction_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentListResponse(BaseModel):
    """Payment list response schema."""

    payments: list[PaymentOut]
    total: int


class InvoiceOut(BaseModel):
    """Invoice output schema."""

    invoice_id: str
    payment_id: uuid.UUID
    subscription_id: uuid.UUID
    amount: float
    currency: str
    status: PaymentStatus
    transaction_id: Optional[str] = None
    invoice_date: datetime
    plan_name: str
    billing_period: str

    class Config:
        from_attributes = True


class SubscriptionListResponse(BaseModel):
    """Subscription list response schema."""

    subscriptions: list[SubscriptionOut]
    total: int


class ChangePlanRequest(BaseModel):
    """Request schema for changing subscription plan."""

    new_plan_id: uuid.UUID
    terms_accepted: bool = Field(..., description="User must accept terms and conditions")


