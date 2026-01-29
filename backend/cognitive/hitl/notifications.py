"""
Approval Notifier - Sends notifications for approval requests

Manages email, webhook, and in-app notifications for pending approvals,
expiring requests, and other approval events.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ...redis.client import RedisClient
from ...redis.pubsub import PubSubService
from ..models import ApprovalRequest, ApprovalStatus

logger = logging.getLogger(__name__)


class ApprovalNotifier:
    """Manages approval notifications."""

    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()
        self.pubsub = PubSubService()
        self.notification_queue = "approval_notifications"

    async def notify_pending(
        self, user_id: str, gate_id: str, preview: str, urgency: str = "normal"
    ) -> bool:
        """
        Notify user of pending approval request.

        Args:
            user_id: User to notify
            gate_id: Approval gate ID
            preview: Output preview
            urgency: Notification urgency

        Returns:
            Success status
        """
        try:
            notification = {
                "type": "approval_pending",
                "user_id": user_id,
                "gate_id": gate_id,
                "preview": preview[:200],  # Limit preview length
                "urgency": urgency,
                "timestamp": datetime.now().isoformat(),
                "action_required": True,
            }

            # Send to notification queue
            await self.redis.lpush(self.notification_queue, json.dumps(notification))

            # Publish real-time notification
            await self.pubsub.publish(
                f"user_notifications:{user_id}", json.dumps(notification)
            )

            logger.info(f"Sent pending approval notification to user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to notify pending approval: {e}")
            return False

    async def notify_expiring(
        self, user_id: str, gate_id: str, time_remaining: int
    ) -> bool:
        """
        Notify user of expiring approval request.

        Args:
            user_id: User to notify
            gate_id: Approval gate ID
            time_remaining: Time remaining in seconds

        Returns:
            Success status
        """
        try:
            notification = {
                "type": "approval_expiring",
                "user_id": user_id,
                "gate_id": gate_id,
                "time_remaining": time_remaining,
                "expires_at": (
                    datetime.now() + timedelta(seconds=time_remaining)
                ).isoformat(),
                "timestamp": datetime.now().isoformat(),
                "action_required": True,
                "priority": (
                    "high" if time_remaining < 300 else "normal"
                ),  # High if < 5 minutes
            }

            # Send to notification queue
            await self.redis.lpush(self.notification_queue, json.dumps(notification))

            # Publish real-time notification
            await self.pubsub.publish(
                f"user_notifications:{user_id}", json.dumps(notification)
            )

            logger.info(f"Sent expiring approval notification to user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to notify expiring approval: {e}")
            return False

    async def notify_completed(
        self,
        user_id: str,
        gate_id: str,
        status: ApprovalStatus,
        feedback: Optional[str] = None,
    ) -> bool:
        """
        Notify user of completed approval.

        Args:
            user_id: User to notify
            gate_id: Approval gate ID
            status: Final approval status
            feedback: Optional feedback

        Returns:
            Success status
        """
        try:
            notification = {
                "type": "approval_completed",
                "user_id": user_id,
                "gate_id": gate_id,
                "status": status.value,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat(),
                "action_required": False,
            }

            # Send to notification queue
            await self.redis.lpush(self.notification_queue, json.dumps(notification))

            # Publish real-time notification
            await self.pubsub.publish(
                f"user_notifications:{user_id}", json.dumps(notification)
            )

            logger.info(f"Sent completed approval notification to user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to notify completed approval: {e}")
            return False

    async def notify_escalation(
        self, escalated_to: str, gate_id: str, reason: str, original_approver: str
    ) -> bool:
        """
        Notify user of approval escalation.

        Args:
            escalated_to: User being escalated to
            gate_id: Approval gate ID
            reason: Escalation reason
            original_approver: Original approver

        Returns:
            Success status
        """
        try:
            notification = {
                "type": "approval_escalated",
                "user_id": escalated_to,
                "gate_id": gate_id,
                "reason": reason,
                "original_approver": original_approver,
                "timestamp": datetime.now().isoformat(),
                "action_required": True,
                "priority": "high",
            }

            # Send to notification queue
            await self.redis.lpush(self.notification_queue, json.dumps(notification))

            # Publish real-time notification
            await self.pubsub.publish(
                f"user_notifications:{escalated_to}", json.dumps(notification)
            )

            logger.info(f"Sent escalation notification to user {escalated_to}")
            return True

        except Exception as e:
            logger.error(f"Failed to notify escalation: {e}")
            return False

    async def batch_notify_pending(self, workspace_id: str) -> int:
        """
        Send batch notifications for all pending approvals.

        Args:
            workspace_id: Workspace identifier

        Returns:
            Number of notifications sent
        """
        try:
            # Get pending approvals for workspace
            from gate import ApprovalGate

            gate = ApprovalGate(self.redis)
            pending_approvals = await gate.get_pending_approvals(workspace_id)

            notifications_sent = 0

            for approval in pending_approvals:
                # Check if notification already sent recently
                notification_key = f"last_notification:{approval.gate_id}"
                last_notification = await self.redis.get(notification_key)

                if last_notification:
                    last_time = datetime.fromisoformat(last_notification)
                    if (
                        datetime.now() - last_time
                    ).total_seconds() < 3600:  # 1 hour cooldown
                        continue

                # Send notification
                success = await self.notify_pending(
                    approval.user_id,
                    approval.gate_id,
                    approval.output_preview,
                    "high" if approval.risk_level.value >= 3 else "normal",
                )

                if success:
                    # Record notification time
                    await self.redis.set(
                        notification_key, datetime.now().isoformat(), ex=3600
                    )
                    notifications_sent += 1

            logger.info(
                f"Sent {notifications_sent} batch notifications for workspace {workspace_id}"
            )
            return notifications_sent

        except Exception as e:
            logger.error(f"Failed to send batch notifications: {e}")
            return 0

    async def start_expiration_monitor(self):
        """Start background task to monitor expiring approvals."""
        try:
            while True:
                await self._check_expiring_approvals()
                await asyncio.sleep(60)  # Check every minute

        except Exception as e:
            logger.error(f"Expiration monitor failed: {e}")

    async def _check_expiring_approvals(self):
        """Check for approvals about to expire and send notifications."""
        try:
            from gate import ApprovalGate

            gate = ApprovalGate(self.redis)

            # This would need to query all pending approvals
            # For now, placeholder implementation

            # TODO: Implement actual expiration checking
            # 1. Get all pending approvals
            # 2. Check expiration times
            # 3. Send notifications for those expiring soon

        except Exception as e:
            logger.error(f"Failed to check expiring approvals: {e}")

    async def get_notification_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's notification preferences.

        Args:
            user_id: User identifier

        Returns:
            Notification preferences
        """
        try:
            preferences_key = f"notification_preferences:{user_id}"
            preferences_data = await self.redis.get(preferences_key)

            if preferences_data:
                return json.loads(preferences_data)

            # Default preferences
            return {
                "email_notifications": True,
                "push_notifications": True,
                "pending_approvals": True,
                "expiring_approvals": True,
                "completed_approvals": True,
                "escalations": True,
                "quiet_hours": {"enabled": False, "start": "22:00", "end": "08:00"},
            }

        except Exception as e:
            logger.error(f"Failed to get notification preferences: {e}")
            return {}

    async def update_notification_preferences(
        self, user_id: str, preferences: Dict[str, Any]
    ) -> bool:
        """
        Update user's notification preferences.

        Args:
            user_id: User identifier
            preferences: New preferences

        Returns:
            Success status
        """
        try:
            preferences_key = f"notification_preferences:{user_id}"
            await self.redis.set(
                preferences_key,
                json.dumps(preferences),
                ex=86400 * 365,  # Keep for 1 year
            )

            logger.info(f"Updated notification preferences for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update notification preferences: {e}")
            return False
