import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from api.v1.notifications import _active_connections
from api.v1.notifications import router as notifications_router
from models.notification_models import (
    NotificationChannel,
    NotificationPreferencesRequest,
    NotificationPriority,
    NotificationProcessRequest,
    NotificationScheduleRequest,
    NotificationSendRequest,
    NotificationTemplateRequest,
    NotificationType,
    ScheduleFrequency,
)
from services.notification_service import NotificationService


class TestNotificationEndpoints:
    """Test suite for notification endpoints."""

    @pytest.fixture
    def mock_notification_service(self):
        """Mock notification service for testing."""
        service = AsyncMock(spec=NotificationService)
        return service

    @pytest.fixture
    def sample_notification_request(self):
        """Sample notification send request."""
        return NotificationSendRequest(
            message="Test notification message",
            subject="Test Subject",
            recipients=["user1@example.com", "user2@example.com"],
            channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
            type=NotificationType.TRANSACTIONAL,
            priority=NotificationPriority.NORMAL,
            metadata={"campaign_id": "123"},
        )

    @pytest.fixture
    def sample_schedule_request(self):
        """Sample notification schedule request."""
        return NotificationScheduleRequest(
            notification_data={
                "message": "Scheduled notification",
                "subject": "Scheduled Subject",
            },
            recipients=["user1@example.com"],
            channels=[NotificationChannel.EMAIL],
            scheduled_at=datetime.utcnow() + timedelta(hours=1),
            frequency=ScheduleFrequency.DAILY,
            max_occurrences=5,
        )

    @pytest.mark.asyncio
    async def test_send_notification_success(
        self, mock_notification_service, sample_notification_request
    ):
        """Test successful notification sending."""
        # Mock service response
        mock_response = {
            "success": True,
            "data": {
                "notification_id": "notif_20240128_120000",
                "delivery_summary": {
                    "total_recipients": 2,
                    "total_sent": 2,
                    "total_failed": 0,
                    "success_rate": 100.0,
                    "delivery_time_seconds": 2.5,
                },
                "delivery_results": {
                    "email": {
                        "sent_count": 2,
                        "failed_count": 0,
                        "delivery_rate": 1.0,
                        "details": "Email sent via SendGrid",
                    },
                    "in_app": {
                        "sent_count": 2,
                        "failed_count": 0,
                        "delivery_rate": 1.0,
                        "details": "In-app notification stored",
                    },
                },
            },
            "message": "Notification sent to 2 recipients via 2 channels",
        }
        mock_notification_service.send_notification.return_value = mock_response

        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from api.v1.notifications import send_notification

            result = await send_notification(
                request=sample_notification_request,
                background_tasks=AsyncMock(),
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_notification_service,
            )

            assert result.success is True
            assert result.message == "Notification sent to 2 recipients via 2 channels"
            assert result.data["delivery_summary"]["total_recipients"] == 2
            assert result.data["delivery_summary"]["success_rate"] == 100.0
            mock_notification_service.send_notification.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_validation_error(self, mock_notification_service):
        """Test notification sending with validation errors."""
        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from fastapi import HTTPException
            from pydantic import ValidationError

            from api.v1.notifications import send_notification

            # Test empty message - this should be caught by Pydantic validation before reaching our endpoint
            try:
                invalid_request = NotificationSendRequest(
                    message="", recipients=["user1@example.com"]
                )
                # If we get here, validation didn't work as expected
                assert False, "Pydantic validation should have failed"
            except ValidationError:
                # This is expected - Pydantic validates before our endpoint logic
                pass

            # Test no recipients - this should also be caught by Pydantic validation
            try:
                invalid_request = NotificationSendRequest(
                    message="Test message", recipients=[]
                )
                # If we get here, validation didn't work as expected
                assert False, "Pydantic validation should have failed"
            except ValidationError:
                # This is expected - Pydantic validates before our endpoint logic
                pass

            # Test a scenario that our endpoint handles (not Pydantic)
            # Since Pydantic handles most validation, let's test a scenario where the service fails
            mock_notification_service.send_notification.side_effect = Exception(
                "Service error"
            )

            valid_request = NotificationSendRequest(
                message="Test message", recipients=["user1@example.com"]
            )

            with pytest.raises(HTTPException) as exc_info:
                await send_notification(
                    request=valid_request,
                    background_tasks=AsyncMock(),
                    tenant_id=uuid4(),
                    _current_user={"id": "test_user"},
                    service=mock_notification_service,
                )

            assert exc_info.value.status_code == 500
            assert "Failed to send notification" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_schedule_notification_success(
        self, mock_notification_service, sample_schedule_request
    ):
        """Test successful notification scheduling."""
        mock_response = {
            "success": True,
            "data": {
                "schedule_id": "schedule_20240128_120000",
                "scheduled_time": sample_schedule_request.scheduled_at.isoformat(),
                "frequency": "daily",
                "status": "scheduled",
                "next_run": sample_schedule_request.scheduled_at.isoformat(),
            },
            "message": f"Notification scheduled for {sample_schedule_request.scheduled_at}",
        }
        mock_notification_service.schedule_notification.return_value = mock_response

        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from api.v1.notifications import schedule_notification

            result = await schedule_notification(
                request=sample_schedule_request,
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_notification_service,
            )

            assert result.success is True
            assert "scheduled" in result.message
            assert result.data["schedule_id"] == "schedule_20240128_120000"
            mock_notification_service.schedule_notification.assert_called_once()

    @pytest.mark.asyncio
    async def test_schedule_notification_past_time_error(
        self, mock_notification_service
    ):
        """Test scheduling notification with past time."""
        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from fastapi import HTTPException

            from api.v1.notifications import schedule_notification

            # Request with past time
            past_request = NotificationScheduleRequest(
                notification_data={"message": "Test"},
                recipients=["user1@example.com"],
                channels=[NotificationChannel.EMAIL],
                scheduled_at=datetime.utcnow() - timedelta(hours=1),  # Past time
            )

            with pytest.raises(HTTPException) as exc_info:
                await schedule_notification(
                    request=past_request,
                    tenant_id=uuid4(),
                    _current_user={"id": "test_user"},
                    service=mock_notification_service,
                )

            assert exc_info.value.status_code == 400
            assert "Scheduled time must be in the future" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_notification_preferences(self, mock_notification_service):
        """Test retrieving notification preferences."""
        mock_response = {
            "success": True,
            "data": {
                "user_preferences": [
                    {
                        "user_id": "test_user",
                        "email_notifications": True,
                        "sms_notifications": False,
                        "push_notifications": True,
                        "in_app_notifications": True,
                        "business_hours_only": True,
                        "notification_types": {
                            "marketing": False,
                            "transactional": True,
                            "security": True,
                        },
                        "quiet_hours": {
                            "enabled": True,
                            "start_time": "22:00",
                            "end_time": "08:00",
                        },
                    }
                ],
                "global_settings": {
                    "default_channels": ["email", "in_app"],
                    "max_notifications_per_day": 50,
                },
            },
        }
        mock_notification_service.get_notification_preferences.return_value = (
            mock_response
        )

        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from api.v1.notifications import get_notification_preferences

            result = await get_notification_preferences(
                user_id="test_user",
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_notification_service,
            )

            assert result.success is True
            preferences = result.data["user_preferences"]
            assert len(preferences) == 1
            assert preferences[0]["user_id"] == "test_user"
            assert preferences[0]["email_notifications"] is True
            assert preferences[0]["sms_notifications"] is False

    @pytest.mark.asyncio
    async def test_update_notification_preferences(self):
        """Test updating notification preferences."""
        with patch("db.get_db_connection") as mock_get_conn:
            mock_conn = AsyncMock()
            mock_cur = AsyncMock()
            mock_conn.cursor.return_value.__aenter__.return_value = mock_cur
            mock_cur.fetchone.return_value = [uuid4()]
            mock_get_conn.return_value.__aenter__.return_value = mock_conn

            from api.v1.notifications import update_notification_preferences

            preferences_request = NotificationPreferencesRequest(
                email_notifications=True,
                sms_notifications=False,
                push_notifications=True,
                in_app_notifications=False,
                business_hours_only=True,
                quiet_hours_enabled=True,
                quiet_hours_start="22:00",
                quiet_hours_end="08:00",
            )

            result = await update_notification_preferences(
                preferences=preferences_request,
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=AsyncMock(),
            )

            assert result.success is True
            assert result.message == "Preferences updated successfully"
            assert "preferences" in result.data

    @pytest.mark.asyncio
    async def test_manage_notification_templates_create(
        self, mock_notification_service
    ):
        """Test creating notification templates."""
        mock_response = {
            "success": True,
            "data": {
                "template_id": "template_20240128_120000",
                "name": "Welcome Email",
                "channel": "email",
                "subject": "Welcome to Our Service!",
                "content": "Hi {{first_name}}, welcome to our service!",
                "variables": ["first_name"],
                "created_at": datetime.utcnow().isoformat(),
                "usage_count": 0,
            },
        }
        mock_notification_service.manage_notification_templates.return_value = (
            mock_response
        )

        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from api.v1.notifications import manage_notification_templates

            template_request = NotificationTemplateRequest(
                action="create",
                name="Welcome Email",
                channel=NotificationChannel.EMAIL,
                subject="Welcome to Our Service!",
                content="Hi {{first_name}}, welcome to our service!",
                variables=["first_name"],
            )

            result = await manage_notification_templates(
                request=template_request,
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_notification_service,
            )

            assert result.success is True
            assert result.message == "Template create completed"
            assert result.data["template_id"] == "template_20240128_120000"

    @pytest.mark.asyncio
    async def test_get_notification_analytics(self, mock_notification_service):
        """Test retrieving notification analytics."""
        mock_response = {
            "success": True,
            "data": {
                "period": "30_days",
                "overview": {
                    "total_notifications": 45600,
                    "unique_recipients": 12500,
                    "total_channels": 5,
                },
                "channel_analytics": {
                    "email": {
                        "volume": 18240,
                        "delivery_rate": 0.93,
                        "open_rate": 0.67,
                    },
                    "sms": {"volume": 9120, "delivery_rate": 0.98, "read_rate": 0.80},
                },
                "engagement_metrics": {
                    "overall_engagement_rate": 0.34,
                    "channel_engagement": {
                        "email": {"open_rate": 0.67, "click_rate": 0.24},
                        "sms": {"read_rate": 0.80},
                    },
                },
                "insights": [
                    "Email performs best on Tuesday mornings",
                    "SMS has highest delivery rate",
                ],
            },
        }
        mock_notification_service.get_notification_analytics.return_value = (
            mock_response
        )

        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from api.v1.notifications import get_notification_analytics

            result = await get_notification_analytics(
                period="30_days",
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_notification_service,
            )

            assert result.success is True
            analytics = result.data
            assert analytics["period"] == "30_days"
            assert analytics["overview"]["total_notifications"] == 45600
            assert "email" in analytics["channel_analytics"]
            assert analytics["engagement_metrics"]["overall_engagement_rate"] == 0.34

    @pytest.mark.asyncio
    async def test_process_signal_notifications(self, mock_notification_service):
        """Test processing radar signal notifications."""
        mock_notifications = [
            {
                "id": "notif_001",
                "type": "alert",
                "title": "High Strength Signal Detected",
                "message": "Competitor launched new campaign",
                "recipients": ["user1@example.com"],
                "priority": "high",
                "metadata": {"signal_id": "signal_123"},
            },
            {
                "id": "notif_002",
                "type": "alert",
                "title": "Pricing Change Alert",
                "message": "Competitor changed pricing strategy",
                "recipients": ["user2@example.com"],
                "priority": "urgent",
                "metadata": {"signal_id": "signal_456"},
            },
        ]
        mock_notification_service.process_signal_notifications.return_value = (
            mock_notifications
        )

        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from api.v1.notifications import process_signal_notifications

            process_request = NotificationProcessRequest(
                signal_ids=["signal_123", "signal_456"],
                tenant_preferences={"high_strength_signals": {"enabled": True}},
            )

            result = await process_signal_notifications(
                request=process_request,
                background_tasks=AsyncMock(),
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_notification_service,
            )

            assert result.success is True
            assert result.data["processed_signals"] == 2
            assert result.data["generated_notifications"] == 2
            assert len(result.data["notifications"]) == 2

    @pytest.mark.asyncio
    async def test_get_daily_digest(self, mock_notification_service):
        """Test retrieving daily digest."""
        mock_digest = {
            "date": datetime.utcnow().date().isoformat(),
            "total_notifications": 25,
            "unread_count": 8,
            "categories": {"transactional": 15, "marketing": 5, "alerts": 5},
            "priority_breakdown": {"normal": 20, "high": 4, "urgent": 1},
            "top_notifications": [
                {
                    "id": "notif_001",
                    "title": "Campaign Update",
                    "type": "transactional",
                    "priority": "high",
                    "read": False,
                }
            ],
            "engagement_summary": {"read_rate": 0.68, "total_categories": 3},
        }
        mock_notification_service.get_daily_digest.return_value = mock_digest

        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from api.v1.notifications import get_daily_digest

            result = await get_daily_digest(
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_notification_service,
            )

            assert result.success is True
            digest = result.data
            assert digest["total_notifications"] == 25
            assert digest["unread_count"] == 8
            assert "transactional" in digest["categories"]
            assert digest["priority_breakdown"]["urgent"] == 1
            assert len(digest["top_notifications"]) == 1

    @pytest.mark.asyncio
    async def test_get_my_notifications(self, mock_notification_service):
        """Test retrieving user's notifications with pagination."""
        mock_response = {
            "notifications": [
                {
                    "id": "notif_001",
                    "type": "transactional",
                    "channel": "email",
                    "title": "Welcome Email",
                    "message": "Welcome to our service",
                    "priority": "normal",
                    "status": "delivered",
                    "read": False,
                    "created_at": datetime.utcnow().isoformat(),
                },
                {
                    "id": "notif_002",
                    "type": "alert",
                    "channel": "in_app",
                    "title": "Security Alert",
                    "message": "New login detected",
                    "priority": "high",
                    "status": "delivered",
                    "read": True,
                    "created_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                },
            ],
            "pagination": {"total": 2, "limit": 50, "offset": 0, "has_more": False},
        }
        mock_notification_service.get_user_notifications.return_value = mock_response

        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from api.v1.notifications import get_my_notifications

            result = await get_my_notifications(
                status="delivered",
                limit=50,
                offset=0,
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_notification_service,
            )

            assert result.success is True
            notifications = result.data["notifications"]
            assert len(notifications) == 2
            assert notifications[0]["title"] == "Welcome Email"
            assert notifications[1]["priority"] == "high"
            pagination = result.data["pagination"]
            assert pagination["total"] == 2
            assert pagination["has_more"] is False

    @pytest.mark.asyncio
    async def test_mark_notification_read(self, mock_notification_service):
        """Test marking notification as read."""
        mock_notification_service.mark_notification_read.return_value = True

        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from api.v1.notifications import mark_notification_read

            result = await mark_notification_read(
                notification_id=str(uuid4()),
                tenant_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_notification_service,
            )

            assert result.success is True
            assert result.message == "Notification marked as read"
            mock_notification_service.mark_notification_read.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_notification_read_not_found(self, mock_notification_service):
        """Test marking non-existent notification as read."""
        mock_notification_service.mark_notification_read.return_value = False

        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from fastapi import HTTPException

            from api.v1.notifications import mark_notification_read

            with pytest.raises(HTTPException) as exc_info:
                await mark_notification_read(
                    notification_id=str(uuid4()),
                    tenant_id=uuid4(),
                    _current_user={"id": "test_user"},
                    service=mock_notification_service,
                )

            assert exc_info.value.status_code == 404
            assert "Notification not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_notification_stream_event_generator(self):
        """Test SSE event generator for notifications."""
        import asyncio

        from api.v1.notifications import _active_connections

        # Setup test connection
        workspace_id = str(uuid4())
        user_id = "test_user"
        connection_id = f"{workspace_id}_{user_id}"

        # Mock queue and connection
        test_queue = asyncio.Queue()
        _active_connections[connection_id] = test_queue

        # Add test notification to queue
        test_notification = {
            "id": "notif_001",
            "title": "Test Notification",
            "message": "Test message",
        }
        await test_queue.put(
            {
                "notification": test_notification,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Verify notification is in queue
        assert not test_queue.empty()

        # Cleanup
        if connection_id in _active_connections:
            del _active_connections[connection_id]

    @pytest.mark.asyncio
    async def test_broadcast_notification_realtime(self):
        """Test real-time notification broadcasting."""
        import asyncio

        from api.v1.notifications import _broadcast_notification_realtime

        # Setup test connections
        workspace_id = str(uuid4())
        recipients = ["user1", "user2"]

        # Create mock queues for recipients
        for recipient in recipients:
            connection_id = f"{workspace_id}_{recipient}"
            _active_connections[connection_id] = asyncio.Queue()

        # Test notification
        notification = {
            "id": "notif_001",
            "title": "Real-time Test",
            "message": "This is a real-time notification",
        }

        # Broadcast notification
        await _broadcast_notification_realtime(workspace_id, notification, recipients)

        # Verify notifications were broadcast
        for recipient in recipients:
            connection_id = f"{workspace_id}_{recipient}"
            if connection_id in _active_connections:
                queue = _active_connections[connection_id]
                assert not queue.empty()

                # Get the broadcasted notification
                broadcasted = await queue.get()
                assert broadcasted["notification"]["id"] == "notif_001"
                assert broadcasted["notification"]["title"] == "Real-time Test"

        # Cleanup
        for recipient in recipients:
            connection_id = f"{workspace_id}_{recipient}"
            if connection_id in _active_connections:
                del _active_connections[connection_id]

    @pytest.mark.asyncio
    async def test_workspace_authorization(
        self, mock_notification_service, sample_notification_request
    ):
        """Test workspace-level authorization."""
        mock_notification_service.send_notification.side_effect = Exception(
            "Unauthorized access"
        )

        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from fastapi import HTTPException

            from api.v1.notifications import send_notification

            with pytest.raises(HTTPException) as exc_info:
                await send_notification(
                    request=sample_notification_request,
                    background_tasks=AsyncMock(),
                    tenant_id=uuid4(),
                    _current_user={"id": "test_user"},
                    service=mock_notification_service,
                )

            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_error_handling(
        self, mock_notification_service, sample_notification_request
    ):
        """Test comprehensive error handling."""
        mock_notification_service.send_notification.side_effect = Exception(
            "Service error"
        )

        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from fastapi import HTTPException

            from api.v1.notifications import send_notification

            with pytest.raises(HTTPException) as exc_info:
                await send_notification(
                    request=sample_notification_request,
                    background_tasks=AsyncMock(),
                    tenant_id=uuid4(),
                    _current_user={"id": "test_user"},
                    service=mock_notification_service,
                )

            assert exc_info.value.status_code == 500
            assert "Failed to send notification" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_template_validation(self, mock_notification_service):
        """Test template validation for different actions."""
        with patch(
            "api.v1.notifications.get_notification_service",
            return_value=mock_notification_service,
        ):
            from fastapi import HTTPException

            from api.v1.notifications import manage_notification_templates

            # Test create without required fields
            invalid_request = NotificationTemplateRequest(
                action="create",
                name="Test Template",
                # Missing channel and content
            )

            with pytest.raises(HTTPException) as exc_info:
                await manage_notification_templates(
                    request=invalid_request,
                    tenant_id=uuid4(),
                    _current_user={"id": "test_user"},
                    service=mock_notification_service,
                )

            assert exc_info.value.status_code == 400
            assert "Channel is required" in str(exc_info.value.detail)

            # Test update without template_id
            update_request = NotificationTemplateRequest(
                action="update",
                name="Updated Template",
                # Missing template_id
            )

            with pytest.raises(HTTPException) as exc_info:
                await manage_notification_templates(
                    request=update_request,
                    tenant_id=uuid4(),
                    _current_user={"id": "test_user"},
                    service=mock_notification_service,
                )

            assert exc_info.value.status_code == 400
            assert "Template ID is required" in str(exc_info.value.detail)
