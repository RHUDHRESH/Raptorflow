"""
Pydantic models for Payment and Subscription management.
Supports PhonePe payment gateway integration.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any, List
from uuid import UUID
from datetime import datetime


class PhonePePaymentRequest(BaseModel):
    """Request model for initiating a PhonePe payment."""
    plan: Literal["ascent", "glide", "soar"]
    billing_period: Literal["monthly", "yearly"] = "monthly"
    user_id: UUID
    workspace_id: UUID
    redirect_url: str = Field(..., description="URL to redirect after payment")
    callback_url: str = Field(..., description="URL for payment webhook")


class PhonePePaymentResponse(BaseModel):
    """Response model for PhonePe payment initiation."""
    transaction_id: str
    merchant_transaction_id: str
    payment_url: str
    amount: int  # Amount in paise (smallest currency unit)
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PaymentStatus(BaseModel):
    """Payment status check response."""
    transaction_id: str
    merchant_transaction_id: str
    status: Literal["pending", "success", "failed", "cancelled"]
    amount: int
    payment_method: Optional[str] = None
    response_code: Optional[str] = None
    response_message: Optional[str] = None
    transaction_time: Optional[datetime] = None


class SubscriptionPlan(BaseModel):
    """Subscription plan details."""
    plan_id: str
    name: Literal["ascent", "glide", "soar"]
    price_monthly: int  # In rupees
    price_yearly: int  # In rupees
    features: Dict[str, Any]
    limits: Dict[str, int]

    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "plan_ascent_monthly",
                "name": "ascent",
                "price_monthly": 2499,
                "price_yearly": 24999,
                "features": {
                    "cohorts": 3,
                    "moves": 1,
                    "analytics": True,
                    "integrations": ["linkedin", "twitter"]
                },
                "limits": {
                    "cohorts": 3,
                    "moves_per_month": 1
                }
            }
        }


class Subscription(BaseModel):
    """User subscription model."""
    id: Optional[UUID] = None
    user_id: UUID
    workspace_id: UUID
    plan: Literal["free", "ascent", "glide", "soar"] = "free"
    status: Literal["active", "inactive", "cancelled", "expired", "trial"] = "active"

    # Payment Gateway Details
    phonepe_customer_id: Optional[str] = None
    phonepe_subscription_id: Optional[str] = None
    phonepe_transaction_id: Optional[str] = None

    # Billing
    billing_period: Literal["monthly", "yearly"] = "monthly"
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None

    # Trial
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None


class PaymentWebhook(BaseModel):
    """PhonePe webhook payload."""
    merchant_id: str
    merchant_transaction_id: str
    transaction_id: str
    amount: int
    state: str  # SUCCESS, FAILED, PENDING
    response_code: str
    payment_instrument: Optional[Dict[str, Any]] = None
    provider_reference_id: Optional[str] = None


class CreateCheckoutRequest(BaseModel):
    """Request to create a checkout session."""
    plan: Literal["ascent", "glide", "soar"]
    billing_period: Literal["monthly", "yearly"] = "monthly"
    success_url: str
    cancel_url: str


class CreateCheckoutResponse(BaseModel):
    """Response from creating a checkout session."""
    checkout_url: str
    session_id: str
    expires_at: datetime


class SubscriptionChangeRequest(BaseModel):
    """Request to change subscription plan."""
    new_plan: Literal["ascent", "glide", "soar"]
    billing_period: Literal["monthly", "yearly"] = "monthly"
    immediate: bool = Field(
        default=False,
        description="If True, change immediately. If False, change at period end"
    )


class BillingHistory(BaseModel):
    """Billing history record."""
    id: Optional[UUID] = None
    user_id: UUID
    workspace_id: UUID
    transaction_id: str
    amount: int
    currency: str = "INR"
    status: Literal["pending", "success", "failed", "refunded"]
    plan: str
    billing_period: str
    payment_method: Optional[str] = None
    invoice_url: Optional[str] = None
    created_at: Optional[datetime] = None


class CancelSubscriptionRequest(BaseModel):
    """Request to cancel subscription."""
    reason: Optional[str] = None
    immediate: bool = Field(
        default=False,
        description="If True, cancel immediately. If False, cancel at period end"
    )


class PlanLimits(BaseModel):
    """Plan limits and usage."""
    plan: Literal["free", "ascent", "glide", "soar"]
    limits: Dict[str, int]
    current_usage: Dict[str, int]
    is_limit_reached: bool = False
    upgrade_required: bool = False
    recommended_plan: Optional[str] = None


# ========================================
# Autopay Models (Recurring Payments)
# ========================================

class AutopaySubscriptionRequest(BaseModel):
    """Request model for creating an autopay subscription."""
    plan: Literal["ascent", "glide", "soar"]
    billing_period: Literal["monthly", "yearly"] = "monthly"
    user_id: UUID
    workspace_id: UUID
    mobile_number: str = Field(..., description="Customer mobile number (required for autopay)")
    redirect_url: str = Field(..., description="URL to redirect after authorization")
    callback_url: str = Field(..., description="URL for autopay webhook notifications")


class AutopaySubscriptionResponse(BaseModel):
    """Response model for autopay subscription creation."""
    subscription_id: str
    merchant_subscription_id: str
    authorization_url: str  # URL to authorize the autopay mandate
    amount: int  # Amount in paise
    status: str
    start_date: datetime
    end_date: datetime
    billing_frequency: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AutopaySubscriptionStatus(BaseModel):
    """Autopay subscription status check response."""
    subscription_id: str
    merchant_subscription_id: str
    status: Literal["pending", "active", "paused", "cancelled", "expired", "unknown"]
    amount: int
    start_date: datetime
    end_date: datetime
    billing_frequency: str
    next_billing_date: Optional[datetime] = None
    total_payments: int = 0
    successful_payments: int = 0
    failed_payments: int = 0


class AutopayWebhook(BaseModel):
    """PhonePe Autopay webhook payload."""
    merchant_subscription_id: str
    subscription_id: str
    event_type: str  # SUBSCRIPTION_ACTIVATED, PAYMENT_SUCCESS, PAYMENT_FAILED, etc.
    payment_id: Optional[str] = None
    amount: Optional[int] = None
    status: str
    timestamp: datetime


class CreateAutopayCheckoutRequest(BaseModel):
    """Request to create an autopay checkout session."""
    plan: Literal["ascent", "glide", "soar"]
    billing_period: Literal["monthly", "yearly"] = "monthly"
    mobile_number: str = Field(..., description="Customer mobile number")
    success_url: str
    cancel_url: str


class CreateAutopayCheckoutResponse(BaseModel):
    """Response from creating an autopay checkout session."""
    authorization_url: str
    subscription_id: str
    merchant_subscription_id: str
    expires_at: datetime


class CancelAutopayRequest(BaseModel):
    """Request to cancel autopay subscription."""
    merchant_subscription_id: str
    reason: Optional[str] = None


class PauseAutopayRequest(BaseModel):
    """Request to pause autopay subscription."""
    merchant_subscription_id: str
    reason: Optional[str] = None


class ResumeAutopayRequest(BaseModel):
    """Request to resume paused autopay subscription."""
    merchant_subscription_id: str
