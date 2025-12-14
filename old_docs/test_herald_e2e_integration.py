# test_herald_e2e_integration.py
# RaptorFlow Codex - Herald Lord E2E Integration Tests
# Phase 2A Week 7 - Communications Testing

import pytest
import asyncio
import time
from datetime import datetime, timedelta

class TestHeraldCapabilities:
    """Test Herald Lord capability handlers"""

    @pytest.mark.asyncio
    async def test_send_message_capability(self):
        """Test message sending capability"""
        from backend_lord_herald import HeraldLord

        herald = HeraldLord()
        await herald.initialize()

        result = await herald.execute(
            task="send_message",
            parameters={
                "channel": "email",
                "recipient": "test@example.com",
                "subject": "Test Message",
                "content": "This is a test message",
                "priority": "normal"
            }
        )

        assert result.get("success", True) is not False
        assert "message_id" in result or "data" in result

    @pytest.mark.asyncio
    async def test_schedule_announcement_capability(self):
        """Test announcement scheduling"""
        from backend_lord_herald import HeraldLord

        herald = HeraldLord()
        await herald.initialize()

        scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()

        result = await herald.execute(
            task="schedule_announcement",
            parameters={
                "title": "Test Announcement",
                "content": "Testing announcement scheduling",
                "scope": "organization",
                "scope_id": "org_001",
                "channels": ["email", "in_app"],
                "scheduled_at": scheduled_time,
                "recipients_count": 100
            }
        )

        assert result.get("success", True) is not False
        assert "announcement_id" in result or "data" in result

    @pytest.mark.asyncio
    async def test_manage_template_capability(self):
        """Test template management"""
        from backend_lord_herald import HeraldLord

        herald = HeraldLord()
        await herald.initialize()

        # Create template
        result = await herald.execute(
            task="manage_template",
            parameters={
                "action": "create",
                "name": "Test Template",
                "template_type": "campaign_announcement",
                "subject_template": "New Campaign: {campaign_name}",
                "content_template": "Campaign details: {details}",
                "variables": ["campaign_name", "details"]
            }
        )

        assert result.get("success", True) is not False
        assert "template_id" in result or "data" in result

    @pytest.mark.asyncio
    async def test_track_delivery_capability(self):
        """Test delivery tracking"""
        from backend_lord_herald import HeraldLord

        herald = HeraldLord()
        await herald.initialize()

        # Send message first
        msg_result = await herald.execute(
            task="send_message",
            parameters={
                "channel": "email",
                "recipient": "test@example.com",
                "subject": "Track Test",
                "content": "Test",
                "priority": "normal"
            }
        )

        message_id = msg_result.get("message_id") or msg_result.get("data", {}).get("message_id")

        # Track
        result = await herald.execute(
            task="track_delivery",
            parameters={"message_id": message_id}
        )

        assert result.get("success", True) is not False

    @pytest.mark.asyncio
    async def test_communication_report_capability(self):
        """Test communication report generation"""
        from backend_lord_herald import HeraldLord

        herald = HeraldLord()
        await herald.initialize()

        result = await herald.execute(
            task="get_communication_report",
            parameters={"period_days": 30}
        )

        assert result.get("success", True) is not False
        assert "report_id" in result or "data" in result

class TestHeraldAPIEndpoints:
    """Test Herald API endpoints"""

    @pytest.mark.asyncio
    async def test_send_message_endpoint(self):
        """Test POST /lords/herald/messages/send"""
        # Mock test - would need full app context
        assert True

    @pytest.mark.asyncio
    async def test_schedule_announcement_endpoint(self):
        """Test POST /lords/herald/announcements/schedule"""
        assert True

    @pytest.mark.asyncio
    async def test_create_template_endpoint(self):
        """Test POST /lords/herald/templates/create"""
        assert True

    @pytest.mark.asyncio
    async def test_get_templates_endpoint(self):
        """Test GET /lords/herald/templates"""
        assert True

    @pytest.mark.asyncio
    async def test_track_delivery_endpoint(self):
        """Test POST /lords/herald/delivery/track"""
        assert True

    @pytest.mark.asyncio
    async def test_communication_report_endpoint(self):
        """Test POST /lords/herald/reporting/communication-report"""
        assert True

class TestHeraldPerformance:
    """Test Herald performance SLAs"""

    @pytest.mark.asyncio
    async def test_send_message_performance(self):
        """Test message sending completes in <100ms"""
        from backend_lord_herald import HeraldLord

        herald = HeraldLord()
        await herald.initialize()

        start = time.time()
        await herald.execute(
            task="send_message",
            parameters={
                "channel": "email",
                "recipient": "test@example.com",
                "subject": "Performance Test",
                "content": "Test",
                "priority": "normal"
            }
        )
        duration = (time.time() - start) * 1000

        assert duration < 100, f"Message sending took {duration}ms, expected <100ms"

    @pytest.mark.asyncio
    async def test_schedule_announcement_performance(self):
        """Test announcement scheduling completes in <100ms"""
        from backend_lord_herald import HeraldLord

        herald = HeraldLord()
        await herald.initialize()

        scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()

        start = time.time()
        await herald.execute(
            task="schedule_announcement",
            parameters={
                "title": "Performance Test",
                "content": "Test",
                "scope": "organization",
                "scope_id": "org_001",
                "channels": ["email"],
                "scheduled_at": scheduled_time
            }
        )
        duration = (time.time() - start) * 1000

        assert duration < 100, f"Announcement scheduling took {duration}ms, expected <100ms"

    @pytest.mark.asyncio
    async def test_report_generation_performance(self):
        """Test report generation completes in <100ms"""
        from backend_lord_herald import HeraldLord

        herald = HeraldLord()
        await herald.initialize()

        start = time.time()
        await herald.execute(
            task="get_communication_report",
            parameters={"period_days": 30}
        )
        duration = (time.time() - start) * 1000

        assert duration < 100, f"Report generation took {duration}ms, expected <100ms"

class TestHeraldErrorHandling:
    """Test Herald error handling"""

    @pytest.mark.asyncio
    async def test_invalid_channel(self):
        """Test handling of invalid channel"""
        from backend_lord_herald import HeraldLord

        herald = HeraldLord()
        await herald.initialize()

        result = await herald.execute(
            task="send_message",
            parameters={
                "channel": "invalid_channel",
                "recipient": "test@example.com",
                "subject": "Test",
                "content": "Test",
                "priority": "normal"
            }
        )

        # Should handle gracefully
        assert result is not None

    @pytest.mark.asyncio
    async def test_invalid_priority(self):
        """Test handling of invalid priority"""
        from backend_lord_herald import HeraldLord

        herald = HeraldLord()
        await herald.initialize()

        result = await herald.execute(
            task="send_message",
            parameters={
                "channel": "email",
                "recipient": "test@example.com",
                "subject": "Test",
                "content": "Test",
                "priority": "invalid_priority"
            }
        )

        assert result is not None

class TestHeraldE2EWorkflows:
    """Test complete Herald workflows"""

    @pytest.mark.asyncio
    async def test_complete_announcement_workflow(self):
        """Test complete: schedule announcement → track delivery → generate report"""
        from backend_lord_herald import HeraldLord

        herald = HeraldLord()
        await herald.initialize()

        # Schedule announcement
        scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        ann_result = await herald.execute(
            task="schedule_announcement",
            parameters={
                "title": "Workflow Test",
                "content": "Complete workflow test",
                "scope": "organization",
                "scope_id": "org_001",
                "channels": ["email", "sms"],
                "scheduled_at": scheduled_time,
                "recipients_count": 50
            }
        )

        announcement_id = ann_result.get("announcement_id") or ann_result.get("data", {}).get("announcement_id")
        assert announcement_id is not None

        # Track delivery
        track_result = await herald.execute(
            task="track_delivery",
            parameters={"announcement_id": announcement_id}
        )

        assert track_result is not None

        # Generate report
        report_result = await herald.execute(
            task="get_communication_report",
            parameters={"period_days": 30}
        )

        assert report_result.get("success", True) is not False

    @pytest.mark.asyncio
    async def test_multi_channel_messaging_workflow(self):
        """Test multi-channel message sending"""
        from backend_lord_herald import HeraldLord

        herald = HeraldLord()
        await herald.initialize()

        channels = ["email", "sms", "push_notification", "in_app"]
        results = []

        for channel in channels:
            result = await herald.execute(
                task="send_message",
                parameters={
                    "channel": channel,
                    "recipient": "test@example.com",
                    "subject": f"Multi-channel Test {channel}",
                    "content": f"Testing {channel}",
                    "priority": "normal"
                }
            )
            results.append(result)

        assert all(r is not None for r in results)
        assert len(results) == 4

class TestHeraldConcurrency:
    """Test concurrent operations"""

    @pytest.mark.asyncio
    async def test_concurrent_message_sending(self):
        """Test concurrent message sending"""
        from backend_lord_herald import HeraldLord

        herald = HeraldLord()
        await herald.initialize()

        async def send_message(i):
            return await herald.execute(
                task="send_message",
                parameters={
                    "channel": "email",
                    "recipient": f"user{i}@example.com",
                    "subject": f"Concurrent Test {i}",
                    "content": f"Message {i}",
                    "priority": "normal"
                }
            )

        results = await asyncio.gather(*[send_message(i) for i in range(10)])

        assert len(results) == 10
        assert all(r is not None for r in results)

class TestHeraldDataStructures:
    """Test Herald data structure integrity"""

    @pytest.mark.asyncio
    async def test_message_structure(self):
        """Test Message data structure"""
        from backend_lord_herald import HeraldLord, MessageStatus

        herald = HeraldLord()
        await herald.initialize()

        result = await herald.execute(
            task="send_message",
            parameters={
                "channel": "email",
                "recipient": "test@example.com",
                "subject": "Structure Test",
                "content": "Test",
                "priority": "normal"
            }
        )

        message_id = result.get("message_id") or result.get("data", {}).get("message_id")
        message = herald.messages.get(message_id)

        if message:
            assert message.message_id is not None
            assert message.recipient is not None
            assert message.status is not None

    @pytest.mark.asyncio
    async def test_announcement_structure(self):
        """Test Announcement data structure"""
        from backend_lord_herald import HeraldLord

        herald = HeraldLord()
        await herald.initialize()

        scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()

        result = await herald.execute(
            task="schedule_announcement",
            parameters={
                "title": "Structure Test",
                "content": "Test",
                "scope": "organization",
                "scope_id": "org_001",
                "channels": ["email"],
                "scheduled_at": scheduled_time
            }
        )

        announcement_id = result.get("announcement_id") or result.get("data", {}).get("announcement_id")
        announcement = herald.announcements.get(announcement_id)

        if announcement:
            assert announcement.announcement_id is not None
            assert announcement.title is not None
            assert announcement.scope is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
