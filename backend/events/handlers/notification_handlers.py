"""
Notification event handlers.
Handle events that trigger user notifications, emails, and alerts.
"""

import logging
from typing import Any, Dict, Optional

from backend.services.email_service import EmailService
from backend.services.notification_service import NotificationService
from ..types import ApprovalRequestedEvent, Event, EventType, UsageLimitReachedEvent

logger = logging.getLogger(__name__)


async def on_approval_requested(event: ApprovalRequestedEvent) -> None:
    """Handle approval requested event - sends notification to approver."""
    try:
        workspace_id = event.workspace_id
        user_id = event.user_id
        approver_id = event.approver_id
        content_id = event.content_id
        content_type = event.content_type

        logger.info(f"Approval requested for {content_type} {content_id} by {user_id}")

        # Get notification service
        notification_service = NotificationService()

        # Create in-app notification for approver
        await notification_service.create_notification(
            user_id=approver_id,
            workspace_id=workspace_id,
            title="Approval Required",
            message=f"{user_id} is requesting approval for {content_type}",
            type="approval_request",
            data={
                "content_id": content_id,
                "content_type": content_type,
                "requester_id": user_id,
            },
            action_url=f"/workspace/{workspace_id}/approvals/{content_id}",
        )

        # Send email notification if enabled
        email_service = EmailService()
        if email_service.is_enabled():
            await email_service.send_approval_request_email(
                approver_email=approver_id,  # Assuming approver_id is email for now
                requester_name=user_id,
                content_type=content_type,
                approval_url=f"/workspace/{workspace_id}/approvals/{content_id}",
            )

        logger.info(f"Approval notification sent to {approver_id}")

    except Exception as e:
        logger.error(f"Failed to handle approval requested event: {e}")


async def on_approval_granted(event: Event) -> None:
    """Handle approval granted event - notifies requester."""
    try:
        workspace_id = event.workspace_id
        requester_id = event.data.get("requester_id") if event.data else None
        approver_id = event.user_id
        content_id = event.data.get("content_id") if event.data else None
        content_type = event.data.get("content_type") if event.data else None

        if not all([requester_id, content_id, content_type]):
            logger.warning("Approval granted event missing required data")
            return

        logger.info(
            f"Approval granted for {content_type} {content_id} by {approver_id}"
        )

        # Notify requester
        notification_service = NotificationService()
        await notification_service.create_notification(
            user_id=requester_id,
            workspace_id=workspace_id,
            title="Approval Granted",
            message=f"Your {content_type} has been approved by {approver_id}",
            type="approval_granted",
            data={
                "content_id": content_id,
                "content_type": content_type,
                "approver_id": approver_id,
            },
            action_url=f"/workspace/{workspace_id}/content/{content_id}",
        )

        logger.info(f"Approval granted notification sent to {requester_id}")

    except Exception as e:
        logger.error(f"Failed to handle approval granted event: {e}")


async def on_approval_denied(event: Event) -> None:
    """Handle approval denied event - notifies requester with reason."""
    try:
        workspace_id = event.workspace_id
        requester_id = event.data.get("requester_id") if event.data else None
        approver_id = event.user_id
        content_id = event.data.get("content_id") if event.data else None
        content_type = event.data.get("content_type") if event.data else None
        reason = event.data.get("reason") if event.data else "No reason provided"

        if not all([requester_id, content_id, content_type]):
            logger.warning("Approval denied event missing required data")
            return

        logger.info(f"Approval denied for {content_type} {content_id} by {approver_id}")

        # Notify requester
        notification_service = NotificationService()
        await notification_service.create_notification(
            user_id=requester_id,
            workspace_id=workspace_id,
            title="Approval Denied",
            message=f"Your {content_type} was denied by {approver_id}: {reason}",
            type="approval_denied",
            data={
                "content_id": content_id,
                "content_type": content_type,
                "approver_id": approver_id,
                "reason": reason,
            },
            action_url=f"/workspace/{workspace_id}/content/{content_id}",
        )

        logger.info(f"Approval denied notification sent to {requester_id}")

    except Exception as e:
        logger.error(f"Failed to handle approval denied event: {e}")


async def on_usage_limit_reached(event: UsageLimitReachedEvent) -> None:
    """Handle usage limit reached event - sends warning notification."""
    try:
        workspace_id = event.workspace_id
        limit_type = event.limit_type
        current_usage = event.current_usage
        limit = event.limit
        percentage_used = event.percentage_used

        logger.info(
            f"Usage limit reached for workspace {workspace_id}: {limit_type} at {percentage_used:.1f}%"
        )

        # Get workspace owners/admins to notify
        # This would typically come from a user service
        notification_service = NotificationService()

        # Create warning notification
        await notification_service.create_workspace_notification(
            workspace_id=workspace_id,
            title="Usage Limit Warning",
            message=f"Workspace {limit_type} usage has reached {percentage_used:.1f}% ({current_usage}/{limit})",
            type="usage_warning",
            data={
                "limit_type": limit_type,
                "current_usage": current_usage,
                "limit": limit,
                "percentage_used": percentage_used,
            },
            priority="high" if percentage_used >= 90 else "medium",
        )

        # Send email for high usage
        email_service = EmailService()
        if email_service.is_enabled() and percentage_used >= 90:
            await email_service.send_usage_warning_email(
                workspace_id=workspace_id,
                limit_type=limit_type,
                percentage_used=percentage_used,
            )

        logger.info(f"Usage limit warning sent for workspace {workspace_id}")

    except Exception as e:
        logger.error(f"Failed to handle usage limit reached event: {e}")


async def on_usage_limit_exceeded(event: Event) -> None:
    """Handle usage limit exceeded event - sends critical notification and may restrict access."""
    try:
        workspace_id = event.workspace_id
        limit_type = event.data.get("limit_type") if event.data else None
        current_usage = event.data.get("current_usage") if event.data else None
        limit = event.data.get("limit") if event.data else None

        if not all([limit_type, current_usage, limit]):
            logger.warning("Usage limit exceeded event missing required data")
            return

        logger.warning(
            f"Usage limit exceeded for workspace {workspace_id}: {limit_type}"
        )

        # Create critical notification
        notification_service = NotificationService()
        await notification_service.create_workspace_notification(
            workspace_id=workspace_id,
            title="Usage Limit Exceeded",
            message=f"Workspace {limit_type} usage has exceeded the limit ({current_usage} > {limit})",
            type="usage_exceeded",
            data={
                "limit_type": limit_type,
                "current_usage": current_usage,
                "limit": limit,
            },
            priority="critical",
        )

        # Send immediate email notification
        email_service = EmailService()
        if email_service.is_enabled():
            await email_service.send_usage_exceeded_email(
                workspace_id=workspace_id,
                limit_type=limit_type,
                current_usage=current_usage,
                limit=limit,
            )

        logger.info(
            f"Usage limit exceeded notification sent for workspace {workspace_id}"
        )

    except Exception as e:
        logger.error(f"Failed to handle usage limit exceeded event: {e}")


# Register all handlers
def register_notification_handlers():
    """Register all notification event handlers."""
    from ..bus import subscribe_event

    handlers = [
        (EventType.APPROVAL_REQUESTED, on_approval_requested),
        (EventType.APPROVAL_GRANTED, on_approval_granted),
        (EventType.APPROVAL_DENIED, on_approval_denied),
        (EventType.USAGE_LIMIT_REACHED, on_usage_limit_reached),
        (EventType.USAGE_LIMIT_EXCEEDED, on_usage_limit_exceeded),
    ]

    for event_type, handler in handlers:
        subscribe_event(event_type, handler)
        logger.debug(f"Registered notification handler for {event_type.value}")
