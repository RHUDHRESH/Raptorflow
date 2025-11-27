# backend/agents/council_of_lords/herald.py
# RaptorFlow Codex - Herald Lord Agent
# Phase 2A Week 7 - Communications & Announcements

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import logging
from abc import ABC, abstractmethod
import uuid

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS
# ============================================================================

class MessageChannel(str, Enum):
    """Communication channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    IN_APP = "in_app"
    SLACK = "slack"
    WEBHOOK = "webhook"


class MessageStatus(str, Enum):
    """Message delivery status"""
    DRAFT = "draft"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    OPENED = "opened"
    CLICKED = "clicked"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class TemplateType(str, Enum):
    """Message template types"""
    CAMPAIGN_ANNOUNCEMENT = "campaign_announcement"
    SYSTEM_ALERT = "system_alert"
    USER_INVITATION = "user_invitation"
    PERFORMANCE_REPORT = "performance_report"
    REMINDER = "reminder"
    CUSTOM = "custom"


class AnnouncementScope(str, Enum):
    """Announcement scope"""
    ORGANIZATION = "organization"
    GUILD = "guild"
    CAMPAIGN = "campaign"
    INDIVIDUAL = "individual"


# ============================================================================
# DATA CLASSES
# ============================================================================

class Message:
    """Represents a single message"""

    def __init__(
        self,
        message_id: str,
        channel: MessageChannel,
        recipient: str,
        subject: str,
        content: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        status: MessageStatus = MessageStatus.DRAFT,
        created_at: datetime = None,
        sent_at: Optional[datetime] = None,
        delivered_at: Optional[datetime] = None,
        opened_at: Optional[datetime] = None,
        clicked_at: Optional[datetime] = None,
        metadata: Dict[str, Any] = None,
    ):
        self.message_id = message_id
        self.channel = channel
        self.recipient = recipient
        self.subject = subject
        self.content = content
        self.priority = priority
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.sent_at = sent_at
        self.delivered_at = delivered_at
        self.opened_at = opened_at
        self.clicked_at = clicked_at
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "channel": self.channel.value,
            "recipient": self.recipient,
            "subject": self.subject,
            "content": self.content,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "clicked_at": self.clicked_at.isoformat() if self.clicked_at else None,
            "metadata": self.metadata,
        }


class MessageTemplate:
    """Represents a message template"""

    def __init__(
        self,
        template_id: str,
        name: str,
        template_type: TemplateType,
        subject_template: str,
        content_template: str,
        default_channel: MessageChannel = MessageChannel.EMAIL,
        variables: List[str] = None,
        created_at: datetime = None,
        description: str = "",
    ):
        self.template_id = template_id
        self.name = name
        self.template_type = template_type
        self.subject_template = subject_template
        self.content_template = content_template
        self.default_channel = default_channel
        self.variables = variables or []
        self.created_at = created_at or datetime.utcnow()
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "template_type": self.template_type.value,
            "subject_template": self.subject_template,
            "content_template": self.content_template,
            "default_channel": self.default_channel.value,
            "variables": self.variables,
            "created_at": self.created_at.isoformat(),
            "description": self.description,
        }


class Announcement:
    """Represents a scheduled announcement"""

    def __init__(
        self,
        announcement_id: str,
        title: str,
        content: str,
        scope: AnnouncementScope,
        scope_id: str,
        channels: List[MessageChannel],
        scheduled_at: datetime,
        status: MessageStatus = MessageStatus.DRAFT,
        recipients_count: int = 0,
        delivered_count: int = 0,
        opened_count: int = 0,
        created_at: datetime = None,
    ):
        self.announcement_id = announcement_id
        self.title = title
        self.content = content
        self.scope = scope
        self.scope_id = scope_id
        self.channels = channels
        self.scheduled_at = scheduled_at
        self.status = status
        self.recipients_count = recipients_count
        self.delivered_count = delivered_count
        self.opened_count = opened_count
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "announcement_id": self.announcement_id,
            "title": self.title,
            "content": self.content,
            "scope": self.scope.value,
            "scope_id": self.scope_id,
            "channels": [ch.value for ch in self.channels],
            "scheduled_at": self.scheduled_at.isoformat(),
            "status": self.status.value,
            "recipients_count": self.recipients_count,
            "delivered_count": self.delivered_count,
            "opened_count": self.opened_count,
            "created_at": self.created_at.isoformat(),
            "delivery_rate": (
                (self.delivered_count / self.recipients_count * 100)
                if self.recipients_count > 0
                else 0
            ),
            "open_rate": (
                (self.opened_count / self.delivered_count * 100)
                if self.delivered_count > 0
                else 0
            ),
        }


class DeliveryReport:
    """Represents delivery metrics for messages/announcements"""

    def __init__(
        self,
        report_id: str,
        period_start: datetime,
        period_end: datetime,
        total_messages: int = 0,
        delivered_messages: int = 0,
        failed_messages: int = 0,
        opened_messages: int = 0,
        clicked_messages: int = 0,
        created_at: datetime = None,
    ):
        self.report_id = report_id
        self.period_start = period_start
        self.period_end = period_end
        self.total_messages = total_messages
        self.delivered_messages = delivered_messages
        self.failed_messages = failed_messages
        self.opened_messages = opened_messages
        self.clicked_messages = clicked_messages
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "total_messages": self.total_messages,
            "delivered_messages": self.delivered_messages,
            "failed_messages": self.failed_messages,
            "opened_messages": self.opened_messages,
            "clicked_messages": self.clicked_messages,
            "delivery_rate": (
                (self.delivered_messages / self.total_messages * 100)
                if self.total_messages > 0
                else 0
            ),
            "failure_rate": (
                (self.failed_messages / self.total_messages * 100)
                if self.total_messages > 0
                else 0
            ),
            "open_rate": (
                (self.opened_messages / self.delivered_messages * 100)
                if self.delivered_messages > 0
                else 0
            ),
            "click_rate": (
                (self.clicked_messages / self.opened_messages * 100)
                if self.opened_messages > 0
                else 0
            ),
            "created_at": self.created_at.isoformat(),
        }


# ============================================================================
# BASE AGENT
# ============================================================================

class BaseAgent(ABC):
    """Abstract base agent class"""

    def __init__(self, name: str):
        self.name = name
        self.status = "uninitialized"

    async def initialize(self):
        """Initialize the agent"""
        self.status = "initialized"

    @abstractmethod
    async def execute(self, task: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task"""
        pass


# ============================================================================
# HERALD LORD AGENT
# ============================================================================

class HeraldLord(BaseAgent):
    """
    Herald Lord - Communications & Announcement Management

    Manages message delivery, announcements, templates, and communication tracking.
    Responsible for all outbound communications across the RaptorFlow system.
    """

    def __init__(self):
        super().__init__("Herald Lord")
        self.role = "Herald"
        self.domain = "Communications"

        # Data storage
        self.messages: Dict[str, Message] = {}
        self.templates: Dict[str, MessageTemplate] = {}
        self.announcements: Dict[str, Announcement] = {}
        self.delivery_reports: Dict[str, DeliveryReport] = {}

        # Performance metrics
        self.metrics = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "messages_failed": 0,
            "announcements_created": 0,
            "templates_created": 0,
            "average_delivery_time_ms": 0,
            "total_execution_time_ms": 0,
        }

        # Registered capabilities
        self.capabilities = {
            "send_message": self._send_message,
            "schedule_announcement": self._schedule_announcement,
            "manage_template": self._manage_template,
            "track_delivery": self._track_delivery,
            "get_communication_report": self._get_communication_report,
        }

    async def initialize(self):
        """Initialize Herald Lord with default templates"""
        await super().initialize()

        # Create default templates
        default_templates = [
            MessageTemplate(
                template_id=f"tpl_{uuid.uuid4().hex[:8]}",
                name="Campaign Announcement",
                template_type=TemplateType.CAMPAIGN_ANNOUNCEMENT,
                subject_template="New Campaign: {campaign_name}",
                content_template="We're excited to announce: {campaign_name}\n\n{details}",
                variables=["campaign_name", "details"],
            ),
            MessageTemplate(
                template_id=f"tpl_{uuid.uuid4().hex[:8]}",
                name="System Alert",
                template_type=TemplateType.SYSTEM_ALERT,
                subject_template="System Alert: {alert_type}",
                content_template="Alert: {alert_type}\n\nDetails: {details}\n\nAction: {action_required}",
                variables=["alert_type", "details", "action_required"],
            ),
            MessageTemplate(
                template_id=f"tpl_{uuid.uuid4().hex[:8]}",
                name="Performance Report",
                template_type=TemplateType.PERFORMANCE_REPORT,
                subject_template="Your {period} Performance Report",
                content_template="Performance Summary:\n\n{metrics}\n\nRecommendations: {recommendations}",
                variables=["period", "metrics", "recommendations"],
            ),
        ]

        for template in default_templates:
            self.templates[template.template_id] = template
            self.metrics["templates_created"] += 1

    async def execute(self, task: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Herald task"""
        if task not in self.capabilities:
            return {"success": False, "error": f"Unknown task: {task}"}

        try:
            capability_handler = self.capabilities[task]
            return await capability_handler(**parameters)
        except Exception as e:
            logger.error(f"Herald error executing {task}: {e}")
            return {"success": False, "error": str(e)}

    # ============================================================================
    # CAPABILITY HANDLERS
    # ============================================================================

    async def _send_message(
        self,
        channel: str,
        recipient: str,
        subject: str,
        content: str,
        priority: str = "normal",
        metadata: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send a message through specified channel"""
        message_id = f"msg_{uuid.uuid4().hex[:12]}"

        try:
            message_channel = MessageChannel(channel)
            message_priority = NotificationPriority(priority)
        except ValueError as e:
            return {"success": False, "error": f"Invalid parameter: {e}"}

        message = Message(
            message_id=message_id,
            channel=message_channel,
            recipient=recipient,
            subject=subject,
            content=content,
            priority=message_priority,
            status=MessageStatus.QUEUED,
            metadata=metadata or {},
        )

        self.messages[message_id] = message
        self.metrics["messages_sent"] += 1

        # Simulate delivery
        message.status = MessageStatus.SENT
        message.sent_at = datetime.utcnow()
        self.metrics["messages_delivered"] += 1

        return {
            "success": True,
            "message_id": message_id,
            "status": message.status.value,
            "recipient": recipient,
            "channel": channel,
        }

    async def _schedule_announcement(
        self,
        title: str,
        content: str,
        scope: str,
        scope_id: str,
        channels: List[str],
        scheduled_at: str,
        recipients_count: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """Schedule an announcement"""
        announcement_id = f"ann_{uuid.uuid4().hex[:12]}"

        try:
            announcement_scope = AnnouncementScope(scope)
            announcement_channels = [MessageChannel(ch) for ch in channels]
        except ValueError as e:
            return {"success": False, "error": f"Invalid parameter: {e}"}

        try:
            scheduled_datetime = datetime.fromisoformat(scheduled_at)
        except ValueError:
            return {"success": False, "error": "Invalid datetime format"}

        announcement = Announcement(
            announcement_id=announcement_id,
            title=title,
            content=content,
            scope=announcement_scope,
            scope_id=scope_id,
            channels=announcement_channels,
            scheduled_at=scheduled_datetime,
            status=MessageStatus.QUEUED,
            recipients_count=recipients_count,
        )

        self.announcements[announcement_id] = announcement
        self.metrics["announcements_created"] += 1

        return {
            "success": True,
            "announcement_id": announcement_id,
            "title": title,
            "scope": scope,
            "scheduled_at": scheduled_at,
            "channels": channels,
            "status": announcement.status.value,
        }

    async def _manage_template(
        self,
        action: str,
        name: str,
        template_type: str,
        subject_template: str = "",
        content_template: str = "",
        variables: List[str] = None,
        template_id: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """Manage message templates"""

        if action == "create":
            try:
                tpl_type = TemplateType(template_type)
            except ValueError:
                return {"success": False, "error": f"Invalid template type: {template_type}"}

            new_template_id = f"tpl_{uuid.uuid4().hex[:8]}"
            template = MessageTemplate(
                template_id=new_template_id,
                name=name,
                template_type=tpl_type,
                subject_template=subject_template,
                content_template=content_template,
                variables=variables or [],
            )

            self.templates[new_template_id] = template
            self.metrics["templates_created"] += 1

            return {
                "success": True,
                "template_id": new_template_id,
                "name": name,
                "template_type": template_type,
            }

        elif action == "get":
            if template_id not in self.templates:
                return {"success": False, "error": f"Template not found: {template_id}"}

            return {
                "success": True,
                "template": self.templates[template_id].to_dict(),
            }

        elif action == "list":
            templates_list = [t.to_dict() for t in self.templates.values()]
            return {
                "success": True,
                "templates": templates_list,
                "total": len(templates_list),
            }

        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    async def _track_delivery(
        self,
        message_id: str = "",
        announcement_id: str = "",
        period_days: int = 7,
        **kwargs
    ) -> Dict[str, Any]:
        """Track message/announcement delivery metrics"""

        if message_id:
            if message_id not in self.messages:
                return {"success": False, "error": f"Message not found: {message_id}"}

            message = self.messages[message_id]
            return {
                "success": True,
                "message_id": message_id,
                "status": message.status.value,
                "sent_at": message.sent_at.isoformat() if message.sent_at else None,
                "delivered_at": message.delivered_at.isoformat() if message.delivered_at else None,
                "opened_at": message.opened_at.isoformat() if message.opened_at else None,
            }

        elif announcement_id:
            if announcement_id not in self.announcements:
                return {"success": False, "error": f"Announcement not found: {announcement_id}"}

            announcement = self.announcements[announcement_id]
            return {
                "success": True,
                "announcement_id": announcement_id,
                "delivery_rate": announcement.to_dict()["delivery_rate"],
                "open_rate": announcement.to_dict()["open_rate"],
                "status": announcement.status.value,
            }

        else:
            return {"success": False, "error": "Must provide message_id or announcement_id"}

    async def _get_communication_report(
        self,
        period_days: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate communication report"""

        report_id = f"rep_{uuid.uuid4().hex[:12]}"
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=period_days)

        # Filter messages by period
        period_messages = [
            m for m in self.messages.values()
            if period_start <= m.created_at <= period_end
        ]

        total_messages = len(period_messages)
        delivered = sum(1 for m in period_messages if m.status in [MessageStatus.DELIVERED, MessageStatus.OPENED])
        failed = sum(1 for m in period_messages if m.status == MessageStatus.FAILED)
        opened = sum(1 for m in period_messages if m.opened_at is not None)
        clicked = sum(1 for m in period_messages if m.clicked_at is not None)

        report = DeliveryReport(
            report_id=report_id,
            period_start=period_start,
            period_end=period_end,
            total_messages=total_messages,
            delivered_messages=delivered,
            failed_messages=failed,
            opened_messages=opened,
            clicked_messages=clicked,
        )

        self.delivery_reports[report_id] = report

        return {
            "success": True,
            "report_id": report_id,
            "period_days": period_days,
            "total_messages": total_messages,
            "delivery_rate": report.to_dict()["delivery_rate"],
            "failure_rate": report.to_dict()["failure_rate"],
            "open_rate": report.to_dict()["open_rate"],
        }

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get Herald performance summary"""
        return {
            "messages_sent": self.metrics["messages_sent"],
            "messages_delivered": self.metrics["messages_delivered"],
            "messages_failed": self.metrics["messages_failed"],
            "announcements_created": self.metrics["announcements_created"],
            "templates_created": self.metrics["templates_created"],
            "delivery_rate": (
                (self.metrics["messages_delivered"] / self.metrics["messages_sent"] * 100)
                if self.metrics["messages_sent"] > 0
                else 0
            ),
        }

    async def get_recent_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages"""
        messages = sorted(
            self.messages.values(),
            key=lambda m: m.created_at,
            reverse=True
        )[:limit]
        return [m.to_dict() for m in messages]

    async def get_recent_announcements(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent announcements"""
        announcements = sorted(
            self.announcements.values(),
            key=lambda a: a.created_at,
            reverse=True
        )[:limit]
        return [a.to_dict() for a in announcements]

    async def get_recent_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent delivery reports"""
        reports = sorted(
            self.delivery_reports.values(),
            key=lambda r: r.created_at,
            reverse=True
        )[:limit]
        return [r.to_dict() for r in reports]
