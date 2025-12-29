from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class NotificationType(str, Enum):
    """Types of notifications."""

    INFORMATIONAL = "informational"
    TRANSACTIONAL = "transactional"
    MARKETING = "marketing"
    SECURITY = "security"
    REMINDER = "reminder"
    SOCIAL = "social"
    SYSTEM = "system"
    ALERT = "alert"


class NotificationChannel(str, Enum):
    """Available notification channels."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    """Notification priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(str, Enum):
    """Notification delivery status."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduleFrequency(str, Enum):
    """Scheduling frequency options."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


# Request Models
class NotificationSendRequest(BaseModel):
    """Request model for sending notifications."""

    message: str = Field(..., min_length=1, max_length=5000)
    subject: Optional[str] = Field(None, max_length=255)
    recipients: List[str] = Field(..., min_items=1, max_items=1000)
    channels: List[NotificationChannel] = Field(default=[NotificationChannel.EMAIL])
    type: NotificationType = NotificationType.INFORMATIONAL
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    template_id: Optional[str] = None
    template_variables: Dict[str, Any] = Field(default_factory=dict)

    @validator("recipients")
    def validate_recipients(cls, v):
        if not v:
            raise ValueError("At least one recipient is required")
        return v


class NotificationScheduleRequest(BaseModel):
    """Request model for scheduling notifications."""

    notification_data: Dict[str, Any]
    recipients: List[str] = Field(..., min_items=1)
    channels: List[NotificationChannel] = Field(..., min_items=1)
    scheduled_at: datetime
    frequency: ScheduleFrequency = ScheduleFrequency.ONCE
    end_date: Optional[datetime] = None
    max_occurrences: int = Field(10, ge=1, le=365)
    timezone: str = "UTC"
    business_hours_only: bool = False
    retry_failed: bool = True
    max_retries: int = Field(3, ge=0, le=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NotificationTemplateRequest(BaseModel):
    """Request model for managing notification templates."""

    action: str = Field(..., pattern="^(list|create|update|delete)$")
    template_id: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    channel: Optional[NotificationChannel] = None
    subject: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    variables: List[str] = Field(default_factory=list)
    is_active: Optional[bool] = None


class NotificationProcessRequest(BaseModel):
    """Request model for processing radar signal notifications."""

    signal_ids: List[str] = Field(..., min_items=1, max_items=100)
    tenant_preferences: Dict[str, Any] = Field(default_factory=dict)


class NotificationPreferencesRequest(BaseModel):
    """Request model for updating notification preferences."""

    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    in_app_notifications: bool = True
    business_hours_only: bool = True
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    timezone: str = "UTC"
    notification_types: Dict[str, bool] = Field(default_factory=dict)


# Response Models
class NotificationDeliveryResult(BaseModel):
    """Delivery result for a specific channel."""

    channel: str
    sent_count: int
    failed_count: int
    delivery_rate: float
    details: str


class NotificationDeliverySummary(BaseModel):
    """Summary of notification delivery across all channels."""

    total_recipients: int
    total_sent: int
    total_failed: int
    success_rate: float
    delivery_time_seconds: float


class NotificationResponse(BaseModel):
    """Response model for notification data."""

    id: str
    workspace_id: str
    type: str
    channel: str
    title: str
    message: str
    subject: Optional[str]
    recipients: List[str]
    priority: str
    status: str
    delivery_results: Dict[str, NotificationDeliveryResult]
    delivery_summary: NotificationDeliverySummary
    read: bool
    read_at: Optional[datetime]
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    template_id: Optional[str]
    batch_id: Optional[str]


class NotificationScheduleResponse(BaseModel):
    """Response model for scheduled notifications."""

    schedule_id: str
    notification_data: Dict[str, Any]
    recipients: List[str]
    channels: List[str]
    scheduled_at: datetime
    frequency: str
    end_date: Optional[datetime]
    max_occurrences: int
    occurrence_count: int
    next_run: datetime
    status: str
    delivery_preferences: Dict[str, Any]
    created_at: datetime


class NotificationPreferences(BaseModel):
    """User notification preferences."""

    user_id: str
    email_notifications: bool
    sms_notifications: bool
    push_notifications: bool
    in_app_notifications: bool
    business_hours_only: bool
    quiet_hours_enabled: bool
    quiet_hours_start: str
    quiet_hours_end: str
    timezone: str
    notification_types: Dict[str, bool]


class NotificationTemplate(BaseModel):
    """Notification template model."""

    template_id: str
    name: str
    channel: str
    subject: Optional[str]
    content: str
    variables: List[str]
    created_at: datetime
    updated_at: Optional[datetime]
    usage_count: int
    is_active: bool


class NotificationAnalytics(BaseModel):
    """Notification analytics data."""

    period: str
    overview: Dict[str, Any]
    channel_analytics: Dict[str, Any]
    engagement_metrics: Dict[str, Any]
    notification_types: Dict[str, Any]
    insights: List[str]


class NotificationDigest(BaseModel):
    """Daily notification digest."""

    date: str
    total_notifications: int
    unread_count: int
    categories: Dict[str, int]
    priority_breakdown: Dict[str, int]
    top_notifications: List[Dict[str, Any]]
    engagement_summary: Dict[str, Any]


class NotificationListResponse(BaseModel):
    """Response model for notification lists with pagination."""

    notifications: List[NotificationResponse]
    pagination: Dict[str, Any]


# WebSocket/SSE Models
class NotificationEvent(BaseModel):
    """Real-time notification event."""

    event_type: str
    notification: NotificationResponse
    timestamp: datetime


class NotificationSubscription(BaseModel):
    """WebSocket subscription model."""

    user_id: str
    workspace_id: str
    channels: List[str]
    filters: Dict[str, Any] = Field(default_factory=dict)
