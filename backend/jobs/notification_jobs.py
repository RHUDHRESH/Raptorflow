"""
Notification jobs for Raptorflow.

Provides background jobs for sending approval reminders,
usage alerts, weekly digests, and user notifications.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from decorators import background_job, daily_job, hourly_job, job, weekly_job
from infrastructure.cloud_monitoring import get_cloud_monitoring
from infrastructure.logging import get_cloud_logging

from .models import JobResult, JobStatus

logger = logging.getLogger(__name__)


@dataclass
class ApprovalReminderResult:
    """Result of approval reminder sending."""

    workspace_id: str
    pending_approvals: int
    reminders_sent: int
    users_notified: List[str]
    notification_channels: List[str]
    response_rate: float
    processing_time_seconds: float
    errors: List[str]


@dataclass
class UsageAlertResult:
    """Result of usage alert sending."""

    workspace_id: str
    alerts_triggered: List[str]
    users_alerted: List[str]
    alert_types: List[str]
    severity_levels: List[str]
    actions_taken: List[str]
    escalation_count: int
    processing_time_seconds: float
    errors: List[str]


@dataclass
class WeeklyDigestResult:
    """Result of weekly digest sending."""

    workspace_id: str
    week_start: str
    week_end: str
    recipients: List[str]
    digest_sections: List[str]
    engagement_metrics: Dict[str, Any]
    personalization_applied: bool
    delivery_status: Dict[str, str]
    processing_time_seconds: float
    errors: List[str]


@dataclass
class UserNotificationResult:
    """Result of user notification sending."""

    user_id: str
    notification_type: str
    channels_used: List[str]
    delivery_status: Dict[str, str]
    engagement_tracked: bool
    follow_up_scheduled: bool
    processing_time_seconds: float
    errors: List[str]


class NotificationJobs:
    """Notification job implementations."""

    def __init__(self):
        self.logger = logging.getLogger("notification_jobs")
        self.logging = get_cloud_logging()
        self.monitoring = get_cloud_monitoring()

    async def send_approval_reminder_job(
        self, workspace_id: str
    ) -> ApprovalReminderResult:
        """Send approval reminders for a workspace."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting approval reminder sending for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "send_approval_reminder",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get notification service
            from notifications.notification_service import get_notification_service

            notification_service = get_notification_service()

            # Get pending approvals
            pending_approvals = await notification_service.get_pending_approvals(
                workspace_id
            )
            pending_approvals_count = len(pending_approvals)

            # Get users who need reminders
            users_to_notify = await notification_service.get_approval_users(
                pending_approvals
            )
            users_notified = []
            reminders_sent = 0
            notification_channels = []

            # Send reminders to each user
            for user in users_to_notify:
                try:
                    # Get user's pending approvals
                    user_approvals = [
                        pa for pa in pending_approvals if pa.assigned_to == user.id
                    ]

                    if user_approvals:
                        # Send reminder
                        reminder_result = (
                            await notification_service.send_approval_reminder(
                                user.id, user_approvals, workspace_id
                            )
                        )

                        if reminder_result.get("success", False):
                            users_notified.append(user.id)
                            reminders_sent += len(user_approvals)
                            notification_channels.extend(
                                reminder_result.get("channels", [])
                            )

                except Exception as e:
                    errors.append(
                        f"Failed to send reminder to user {user.id}: {str(e)}"
                    )

            # Calculate response rate
            response_rate = await notification_service.calculate_approval_response_rate(
                workspace_id, pending_approvals
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = ApprovalReminderResult(
                workspace_id=workspace_id,
                pending_approvals=pending_approvals_count,
                reminders_sent=reminders_sent,
                users_notified=users_notified,
                notification_channels=list(set(notification_channels)),
                response_rate=response_rate,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "approval_reminders_sent",
                reminders_sent,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "approval_reminder_response_rate",
                response_rate,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "approval_reminder_processing_time",
                processing_time,
                {"workspace_id": workspace_id},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Approval reminder sending completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "pending_approvals": pending_approvals_count,
                    "reminders_sent": reminders_sent,
                    "users_notified": len(users_notified),
                    "response_rate": response_rate,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Approval reminder sending failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Approval reminder sending failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def send_usage_alert_job(self, workspace_id: str) -> UsageAlertResult:
        """Send usage alerts for a workspace."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting usage alert sending for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "send_usage_alert",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get notification service
            from notifications.notification_service import get_notification_service

            notification_service = get_notification_service()

            # Check usage limits and thresholds
            usage_alerts = await notification_service.check_usage_alerts(workspace_id)
            alerts_triggered = [alert.get("type") for alert in usage_alerts]

            # Get users to alert
            users_to_alert = await notification_service.get_usage_alert_users(
                workspace_id
            )
            users_alerted = []
            alert_types = []
            severity_levels = []
            actions_taken = []
            escalation_count = 0

            # Send alerts to each user
            for user in users_to_alert:
                try:
                    # Get user-specific alerts
                    user_alerts = [
                        alert
                        for alert in usage_alerts
                        if alert.get("user_id") == user.id
                    ]

                    if user_alerts:
                        # Send alerts
                        alert_result = await notification_service.send_usage_alerts(
                            user.id, user_alerts, workspace_id
                        )

                        if alert_result.get("success", False):
                            users_alerted.append(user.id)
                            alert_types.extend(
                                [alert.get("type") for alert in user_alerts]
                            )
                            severity_levels.extend(
                                [alert.get("severity") for alert in user_alerts]
                            )
                            actions_taken.extend(alert_result.get("actions_taken", []))

                            # Check for escalation
                            if alert_result.get("escalated", False):
                                escalation_count += 1

                except Exception as e:
                    errors.append(f"Failed to send alert to user {user.id}: {str(e)}")

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = UsageAlertResult(
                workspace_id=workspace_id,
                alerts_triggered=alerts_triggered,
                users_alerted=users_alerted,
                alert_types=list(set(alert_types)),
                severity_levels=list(set(severity_levels)),
                actions_taken=actions_taken,
                escalation_count=escalation_count,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "usage_alerts_triggered",
                len(alerts_triggered),
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "usage_alerts_sent", len(users_alerted), {"workspace_id": workspace_id}
            )

            await self.monitoring.record_metric(
                "usage_alert_escalations",
                escalation_count,
                {"workspace_id": workspace_id},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Usage alert sending completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "alerts_triggered": len(alerts_triggered),
                    "users_alerted": len(users_alerted),
                    "escalation_count": escalation_count,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Usage alert sending failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Usage alert sending failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def send_weekly_digest_job(
        self, workspace_id: str, week_start: Optional[str] = None
    ) -> WeeklyDigestResult:
        """Send weekly digest for a workspace."""
        if week_start is None:
            # Get last week's start date (Monday)
            today = datetime.utcnow().date()
            days_since_monday = today.weekday()
            last_monday = today - timedelta(days=days_since_monday + 7)
            week_start = last_monday.strftime("%Y-%m-%d")

        week_end = (
            datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=6)
        ).strftime("%Y-%m-%d")

        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting weekly digest sending for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "week_start": week_start,
                    "week_end": week_end,
                    "job_type": "send_weekly_digest",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get notification service
            from notifications.notification_service import get_notification_service

            notification_service = get_notification_service()

            # Generate digest content
            digest_content = await notification_service.generate_weekly_digest(
                workspace_id, week_start, week_end
            )

            # Get digest recipients
            recipients = await notification_service.get_digest_recipients(workspace_id)
            recipient_emails = [user.email for user in recipients]

            # Get digest sections
            digest_sections = list(digest_content.get("sections", {}).keys())

            # Send digest to each recipient
            delivery_status = {}
            engagement_metrics = {}
            personalization_applied = False

            for recipient in recipients:
                try:
                    # Personalize digest
                    personalized_digest = await notification_service.personalize_digest(
                        digest_content, recipient
                    )

                    if personalized_digest.get("personalized", False):
                        personalization_applied = True

                    # Send digest
                    send_result = await notification_service.send_weekly_digest(
                        recipient.id, personalized_digest, workspace_id
                    )

                    delivery_status[recipient.email] = send_result.get(
                        "status", "failed"
                    )

                    # Track engagement metrics
                    engagement_metrics[recipient.email] = send_result.get(
                        "engagement_metrics", {}
                    )

                except Exception as e:
                    errors.append(
                        f"Failed to send digest to {recipient.email}: {str(e)}"
                    )
                    delivery_status[recipient.email] = "failed"

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = WeeklyDigestResult(
                workspace_id=workspace_id,
                week_start=week_start,
                week_end=week_end,
                recipients=recipient_emails,
                digest_sections=digest_sections,
                engagement_metrics=engagement_metrics,
                personalization_applied=personalization_applied,
                delivery_status=delivery_status,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "weekly_digest_sent",
                len([s for s in delivery_status.values() if s == "sent"]),
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "weekly_digest_sections",
                len(digest_sections),
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "weekly_digest_processing_time",
                processing_time,
                {"workspace_id": workspace_id},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Weekly digest sending completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "week_start": week_start,
                    "week_end": week_end,
                    "recipients": len(recipients),
                    "digest_sections": len(digest_sections),
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Weekly digest sending failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Weekly digest sending failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "week_start": week_start,
                    "week_end": week_end,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def send_user_notification_job(
        self,
        user_id: str,
        notification_type: str,
        message: str,
        channels: Optional[List[str]] = None,
    ) -> UserNotificationResult:
        """Send notification to a specific user."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting user notification sending for user: {user_id}",
                {
                    "user_id": user_id,
                    "notification_type": notification_type,
                    "job_type": "send_user_notification",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get notification service
            from notifications.notification_service import get_notification_service

            notification_service = get_notification_service()

            # Get user preferences
            user_preferences = (
                await notification_service.get_user_notification_preferences(user_id)
            )

            # Determine channels to use
            if channels is None:
                channels = user_preferences.get("preferred_channels", ["email"])

            # Send notification
            notification_result = await notification_service.send_notification(
                user_id, notification_type, message, channels
            )

            # Extract results
            delivery_status = notification_result.get("delivery_status", {})
            engagement_tracked = notification_result.get("engagement_tracked", False)
            follow_up_scheduled = notification_result.get("follow_up_scheduled", False)

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = UserNotificationResult(
                user_id=user_id,
                notification_type=notification_type,
                channels_used=channels,
                delivery_status=delivery_status,
                engagement_tracked=engagement_tracked,
                follow_up_scheduled=follow_up_scheduled,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "user_notification_sent",
                len([s for s in delivery_status.values() if s == "sent"]),
                {"notification_type": notification_type},
            )

            await self.monitoring.record_metric(
                "user_notification_engagement_tracked",
                1 if engagement_tracked else 0,
                {"notification_type": notification_type},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"User notification sending completed for user: {user_id}",
                {
                    "user_id": user_id,
                    "notification_type": notification_type,
                    "channels_used": channels,
                    "delivery_status": delivery_status,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"User notification sending failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"User notification sending failed for user: {user_id}",
                {
                    "user_id": user_id,
                    "notification_type": notification_type,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def process_notification_queue_job(self) -> Dict[str, Any]:
        """Process notification queue."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                "Starting notification queue processing",
                {
                    "job_type": "process_notification_queue",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get notification service
            from notifications.notification_service import get_notification_service

            notification_service = get_notification_service()

            # Get pending notifications
            pending_notifications = (
                await notification_service.get_pending_notifications()
            )

            processed_notifications = []
            failed_notifications = []

            # Process each notification
            for notification in pending_notifications:
                try:
                    # Send notification
                    result = await notification_service.send_notification(
                        notification.get("user_id"),
                        notification.get("type"),
                        notification.get("message"),
                        notification.get("channels", ["email"]),
                    )

                    if result.get("success", False):
                        processed_notifications.append(notification)
                    else:
                        failed_notifications.append(notification)

                except Exception as e:
                    errors.append(
                        f"Failed to process notification {notification.get('id')}: {str(e)}"
                    )
                    failed_notifications.append(notification)

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = {
                "pending_notifications": len(pending_notifications),
                "processed_notifications": len(processed_notifications),
                "failed_notifications": len(failed_notifications),
                "processing_time_seconds": processing_time,
                "errors": errors,
            }

            # Record metrics
            await self.monitoring.record_metric(
                "notification_queue_processed",
                len(processed_notifications),
                {"operation": "queue_processing"},
            )

            await self.monitoring.record_metric(
                "notification_queue_failed",
                len(failed_notifications),
                {"operation": "queue_processing"},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                "Notification queue processing completed",
                {
                    "pending_notifications": len(pending_notifications),
                    "processed_notifications": len(processed_notifications),
                    "failed_notifications": len(failed_notifications),
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Notification queue processing failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                "Notification queue processing failed",
                {"error": str(e), "processing_time_seconds": processing_time},
            )

            raise


# Create global instance
_notification_jobs = NotificationJobs()


# Job implementations with decorators
@hourly_job(
    minute=0,
    queue="notifications",
    retries=2,
    timeout=600,  # 10 minutes
    description="Send approval reminders",
)
async def send_approval_reminder_job(workspace_id: str) -> Dict[str, Any]:
    """Send approval reminders job."""
    result = await _notification_jobs.send_approval_reminder_job(workspace_id)
    return result.__dict__


@hourly_job(
    minute=15,
    queue="notifications",
    retries=2,
    timeout=600,  # 10 minutes
    description="Send usage alerts",
)
async def send_usage_alert_job(workspace_id: str) -> Dict[str, Any]:
    """Send usage alerts job."""
    result = await _notification_jobs.send_usage_alert_job(workspace_id)
    return result.__dict__


@weekly_job(
    day_of_week=1,  # Monday
    hour=9,
    minute=0,
    queue="notifications",
    retries=2,
    timeout=1800,  # 30 minutes
    description="Send weekly digest",
)
async def send_weekly_digest_job(
    workspace_id: str, week_start: Optional[str] = None
) -> Dict[str, Any]:
    """Send weekly digest job."""
    result = await _notification_jobs.send_weekly_digest_job(workspace_id, week_start)
    return result.__dict__


@background_job(
    queue="notifications",
    retries=1,
    timeout=300,  # 5 minutes
    description="Send user notification",
)
async def send_user_notification_job(
    user_id: str,
    notification_type: str,
    message: str,
    channels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Send user notification job."""
    result = await _notification_jobs.send_user_notification_job(
        user_id, notification_type, message, channels
    )
    return result.__dict__


@interval_job(
    seconds=300,  # 5 minutes
    queue="notifications",
    retries=1,
    timeout=600,  # 10 minutes
    description="Process notification queue",
)
async def process_notification_queue_job() -> Dict[str, Any]:
    """Process notification queue job."""
    result = await _notification_jobs.process_notification_queue_job()
    return result


# Convenience functions
async def send_workspace_approval_reminders(
    workspace_id: str,
) -> ApprovalReminderResult:
    """Send approval reminders for a workspace."""
    return await _notification_jobs.send_approval_reminder_job(workspace_id)


async def send_workspace_usage_alerts(workspace_id: str) -> UsageAlertResult:
    """Send usage alerts for a workspace."""
    return await _notification_jobs.send_usage_alert_job(workspace_id)


async def send_workspace_weekly_digest(
    workspace_id: str, week_start: Optional[str] = None
) -> WeeklyDigestResult:
    """Send weekly digest for a workspace."""
    return await _notification_jobs.send_weekly_digest_job(workspace_id, week_start)


async def send_user_notification(
    user_id: str,
    notification_type: str,
    message: str,
    channels: Optional[List[str]] = None,
) -> UserNotificationResult:
    """Send notification to a user."""
    return await _notification_jobs.send_user_notification_job(
        user_id, notification_type, message, channels
    )


async def process_notification_queue() -> Dict[str, Any]:
    """Process notification queue."""
    return await _notification_jobs.process_notification_queue_job()


# Export all jobs
__all__ = [
    "NotificationJobs",
    "send_approval_reminder_job",
    "send_usage_alert_job",
    "send_weekly_digest_job",
    "send_user_notification_job",
    "process_notification_queue_job",
    "send_workspace_approval_reminders",
    "send_workspace_usage_alerts",
    "send_workspace_weekly_digest",
    "send_user_notification",
    "process_notification_queue",
]
