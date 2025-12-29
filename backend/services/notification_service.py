import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from db import get_db_connection
from models.notification_models import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)
from tools.notification_system import NotificationSystemTool

logger = logging.getLogger("raptorflow.services.notification")


class NotificationService:
    """
    Service layer for notification management.
    Wraps the NotificationSystemTool and provides database persistence.
    """

    def __init__(self):
        self.notification_tool = NotificationSystemTool()

    async def send_notification(
        self,
        workspace_id: str,
        message: str,
        subject: Optional[str] = None,
        recipients: List[str] = None,
        channels: List[str] = None,
        notification_type: str = "informational",
        priority: str = "normal",
        metadata: Dict[str, Any] = None,
        template_id: Optional[str] = None,
        template_variables: Dict[str, Any] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a notification and store it in the database."""

        if not recipients:
            raise ValueError("Recipients are required")

        if not channels:
            channels = ["email"]

        # Prepare notification data for the tool
        notification_data = {
            "message": message,
            "subject": subject or "Notification",
            "type": notification_type,
            "priority": priority,
            "metadata": metadata or {},
            "template_id": template_id,
            "template_variables": template_variables or {},
        }

        # Send notification using the tool
        tool_result = await self.notification_tool._execute(
            action="send_notification",
            notification_data=notification_data,
            recipients=recipients,
            channels=channels,
        )

        if tool_result.get("success"):
            # Store notification in database
            notification_id = await self._store_notification(
                workspace_id=workspace_id,
                notification_data=notification_data,
                recipients=recipients,
                channels=channels,
                delivery_results=tool_result["data"]["delivery_results"],
                delivery_summary=tool_result["data"]["delivery_summary"],
                user_id=user_id,
            )

            # Update tool result with database ID
            tool_result["data"]["id"] = notification_id
            tool_result["data"]["workspace_id"] = workspace_id

            return tool_result
        else:
            raise Exception(f"Failed to send notification: {tool_result}")

    async def schedule_notification(
        self,
        workspace_id: str,
        notification_data: Dict[str, Any],
        recipients: List[str],
        channels: List[str],
        scheduled_at: datetime,
        frequency: str = "once",
        end_date: Optional[datetime] = None,
        max_occurrences: int = 10,
        timezone: str = "UTC",
        business_hours_only: bool = False,
        retry_failed: bool = True,
        max_retries: int = 3,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Schedule a notification for future delivery."""

        # Prepare scheduling data
        schedule_data = {
            **notification_data,
            "scheduled_time": scheduled_at.isoformat(),
            "frequency": frequency,
            "end_date": end_date.isoformat() if end_date else None,
            "max_occurrences": max_occurrences,
            "timezone": timezone,
            "business_hours_only": business_hours_only,
            "retry_failed": retry_failed,
            "max_retries": max_retries,
        }

        # Schedule using the tool
        tool_result = await self.notification_tool._execute(
            action="schedule_notification",
            notification_data=schedule_data,
            recipients=recipients,
            channels=channels,
        )

        if tool_result.get("success"):
            # Store schedule in database
            schedule_id = await self._store_notification_schedule(
                workspace_id=workspace_id,
                notification_data=notification_data,
                recipients=recipients,
                channels=channels,
                scheduled_at=scheduled_at,
                frequency=frequency,
                end_date=end_date,
                max_occurrences=max_occurrences,
                timezone=timezone,
                business_hours_only=business_hours_only,
                retry_failed=retry_failed,
                max_retries=max_retries,
                user_id=user_id,
            )

            # Update tool result with database ID
            tool_result["data"]["schedule_id"] = schedule_id
            tool_result["data"]["workspace_id"] = workspace_id

            return tool_result
        else:
            raise Exception(f"Failed to schedule notification: {tool_result}")

    async def get_notification_preferences(
        self, workspace_id: str, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get notification preferences for a user or workspace."""

        # Get preferences from tool
        tool_result = await self.notification_tool._execute(
            action="get_preferences",
            filters={"workspace_id": workspace_id, "user_id": user_id},
        )

        if tool_result.get("success"):
            # Enhance with database preferences if available
            if user_id:
                db_preferences = await self._get_user_preferences(workspace_id, user_id)
                if db_preferences:
                    tool_result["data"]["user_preferences"] = [
                        pref
                        for pref in tool_result["data"]["user_preferences"]
                        if pref["user_id"] == user_id
                    ] or [db_preferences]

            return tool_result
        else:
            raise Exception(f"Failed to get preferences: {tool_result}")

    async def manage_notification_templates(
        self,
        workspace_id: str,
        action: str,
        template_data: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Manage notification templates."""

        # Add workspace context to template data
        template_data["workspace_id"] = workspace_id

        # Manage templates using the tool
        tool_result = await self.notification_tool._execute(
            action="manage_templates",
            notification_data=template_data,
        )

        if tool_result.get("success"):
            # Store template in database if creating or updating
            if action in ["create", "update"]:
                await self._store_notification_template(
                    workspace_id=workspace_id,
                    template_data=template_data,
                    action=action,
                    user_id=user_id,
                )

            return tool_result
        else:
            raise Exception(f"Failed to manage templates: {tool_result}")

    async def get_notification_analytics(
        self, workspace_id: str, period: str = "30_days"
    ) -> Dict[str, Any]:
        """Get notification analytics."""

        # Get analytics from tool
        tool_result = await self.notification_tool._execute(
            action="notification_analytics",
            filters={"workspace_id": workspace_id, "period": period},
        )

        if tool_result.get("success"):
            # Enhance with database analytics
            db_analytics = await self._get_database_analytics(workspace_id, period)
            if db_analytics:
                tool_result["data"]["database_analytics"] = db_analytics

            return tool_result
        else:
            raise Exception(f"Failed to get analytics: {tool_result}")

    async def process_signal_notifications(
        self,
        workspace_id: str,
        signal_ids: List[str],
        tenant_preferences: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Process radar signal notifications."""

        from services.radar_notification_service import RadarNotificationService
        from services.radar_repository import RadarRepository

        try:
            # Fetch signals
            repository = RadarRepository()
            signals = await repository.fetch_signals(workspace_id, signal_ids)

            # Process notifications
            radar_service = RadarNotificationService()
            notifications = await radar_service.process_signal_notifications(
                signals, tenant_preferences
            )

            # Store notifications if generated
            for notification in notifications:
                await self._store_notification_from_radar(
                    workspace_id=workspace_id,
                    notification=notification,
                )

            return notifications

        except Exception as e:
            logger.error(f"Failed to process signal notifications: {e}")
            raise

    async def get_daily_digest(self, workspace_id: str) -> Dict[str, Any]:
        """Get daily digest of notifications."""

        # Get today's notifications
        today = datetime.utcnow().date()

        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    SELECT
                        type,
                        priority,
                        status,
                        COUNT(*) as count,
                        COUNT(CASE WHEN read = FALSE THEN 1 END) as unread_count
                    FROM notifications
                    WHERE workspace_id = %s
                        AND DATE(created_at) = %s
                    GROUP BY type, priority, status
                    ORDER BY priority DESC, count DESC
                """
                await cur.execute(query, (workspace_id, today))
                results = await cur.fetchall()

                # Get top notifications
                top_query = """
                    SELECT id, title, message, type, priority, created_at, read
                    FROM notifications
                    WHERE workspace_id = %s
                        AND DATE(created_at) = %s
                    ORDER BY priority DESC, created_at DESC
                    LIMIT 10
                """
                await cur.execute(top_query, (workspace_id, today))
                top_results = await cur.fetchall()

        # Build digest
        total_notifications = sum(row[3] for row in results)
        total_unread = sum(row[4] for row in results)

        categories = {}
        priority_breakdown = {"low": 0, "normal": 0, "high": 0, "urgent": 0}

        for row in results:
            notif_type, priority, _, count, unread = row
            categories[notif_type] = categories.get(notif_type, 0) + count
            priority_breakdown[priority] = priority_breakdown.get(priority, 0) + count

        return {
            "date": today.isoformat(),
            "total_notifications": total_notifications,
            "unread_count": total_unread,
            "categories": categories,
            "priority_breakdown": priority_breakdown,
            "top_notifications": [
                {
                    "id": str(row[0]),
                    "title": row[1],
                    "message": row[2],
                    "type": row[3],
                    "priority": row[4],
                    "created_at": row[5].isoformat(),
                    "read": row[6],
                }
                for row in top_results
            ],
            "engagement_summary": {
                "read_rate": (
                    (total_notifications - total_unread) / total_notifications
                    if total_notifications > 0
                    else 0
                ),
                "total_categories": len(categories),
            },
        }

    async def get_user_notifications(
        self,
        workspace_id: str,
        user_id: str,
        status: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get notifications for a specific user with pagination."""

        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                # Build query with filters
                where_conditions = ["workspace_id = %s"]
                params = [workspace_id]

                if status:
                    where_conditions.append("status = %s")
                    params.append(status)

                if type:
                    where_conditions.append("type = %s")
                    params.append(type)

                where_clause = " AND ".join(where_conditions)

                query = f"""
                    SELECT
                        id, type, channel, title, message, subject, priority, status,
                        read, read_at, created_at, sent_at, delivered_at, metadata
                    FROM notifications
                    WHERE {where_clause}
                        AND recipients @> %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """
                params.extend([f'["{user_id}"]', limit, offset])

                await cur.execute(query, params)
                notifications = await cur.fetchall()

                # Get total count for pagination
                count_query = f"""
                    SELECT COUNT(*)
                    FROM notifications
                    WHERE {where_clause}
                        AND recipients @> %s
                """
                await cur.execute(count_query, params[:-2])  # Exclude limit and offset
                total_count = (await cur.fetchone())[0]

        return {
            "notifications": [
                {
                    "id": str(row[0]),
                    "type": row[1],
                    "channel": row[2],
                    "title": row[3],
                    "message": row[4],
                    "subject": row[5],
                    "priority": row[6],
                    "status": row[7],
                    "read": row[8],
                    "read_at": row[9].isoformat() if row[9] else None,
                    "created_at": row[10].isoformat(),
                    "sent_at": row[11].isoformat() if row[11] else None,
                    "delivered_at": row[12].isoformat() if row[12] else None,
                    "metadata": row[13],
                }
                for row in notifications
            ],
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count,
            },
        }

    async def mark_notification_read(
        self, workspace_id: str, notification_id: str, user_id: str
    ) -> bool:
        """Mark a notification as read for a user."""

        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    UPDATE notifications
                    SET read = TRUE, read_at = NOW()
                    WHERE id = %s AND workspace_id = %s AND recipients @> %s
                    RETURNING id
                """
                await cur.execute(
                    query, (notification_id, workspace_id, f'["{user_id}"]')
                )
                result = await cur.fetchone()

                return result is not None

    # Private helper methods
    async def _store_notification(
        self,
        workspace_id: str,
        notification_data: Dict[str, Any],
        recipients: List[str],
        channels: List[str],
        delivery_results: Dict[str, Any],
        delivery_summary: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> str:
        """Store notification in database."""

        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    INSERT INTO notifications (
                        workspace_id, tenant_id, type, channel, title, message,
                        subject, recipients, sender_id, priority, status,
                        delivery_results, created_at, metadata, template_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s)
                    RETURNING id
                """

                await cur.execute(
                    query,
                    (
                        workspace_id,
                        workspace_id,  # tenant_id same as workspace_id for now
                        notification_data.get("type", "informational"),
                        channels[0] if channels else "email",  # Primary channel
                        notification_data.get("subject", "Notification"),
                        notification_data.get("message"),
                        notification_data.get("subject"),
                        recipients,
                        user_id,
                        notification_data.get("priority", "normal"),
                        "sent",  # Status after successful send
                        delivery_results,
                        notification_data.get("metadata", {}),
                        notification_data.get("template_id"),
                    ),
                )

                result = await cur.fetchone()
                return str(result[0])

    async def _store_notification_schedule(
        self,
        workspace_id: str,
        notification_data: Dict[str, Any],
        recipients: List[str],
        channels: List[str],
        scheduled_at: datetime,
        frequency: str,
        end_date: Optional[datetime],
        max_occurrences: int,
        timezone: str,
        business_hours_only: bool,
        retry_failed: bool,
        max_retries: int,
        user_id: Optional[str] = None,
    ) -> str:
        """Store notification schedule in database."""

        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    INSERT INTO notification_schedules (
                        workspace_id, tenant_id, notification_data, recipients, channels,
                        scheduled_at, frequency, end_date, max_occurrences,
                        next_run, status, timezone, business_hours_only,
                        retry_failed, max_retries, created_by
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """

                await cur.execute(
                    query,
                    (
                        workspace_id,
                        workspace_id,
                        notification_data,
                        recipients,
                        channels,
                        scheduled_at,
                        frequency,
                        end_date,
                        max_occurrences,
                        scheduled_at,
                        "scheduled",
                        timezone,
                        business_hours_only,
                        retry_failed,
                        max_retries,
                        user_id,
                    ),
                )

                result = await cur.fetchone()
                return str(result[0])

    async def _get_user_preferences(
        self, workspace_id: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get user preferences from database."""

        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    SELECT * FROM notification_preferences
                    WHERE workspace_id = %s AND user_id = %s
                """
                await cur.execute(query, (workspace_id, user_id))
                result = await cur.fetchone()

                if result:
                    return {
                        "user_id": str(result[2]),
                        "email_notifications": result[3],
                        "sms_notifications": result[4],
                        "push_notifications": result[5],
                        "in_app_notifications": result[6],
                        "business_hours_only": result[7],
                        "quiet_hours_enabled": result[8],
                        "quiet_hours_start": result[9].strftime("%H:%M"),
                        "quiet_hours_end": result[10].strftime("%H:%M"),
                        "timezone": result[11],
                        "notification_types": result[12],
                    }
                return None

    async def _store_notification_template(
        self,
        workspace_id: str,
        template_data: Dict[str, Any],
        action: str,
        user_id: Optional[str] = None,
    ):
        """Store or update notification template in database."""

        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                if action == "create":
                    query = """
                        INSERT INTO notification_templates (
                            workspace_id, tenant_id, name, channel, subject, content,
                            variables, created_by
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """
                    await cur.execute(
                        query,
                        (
                            workspace_id,
                            workspace_id,
                            template_data.get("name"),
                            template_data.get("channel"),
                            template_data.get("subject"),
                            template_data.get("content"),
                            template_data.get("variables", []),
                            user_id,
                        ),
                    )
                elif action == "update":
                    query = """
                        UPDATE notification_templates
                        SET name = %s, channel = %s, subject = %s, content = %s,
                            variables = %s, updated_by = %s, updated_at = NOW()
                        WHERE workspace_id = %s AND id = %s
                    """
                    await cur.execute(
                        query,
                        (
                            template_data.get("name"),
                            template_data.get("channel"),
                            template_data.get("subject"),
                            template_data.get("content"),
                            template_data.get("variables", []),
                            user_id,
                            workspace_id,
                            template_data.get("template_id"),
                        ),
                    )

    async def _get_database_analytics(
        self, workspace_id: str, period: str
    ) -> Dict[str, Any]:
        """Get analytics from database."""

        # Calculate date range based on period
        end_date = datetime.utcnow()
        if period == "24_hours":
            start_date = end_date - timedelta(hours=24)
        elif period == "7_days":
            start_date = end_date - timedelta(days=7)
        elif period == "30_days":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=30)

        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                # Get basic stats
                query = """
                    SELECT
                        COUNT(*) as total_notifications,
                        COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                        COUNT(CASE WHEN read = TRUE THEN 1 END) as read,
                        COUNT(DISTINCT recipients) as unique_recipients
                    FROM notifications
                    WHERE workspace_id = %s AND created_at BETWEEN %s AND %s
                """
                await cur.execute(query, (workspace_id, start_date, end_date))
                stats = await cur.fetchone()

                # Get channel breakdown
                channel_query = """
                    SELECT channel, COUNT(*) as count
                    FROM notifications
                    WHERE workspace_id = %s AND created_at BETWEEN %s AND %s
                    GROUP BY channel
                """
                await cur.execute(channel_query, (workspace_id, start_date, end_date))
                channel_stats = await cur.fetchall()

        return {
            "total_notifications": stats[0],
            "delivered": stats[1],
            "failed": stats[2],
            "read": stats[3],
            "unique_recipients": stats[4],
            "delivery_rate": stats[1] / stats[0] if stats[0] > 0 else 0,
            "read_rate": stats[3] / stats[0] if stats[0] > 0 else 0,
            "channel_breakdown": {row[0]: row[1] for row in channel_stats},
        }

    async def _store_notification_from_radar(
        self, workspace_id: str, notification: Dict[str, Any]
    ):
        """Store notification generated from radar signals."""

        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    INSERT INTO notifications (
                        workspace_id, tenant_id, type, channel, title, message,
                        subject, recipients, priority, status, metadata, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """

                await cur.execute(
                    query,
                    (
                        workspace_id,
                        workspace_id,
                        notification.get("type", "alert"),
                        notification.get("channel", "in_app"),
                        notification.get("title", "Radar Alert"),
                        notification.get("message", ""),
                        notification.get("subject"),
                        notification.get("recipients", []),
                        notification.get("priority", "normal"),
                        "sent",
                        notification.get("metadata", {}),
                    ),
                )


def get_notification_service() -> NotificationService:
    """Dependency injection for NotificationService."""
    return NotificationService()
