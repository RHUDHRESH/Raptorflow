"""
Payments Domain - Models
Payment and subscription models
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    """Payment status"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"


class Payment(BaseModel):
    """Payment model"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    workspace_id: str
    merchant_order_id: str
    phonepe_transaction_id: Optional[str] = None
    amount: int  # in paise
    currency: str = "INR"
    status: PaymentStatus = PaymentStatus.PENDING
    plan: str
    customer_email: str
    customer_name: Optional[str] = None
    payment_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None


class Subscription(BaseModel):
    """Subscription model"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    workspace_id: str
    payment_id: str
    plan: str
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    amount: int
    currency: str = "INR"
    interval: str = "month"  # month, year
    current_period_start: datetime = Field(default_factory=datetime.utcnow)
    current_period_end: datetime
    cancel_at_period_end: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Refund(BaseModel):
    """Refund model"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    payment_id: str
    workspace_id: str
    amount: int
    currency: str = "INR"
    reason: Optional[str] = None
    status: str = "pending"  # pending, processed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
