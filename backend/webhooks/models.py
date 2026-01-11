"""
Webhook models for Raptorflow.

Defines data structures for webhook events, responses,
configurations, and verification.
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class WebhookEventType(Enum):
    """Webhook event types."""

    # Supabase events
    SUPABASE_USER_CREATED = "supabase.user.created"
    SUPABASE_USER_UPDATED = "supabase.user.updated"
    SUPABASE_USER_DELETED = "supabase.user.deleted"
    SUPABASE_AUTH_LOGIN = "supabase.auth.login"
    SUPABASE_AUTH_LOGOUT = "supabase.auth.logout"

    # Stripe events
    STRIPE_PAYMENT_INTENT_SUCCEEDED = "stripe.payment_intent.succeeded"
    STRIPE_PAYMENT_INTENT_FAILED = "stripe.payment_intent.failed"
    STRIPE_INVOICE_CREATED = "stripe.invoice.created"
    STRIPE_INVOICE_PAYMENT_SUCCEEDED = "stripe.invoice.payment_succeeded"
    STRIPE_SUBSCRIPTION_CREATED = "stripe.subscription.created"
    STRIPE_SUBSCRIPTION_UPDATED = "stripe.subscription.updated"
    STRIPE_SUBSCRIPTION_DELETED = "stripe.subscription.deleted"

    # PhonePe events
    PHONEPE_PAYMENT_INITIATED = "phonepe.payment.initiated"
    PHONEPE_PAYMENT_SUCCESS = "phonepe.payment.success"
    PHONEPE_PAYMENT_FAILED = "phonepe.payment.failed"
    PHONEPE_REFUND_PROCESSED = "phonepe.refund.processed"


class WebhookStatus(Enum):
    """Webhook processing status."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    TIMEOUT = "TIMEOUT"


class DeliveryStatus(Enum):
    """Webhook delivery status."""

    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    RETRY = "RETRY"
    TIMEOUT = "TIMEOUT"


@dataclass
class WebhookRetryConfig:
    """Webhook retry configuration."""

    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    strategy: str = "exponential"  # exponential, linear, fixed
    backoff_multiplier: float = 2.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "max_retries": self.max_retries,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay,
            "strategy": self.strategy,
            "backoff_multiplier": self.backoff_multiplier,
        }


@dataclass
class WebhookConfig:
    """Webhook configuration."""

    source: str
    secret_key: str
    enabled: bool = True
    retry_config: Optional[WebhookRetryConfig] = None
    timeout_seconds: int = 30
    allowed_ips: List[str] = field(default_factory=list)
    rate_limit_per_minute: int = 100
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        if self.retry_config is None:
            self.retry_config = WebhookRetryConfig()

        if self.allowed_ips is None:
            self.allowed_ips = []

        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "enabled": self.enabled,
            "retry_config": self.retry_config.to_dict() if self.retry_config else None,
            "timeout_seconds": self.timeout_seconds,
            "allowed_ips": self.allowed_ips,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class WebhookEvent:
    """Webhook event data."""

    event_id: str
    source: str
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    headers: Dict[str, str]
    processed: bool = False
    status: WebhookStatus = WebhookStatus.PENDING
    error: Optional[str] = None
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.status, str):
            self.status = WebhookStatus(self.status)

        if self.data is None:
            self.data = {}

        if self.headers is None:
            self.headers = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "source": self.source,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "headers": self.headers,
            "processed": self.processed,
            "status": self.status.value,
            "error": self.error,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def mark_processed(self):
        """Mark event as processed."""
        self.processed = True
        self.status = WebhookStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error: str):
        """Mark event as failed."""
        self.processed = False
        self.status = WebhookStatus.FAILED
        self.error = error
        self.updated_at = datetime.utcnow()

    def increment_retry(self):
        """Increment retry count."""
        self.retry_count += 1
        self.status = WebhookStatus.RETRYING
        self.updated_at = datetime.utcnow()

    def can_retry(self, max_retries: int) -> bool:
        """Check if event can be retried."""
        return self.retry_count < max_retries and self.status in [
            WebhookStatus.FAILED,
            WebhookStatus.TIMEOUT,
        ]


@dataclass
class WebhookResponse:
    """Webhook response data."""

    status_code: int
    body: Union[str, Dict[str, Any]]
    headers: Dict[str, str]
    processing_time_ms: Optional[float] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if self.body is None:
            self.body = {}

        if isinstance(self.body, dict):
            self.body = json.dumps(self.body)

        if self.headers is None:
            self.headers = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status_code": self.status_code,
            "body": self.body,
            "headers": self.headers,
            "processing_time_ms": self.processing_time_ms,
        }

    def is_success(self) -> bool:
        """Check if response indicates success."""
        return 200 <= self.status_code < 300

    def is_error(self) -> bool:
        """Check if response indicates error."""
        return self.status_code >= 400


@dataclass
class WebhookSignature:
    """Webhook signature information."""

    source: str
    signature: str
    timestamp: Optional[int] = None
    algorithm: str = "HMAC-SHA256"
    version: str = "v1"

    def __post_init__(self):
        """Post-initialization processing."""
        if self.signature is None:
            self.signature = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "signature": self.signature,
            "timestamp": self.timestamp,
            "algorithm": self.algorithm,
            "version": self.version,
        }

    def is_expired(self, max_age_seconds: int = 300) -> bool:
        """Check if signature is expired."""
        if self.timestamp is None:
            return False

        current_time = int(datetime.utcnow().timestamp())
        return (current_time - self.timestamp) > max_age_seconds


@dataclass
class WebhookDelivery:
    """Webhook delivery tracking."""

    delivery_id: str
    event_id: str
    webhook_url: str
    status: DeliveryStatus
    attempt_count: int = 1
    max_attempts: int = 3
    next_retry_at: Optional[datetime] = None
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.status, str):
            self.status = DeliveryStatus(self.status)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "delivery_id": self.delivery_id,
            "event_id": self.event_id,
            "webhook_url": self.webhook_url,
            "status": self.status.value,
            "attempt_count": self.attempt_count,
            "max_attempts": self.max_attempts,
            "next_retry_at": (
                self.next_retry_at.isoformat() if self.next_retry_at else None
            ),
            "response_code": self.response_code,
            "response_body": self.response_body,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "delivered_at": (
                self.delivered_at.isoformat() if self.delivered_at else None
            ),
        }

    def mark_delivered(self, response_code: int, response_body: str):
        """Mark delivery as successful."""
        self.status = DeliveryStatus.DELIVERED
        self.response_code = response_code
        self.response_body = response_body
        self.delivered_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error_message: str, response_code: Optional[int] = None):
        """Mark delivery as failed."""
        self.status = DeliveryStatus.FAILED
        self.error_message = error_message
        self.response_code = response_code
        self.updated_at = datetime.utcnow()

    def schedule_retry(self, delay_seconds: float):
        """Schedule retry for delivery."""
        self.status = DeliveryStatus.RETRY
        self.attempt_count += 1
        self.next_retry_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
        self.updated_at = datetime.utcnow()

    def can_retry(self) -> bool:
        """Check if delivery can be retried."""
        return self.attempt_count < self.max_attempts and self.status in [
            DeliveryStatus.FAILED,
            DeliveryStatus.TIMEOUT,
        ]

    def is_final(self) -> bool:
        """Check if delivery is in final state."""
        return self.status in [DeliveryStatus.DELIVERED, DeliveryStatus.FAILED]


@dataclass
class WebhookRetry:
    """Webhook retry information."""

    event_id: str
    attempt: int
    scheduled_at: datetime
    max_attempts: int
    delay_seconds: float
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Post-initialization processing."""
        if self.error_message is None:
            self.error_message = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "attempt": self.attempt,
            "scheduled_at": self.scheduled_at.isoformat(),
            "max_attempts": self.max_attempts,
            "delay_seconds": self.delay_seconds,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
        }

    def is_due(self) -> bool:
        """Check if retry is due."""
        return datetime.utcnow() >= self.scheduled_at

    def is_final_attempt(self) -> bool:
        """Check if this is the final attempt."""
        return self.attempt >= self.max_attempts


@dataclass
class WebhookMetrics:
    """Webhook processing metrics."""

    source: str
    total_events: int = 0
    successful_events: int = 0
    failed_events: int = 0
    average_processing_time_ms: float = 0.0
    last_event_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    last_failure_at: Optional[datetime] = None
    error_rate: float = 0.0
    success_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "total_events": self.total_events,
            "successful_events": self.successful_events,
            "failed_events": self.failed_events,
            "average_processing_time_ms": self.average_processing_time_ms,
            "last_event_at": (
                self.last_event_at.isoformat() if self.last_event_at else None
            ),
            "last_success_at": (
                self.last_success_at.isoformat() if self.last_success_at else None
            ),
            "last_failure_at": (
                self.last_failure_at.isoformat() if self.last_failure_at else None
            ),
            "error_rate": self.error_rate,
            "success_rate": self.success_rate,
        }

    def update_success(self, processing_time_ms: float):
        """Update metrics with successful event."""
        self.total_events += 1
        self.successful_events += 1
        self.last_event_at = datetime.utcnow()
        self.last_success_at = datetime.utcnow()

        # Update average processing time
        if self.total_events == 1:
            self.average_processing_time_ms = processing_time_ms
        else:
            self.average_processing_time_ms = (
                self.average_processing_time_ms * (self.total_events - 1)
                + processing_time_ms
            ) / self.total_events

        # Update rates
        self._update_rates()

    def update_failure(self):
        """Update metrics with failed event."""
        self.total_events += 1
        self.failed_events += 1
        self.last_event_at = datetime.utcnow()
        self.last_failure_at = datetime.utcnow()

        # Update rates
        self._update_rates()

    def _update_rates(self):
        """Update success and error rates."""
        if self.total_events > 0:
            self.success_rate = (self.successful_events / self.total_events) * 100
            self.error_rate = (self.failed_events / self.total_events) * 100


# Utility functions
def create_webhook_event(
    source: str,
    event_type: str,
    data: Dict[str, Any],
    headers: Dict[str, str],
    event_id: Optional[str] = None,
) -> WebhookEvent:
    """Create a webhook event."""
    if event_id is None:
        import uuid

        event_id = str(uuid.uuid4())

    return WebhookEvent(
        event_id=event_id,
        source=source,
        event_type=event_type,
        data=data,
        timestamp=datetime.utcnow(),
        headers=headers,
    )


def create_webhook_response(
    status_code: int,
    body: Union[str, Dict[str, Any]],
    headers: Optional[Dict[str, str]] = None,
) -> WebhookResponse:
    """Create a webhook response."""
    return WebhookResponse(status_code=status_code, body=body, headers=headers or {})


def create_webhook_delivery(
    event_id: str, webhook_url: str, max_attempts: int = 3
) -> WebhookDelivery:
    """Create a webhook delivery."""
    import uuid

    return WebhookDelivery(
        delivery_id=str(uuid.uuid4()),
        event_id=event_id,
        webhook_url=webhook_url,
        status=DeliveryStatus.PENDING,
        max_attempts=max_attempts,
    )


def create_webhook_retry(
    event_id: str, attempt: int, delay_seconds: float, max_attempts: int
) -> WebhookRetry:
    """Create a webhook retry."""
    return WebhookRetry(
        event_id=event_id,
        attempt=attempt,
        scheduled_at=datetime.utcnow() + timedelta(seconds=delay_seconds),
        max_attempts=max_attempts,
        delay_seconds=delay_seconds,
    )


def create_webhook_config(
    source: str,
    secret_key: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
    strategy: str = "exponential",
) -> WebhookConfig:
    """Create a webhook configuration."""
    retry_config = WebhookRetryConfig(
        max_retries=max_retries, base_delay=base_delay, strategy=strategy
    )

    return WebhookConfig(
        source=source, secret_key=secret_key, retry_config=retry_config
    )


def create_webhook_metrics(source: str) -> WebhookMetrics:
    """Create webhook metrics."""
    return WebhookMetrics(source=source)


# Serialization helpers
def serialize_webhook_event(event: WebhookEvent) -> str:
    """Serialize webhook event to JSON string."""
    return json.dumps(event.to_dict(), default=str)


def deserialize_webhook_event(data: str) -> WebhookEvent:
    """Deserialize webhook event from JSON string."""
    data_dict = json.loads(data)

    # Parse datetime fields
    if data_dict.get("timestamp"):
        data_dict["timestamp"] = datetime.fromisoformat(data_dict["timestamp"])

    if data_dict.get("created_at"):
        data_dict["created_at"] = datetime.fromisoformat(data_dict["created_at"])

    if data_dict.get("updated_at"):
        data_dict["updated_at"] = datetime.fromisoformat(data_dict["updated_at"])

    return WebhookEvent(**data_dict)


def serialize_webhook_delivery(delivery: WebhookDelivery) -> str:
    """Serialize webhook delivery to JSON string."""
    return json.dumps(delivery.to_dict(), default=str)


def deserialize_webhook_delivery(data: str) -> WebhookDelivery:
    """Deserialize webhook delivery from JSON string."""
    data_dict = json.loads(data)

    # Parse datetime fields
    if data_dict.get("next_retry_at"):
        data_dict["next_retry_at"] = datetime.fromisoformat(data_dict["next_retry_at"])

    if data_dict.get("created_at"):
        data_dict["created_at"] = datetime.fromisoformat(data_dict["created_at"])

    if data_dict.get("updated_at"):
        data_dict["updated_at"] = datetime.fromisoformat(data_dict["updated_at"])

    if data_dict.get("delivered_at"):
        data_dict["delivered_at"] = datetime.fromisoformat(data_dict["delivered_at"])

    return WebhookDelivery(**data_dict)


# Validation functions
def validate_webhook_event(event: WebhookEvent) -> List[str]:
    """Validate webhook event data."""
    errors = []

    if not event.event_id:
        errors.append("Event ID is required")

    if not event.source:
        errors.append("Source is required")

    if not event.event_type:
        errors.append("Event type is required")

    if not event.data:
        errors.append("Event data is required")

    if not event.timestamp:
        errors.append("Timestamp is required")

    return errors


def validate_webhook_config(config: WebhookConfig) -> List[str]:
    """Validate webhook configuration."""
    errors = []

    if not config.source:
        errors.append("Source is required")

    if not config.secret_key:
        errors.append("Secret key is required")

    if config.timeout_seconds <= 0:
        errors.append("Timeout must be positive")

    if config.rate_limit_per_minute <= 0:
        errors.append("Rate limit must be positive")

    if config.retry_config:
        if config.retry_config.max_retries < 0:
            errors.append("Max retries must be non-negative")

        if config.retry_config.base_delay < 0:
            errors.append("Base delay must be non-negative")

        if config.retry_config.max_delay < 0:
            errors.append("Max delay must be non-negative")

        if config.retry_config.strategy not in ["exponential", "linear", "fixed"]:
            errors.append("Invalid retry strategy")

    return errors


# Status transition helpers
def can_transition_webhook_status(
    from_status: WebhookStatus, to_status: WebhookStatus
) -> bool:
    """Check if webhook status transition is valid."""
    valid_transitions = {
        WebhookStatus.PENDING: [WebhookStatus.PROCESSING, WebhookStatus.FAILED],
        WebhookStatus.PROCESSING: [
            WebhookStatus.COMPLETED,
            WebhookStatus.FAILED,
            WebhookStatus.TIMEOUT,
        ],
        WebhookStatus.RETRYING: [WebhookStatus.PROCESSING, WebhookStatus.FAILED],
        WebhookStatus.COMPLETED: [],  # Terminal state
        WebhookStatus.FAILED: [WebhookStatus.RETRYING],  # Can retry
        WebhookStatus.TIMEOUT: [WebhookStatus.RETRYING],  # Can retry
    }

    return to_status in valid_transitions.get(from_status, [])


def can_transition_delivery_status(
    from_status: DeliveryStatus, to_status: DeliveryStatus
) -> bool:
    """Check if delivery status transition is valid."""
    valid_transitions = {
        DeliveryStatus.PENDING: [DeliveryStatus.SENT, DeliveryStatus.FAILED],
        DeliveryStatus.SENT: [
            DeliveryStatus.DELIVERED,
            DeliveryStatus.FAILED,
            DeliveryStatus.TIMEOUT,
        ],
        DeliveryStatus.RETRY: [DeliveryStatus.SENT, DeliveryStatus.FAILED],
        DeliveryStatus.DELIVERED: [],  # Terminal state
        DeliveryStatus.FAILED: [DeliveryStatus.RETRY],  # Can retry
        DeliveryStatus.TIMEOUT: [DeliveryStatus.RETRY],  # Can retry
    }

    return to_status in valid_transitions.get(from_status, [])


# Constants
DEFAULT_WEBHOOK_TIMEOUT = 30  # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0  # seconds
DEFAULT_MAX_DELAY = 60.0  # seconds
DEFAULT_RATE_LIMIT = 100  # per minute
SIGNATURE_MAX_AGE = 300  # 5 minutes

# Export all classes and functions
__all__ = [
    "WebhookEventType",
    "WebhookStatus",
    "DeliveryStatus",
    "WebhookRetryConfig",
    "WebhookConfig",
    "WebhookEvent",
    "WebhookResponse",
    "WebhookSignature",
    "WebhookDelivery",
    "WebhookRetry",
    "WebhookMetrics",
    "create_webhook_event",
    "create_webhook_response",
    "create_webhook_delivery",
    "create_webhook_retry",
    "create_webhook_config",
    "create_webhook_metrics",
    "serialize_webhook_event",
    "deserialize_webhook_event",
    "serialize_webhook_delivery",
    "deserialize_webhook_delivery",
    "validate_webhook_event",
    "validate_webhook_config",
    "can_transition_webhook_status",
    "can_transition_delivery_status",
    "DEFAULT_WEBHOOK_TIMEOUT",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_BASE_DELAY",
    "DEFAULT_MAX_DELAY",
    "DEFAULT_RATE_LIMIT",
    "SIGNATURE_MAX_AGE",
]
