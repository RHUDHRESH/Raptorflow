"""
Webhook models for Redis-based webhook handling.

Provides data structures for webhook events, delivery tracking,
and webhook endpoint management.
"""

import hashlib
import hmac
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class WebhookStatus(Enum):
    """Webhook status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISABLED = "disabled"
    PENDING = "pending"
    FAILED = "failed"


class WebhookEventType(Enum):
    """Webhook event type enumeration."""
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    SESSION_CREATED = "session.created"
    SESSION_UPDATED = "session.updated"
    SESSION_DELETED = "session.deleted"
    USAGE_RECORDED = "usage.recorded"
    USAGE_LIMIT_REACHED = "usage.limit_reached"
    BUDGET_EXCEEDED = "budget.exceeded"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    QUEUE_JOB_CREATED = "queue.job_created"
    QUEUE_JOB_COMPLETED = "queue.job_completed"
    QUEUE_JOB_FAILED = "queue.job_failed"
    SYSTEM_ALERT = "system.alert"
    SYSTEM_ERROR = "system.error"
    CUSTOM = "custom"


class WebhookDeliveryStatus(Enum):
    """Webhook delivery status enumeration."""
    PENDING = "pending"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"


class WebhookRetryPolicy(Enum):
    """Webhook retry policy enumeration."""
    NONE = "none"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIXED = "fixed"


@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration."""
    endpoint_id: str
    workspace_id: str
    url: str
    secret: str
    events: List[WebhookEventType]
    status: WebhookStatus = WebhookStatus.ACTIVE

    # Configuration
    timeout_seconds: int = 30
    retry_policy: WebhookRetryPolicy = WebhookRetryPolicy.EXPONENTIAL
    max_retries: int = 3
    retry_delay_seconds: int = 60

    # Security
    signature_algorithm: str = "sha256"
    signature_header: str = os.getenv('STR')

    # Filtering
    filters: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_delivery_at: Optional[datetime] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.status, str):
            self.status = WebhookStatus(self.status)
        if isinstance(self.retry_policy, str):
            self.retry_policy = WebhookRetryPolicy(self.retry_policy)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
        if isinstance(self.last_delivery_at, str):
            self.last_delivery_at = datetime.fromisoformat(self.last_delivery_at)

        # Convert event strings to enums
        if self.events and isinstance(self.events[0], str):
            self.events = [WebhookEventType(event) for event in self.events]

    def is_active(self) -> bool:
        """Check if webhook is active."""
        return self.status == WebhookStatus.ACTIVE

    def should_deliver_event(self, event_type: WebhookEventType, payload: Dict[str, Any]) -> bool:
        """Check if webhook should deliver this event."""
        if not self.is_active():
            return False

        # Check event type
        if event_type not in self.events:
            return False

        # Apply filters
        if self.filters:
            for filter_key, filter_value in self.filters.items():
                if filter_key in payload:
                    if isinstance(filter_value, list):
                        if payload[filter_key] not in filter_value:
                            return False
                    elif payload[filter_key] != filter_value:
                        return False

        return True

    def generate_signature(self, payload: str) -> str:
        """Generate webhook signature."""
        return hmac.new(
            self.secret.encode(),
            payload.encode(),
            getattr(hashlib, self.signature_algorithm)
        ).hexdigest()

    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature."""
        expected_signature = self.generate_signature(payload)
        return hmac.compare_digest(expected_signature, signature)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enums to strings
        data["status"] = self.status.value
        data["retry_policy"] = self.retry_policy.value
        data["events"] = [event.value for event in self.events]

        # Convert datetime objects
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        if self.last_delivery_at:
            data["last_delivery_at"] = self.last_delivery_at.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebhookEndpoint":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class WebhookEvent:
    """Webhook event data."""
    event_id: str
    event_type: WebhookEventType
    workspace_id: str
    payload: Dict[str, Any]

    # Event metadata
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "system"
    version: str = "1.0"

    # Delivery tracking
    delivered: bool = False
    delivery_attempts: int = 0
    last_delivery_attempt: Optional[datetime] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.event_type, str):
            self.event_type = WebhookEventType(self.event_type)
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if isinstance(self.last_delivery_attempt, str):
            self.last_delivery_attempt = datetime.fromisoformat(self.last_delivery_attempt)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enum to string
        data["event_type"] = self.event_type.value

        # Convert datetime objects
        data["timestamp"] = self.timestamp.isoformat()
        if self.last_delivery_attempt:
            data["last_delivery_attempt"] = self.last_delivery_attempt.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebhookEvent":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class WebhookDelivery:
    """Webhook delivery tracking."""
    delivery_id: str
    webhook_id: str
    event_id: str
    endpoint_id: str
    status: WebhookDeliveryStatus

    # Delivery details
    url: str
    method: str = "POST"
    headers: Dict[str, str] = field(default_factory=dict)
    payload: str = ""

    # Response details
    response_status_code: Optional[int] = None
    response_body: Optional[str] = None
    response_headers: Dict[str, str] = field(default_factory=dict)

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

    # Retry tracking
    attempt_number: int = 1
    max_retries: int = 3
    next_retry_at: Optional[datetime] = None

    # Error details
    error_message: Optional[str] = None
    error_type: Optional[str] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.status, str):
            self.status = WebhookDeliveryStatus(self.status)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.sent_at, str):
            self.sent_at = datetime.fromisoformat(self.sent_at)
        if isinstance(self.completed_at, str):
            self.completed_at = datetime.fromisoformat(self.completed_at)
        if isinstance(self.next_retry_at, str):
            self.next_retry_at = datetime.fromisoformat(self.next_retry_at)

    def is_successful(self) -> bool:
        """Check if delivery was successful."""
        return self.status == WebhookDeliveryStatus.DELIVERED

    def is_failed(self) -> bool:
        """Check if delivery failed."""
        return self.status in [WebhookDeliveryStatus.FAILED, WebhookDeliveryStatus.EXPIRED]

    def can_retry(self) -> bool:
        """Check if delivery can be retried."""
        return (
            self.is_failed() and
            self.attempt_number < self.max_retries and
            self.next_retry_at and
            self.next_retry_at <= datetime.now()
        )

    def calculate_retry_delay(self, policy: WebhookRetryPolicy) -> int:
        """Calculate retry delay in seconds."""
        if policy == WebhookRetryPolicy.NONE:
            return 0
        elif policy == WebhookRetryPolicy.FIXED:
            return 60  # Fixed 1 minute
        elif policy == WebhookRetryPolicy.LINEAR:
            return self.attempt_number * 60  # Linear: 1min, 2min, 3min...
        elif policy == WebhookRetryPolicy.EXPONENTIAL:
            return min(60 * (2 ** (self.attempt_number - 1)), 3600)  # Exponential: 1min, 2min, 4min, max 1hour

        return 60

    def mark_sent(self):
        """Mark delivery as sent."""
        self.status = WebhookDeliveryStatus.SENDING
        self.sent_at = datetime.now()

    def mark_completed(self, status_code: int, response_body: str = "", response_headers: Dict[str, str] = None):
        """Mark delivery as completed."""
        self.status = WebhookDeliveryStatus.DELIVERED
        self.completed_at = datetime.now()
        self.response_status_code = status_code
        self.response_body = response_body
        if response_headers:
            self.response_headers = response_headers

        if self.sent_at:
            self.duration_ms = int((self.completed_at - self.sent_at).total_seconds() * 1000)

    def mark_failed(self, error_message: str, error_type: str = "unknown"):
        """Mark delivery as failed."""
        self.status = WebhookDeliveryStatus.FAILED
        self.error_message = error_message
        self.error_type = error_type
        self.completed_at = datetime.now()

        if self.sent_at:
            self.duration_ms = int((self.completed_at - self.sent_at).total_seconds() * 1000)

    def schedule_retry(self, policy: WebhookRetryPolicy):
        """Schedule next retry."""
        if self.attempt_number < self.max_retries:
            self.status = WebhookDeliveryStatus.RETRYING
            self.attempt_number += 1

            delay_seconds = self.calculate_retry_delay(policy)
            self.next_retry_at = datetime.now() + timedelta(seconds=delay_seconds)
        else:
            self.status = WebhookDeliveryStatus.EXPIRED
            self.next_retry_at = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enum to string
        data["status"] = self.status.value

        # Convert datetime objects
        data["created_at"] = self.created_at.isoformat()
        if self.sent_at:
            data["sent_at"] = self.sent_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
        if self.next_retry_at:
            data["next_retry_at"] = self.next_retry_at.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebhookDelivery":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class WebhookStats:
    """Webhook statistics."""
    webhook_id: str
    endpoint_id: str
    workspace_id: str

    # Delivery statistics
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    pending_deliveries: int = 0

    # Performance metrics
    avg_response_time_ms: float = 0.0
    success_rate: float = 0.0
    throughput_per_hour: float = 0.0

    # Error statistics
    error_types: Dict[str, int] = field(default_factory=dict)

    # Time range
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.period_start, str):
            self.period_start = datetime.fromisoformat(self.period_start)
        if isinstance(self.period_end, str):
            self.period_end = datetime.fromisoformat(self.period_end)

        self._calculate_metrics()

    def _calculate_metrics(self):
        """Calculate derived metrics."""
        total = self.total_deliveries
        if total > 0:
            self.success_rate = (self.successful_deliveries / total) * 100

        # Calculate throughput (deliveries per hour)
        if self.period_end > self.period_start:
            hours = (self.period_end - self.period_start).total_seconds() / 3600
            if hours > 0:
                self.throughput_per_hour = self.total_deliveries / hours

    def record_delivery(self, delivery: WebhookDelivery):
        """Record a delivery attempt."""
        self.total_deliveries += 1

        if delivery.is_successful():
            self.successful_deliveries += 1
        elif delivery.is_failed():
            self.failed_deliveries += 1

            # Track error types
            if delivery.error_type:
                self.error_types[delivery.error_type] = self.error_types.get(delivery.error_type, 0) + 1
        else:
            self.pending_deliveries += 1

        # Update average response time
        if delivery.duration_ms is not None:
            total_time = self.avg_response_time_ms * (self.total_deliveries - 1) + delivery.duration_ms
            self.avg_response_time_ms = total_time / self.total_deliveries

        # Update period end
        self.period_end = datetime.now()
        self._calculate_metrics()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert datetime objects
        data["period_start"] = self.period_start.isoformat()
        data["period_end"] = self.period_end.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebhookStats":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class WebhookBatch:
    """Batch webhook delivery."""
    batch_id: str
    webhook_id: str
    endpoint_id: str
    events: List[WebhookEvent]

    # Batch configuration
    max_events_per_batch: int = 100
    batch_timeout_seconds: int = 30

    # Batch status
    status: WebhookDeliveryStatus = WebhookDeliveryStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Delivery tracking
    delivery_id: Optional[str] = None
    response_status_code: Optional[int] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.status, str):
            self.status = WebhookDeliveryStatus(self.status)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.sent_at, str):
            self.sent_at = datetime.fromisoformat(self.sent_at)
        if isinstance(self.completed_at, str):
            self.completed_at = datetime.fromisoformat(self.completed_at)

    def is_ready(self) -> bool:
        """Check if batch is ready to send."""
        return (
            self.status == WebhookDeliveryStatus.PENDING and
            (len(self.events) >= self.max_events_per_batch or
             (datetime.now() - self.created_at).total_seconds() >= self.batch_timeout_seconds))
        )

    def get_payload(self) -> str:
        """Get batch payload as JSON string."""
        batch_data = {
            "batch_id": self.batch_id,
            "webhook_id": self.webhook_id,
            "created_at": self.created_at.isoformat(),
            "events": [event.to_dict() for event in self.events]
        }
        return json.dumps(batch_data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enum to string
        data["status"] = self.status.value

        # Convert datetime objects
        data["created_at"] = self.created_at.isoformat()
        if self.sent_at:
            data["sent_at"] = self.sent_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()

        # Convert events
        data["events"] = [event.to_dict() for event in self.events]

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebhookBatch":
        """Create from dictionary."""
        # Convert events
        if "events" in data:
            events = [WebhookEvent.from_dict(event_data) for event_data in data["events"]]
            data["events"] = events

        return cls(**data)
