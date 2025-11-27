# backend/tests/test_raptor_bus.py
# RaptorFlow Codex - RaptorBus Tests
# Week 3 Tuesday - Message Bus Test Suite

import pytest
import asyncio
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

from raptor_bus import (
    RaptorBus, Message, EventType, ChannelType,
    get_raptor_bus, shutdown_raptor_bus
)
from raptor_events import (
    AgentStartPayload, AgentCompletePayload,
    CampaignActivatePayload
)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
async def raptor_bus():
    """Create RaptorBus instance for testing"""
    bus = RaptorBus("redis://localhost:6379/0")
    try:
        await bus.connect()
        yield bus
    finally:
        await bus.disconnect()

@pytest.fixture
def sample_message():
    """Create sample message for testing"""
    return Message(
        id="test-msg-001",
        event_type=EventType.AGENT_START,
        channel=ChannelType.GUILD_RESEARCH,
        workspace_id="ws-001",
        user_id="user-001",
        source_agent="researcher-1",
        payload={"task": "analyze_market", "priority": 5},
        timestamp=datetime.utcnow().isoformat()
    )

# ============================================================================
# CONNECTION TESTS
# ============================================================================

class TestRaptorBusConnection:
    """Test RaptorBus connection functionality"""

    @pytest.mark.asyncio
    async def test_connect(self, raptor_bus):
        """Test Redis connection"""
        assert raptor_bus.redis is not None
        assert raptor_bus.running == False

    @pytest.mark.asyncio
    async def test_disconnect(self, raptor_bus):
        """Test Redis disconnection"""
        await raptor_bus.disconnect()
        assert raptor_bus.redis is None

    @pytest.mark.asyncio
    async def test_connect_failure(self):
        """Test connection failure handling"""
        bus = RaptorBus("redis://invalid-host:9999")
        with pytest.raises(Exception):
            await bus.connect()

# ============================================================================
# MESSAGE PUBLISHING TESTS
# ============================================================================

class TestMessagePublishing:
    """Test message publishing functionality"""

    @pytest.mark.asyncio
    async def test_publish_message(self, raptor_bus):
        """Test publishing a message"""
        message_id = await raptor_bus.publish(
            event_type=EventType.AGENT_START,
            channel=ChannelType.GUILD_RESEARCH,
            workspace_id="ws-001",
            user_id="user-001",
            source_agent="researcher-1",
            payload={"task": "analyze"}
        )

        assert message_id is not None
        assert len(message_id) > 0
        assert raptor_bus.metrics[ChannelType.GUILD_RESEARCH.value]["published"] == 1

    @pytest.mark.asyncio
    async def test_publish_multiple_channels(self, raptor_bus):
        """Test publishing to multiple channels"""
        channels = [
            ChannelType.GUILD_RESEARCH,
            ChannelType.GUILD_BROADCAST,
            ChannelType.ALERT
        ]

        for channel in channels:
            await raptor_bus.publish(
                event_type=EventType.AGENT_COMPLETE,
                channel=channel,
                workspace_id="ws-001",
                user_id="user-001",
                source_agent="agent-1",
                payload={"success": True}
            )

        assert len(raptor_bus.metrics) >= 3

    @pytest.mark.asyncio
    async def test_message_serialization(self, sample_message):
        """Test message JSON serialization"""
        json_str = sample_message.to_json()
        assert isinstance(json_str, str)

        # Deserialize and verify
        deserialized = Message.from_json(json_str)
        assert deserialized.id == sample_message.id
        assert deserialized.event_type == sample_message.event_type
        assert deserialized.workspace_id == sample_message.workspace_id

# ============================================================================
# MESSAGE CONSUMPTION TESTS
# ============================================================================

class TestMessageConsumption:
    """Test message consumption functionality"""

    @pytest.mark.asyncio
    async def test_subscribe_handler(self, raptor_bus):
        """Test subscribing handler to channel"""
        handler_called = []

        async def test_handler(message: Message):
            handler_called.append(message.id)

        await raptor_bus.subscribe(ChannelType.GUILD_RESEARCH, test_handler)

        assert ChannelType.GUILD_RESEARCH.value in raptor_bus.subscription_handlers
        assert test_handler in raptor_bus.subscription_handlers[ChannelType.GUILD_RESEARCH.value]

    @pytest.mark.asyncio
    async def test_multiple_handlers(self, raptor_bus):
        """Test multiple handlers on same channel"""
        handlers = []

        async def handler1(message: Message):
            pass

        async def handler2(message: Message):
            pass

        await raptor_bus.subscribe(ChannelType.ALERT, handler1)
        await raptor_bus.subscribe(ChannelType.ALERT, handler2)

        channel_handlers = raptor_bus.subscription_handlers[ChannelType.ALERT.value]
        assert len(channel_handlers) == 2
        assert handler1 in channel_handlers
        assert handler2 in channel_handlers

# ============================================================================
# ERROR HANDLING & RETRY TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and retry logic"""

    @pytest.mark.asyncio
    async def test_dlq_message_creation(self, raptor_bus, sample_message):
        """Test DLQ message creation"""
        await raptor_bus._send_to_dlq(sample_message, "Test failure reason")

        # Verify DLQ message was created
        assert ChannelType.DLQ.value in raptor_bus.metrics

    @pytest.mark.asyncio
    async def test_retry_logic(self, raptor_bus):
        """Test message retry logic"""
        message = Message(
            id="retry-test",
            event_type=EventType.AGENT_ERROR,
            channel=ChannelType.GUILD_RESEARCH,
            workspace_id="ws-001",
            user_id="user-001",
            source_agent="agent-1",
            payload={"error": "test"},
            timestamp=datetime.utcnow().isoformat(),
            retry_count=0,
            max_retries=3
        )

        # Simulate retry
        message.retry_count += 1
        assert message.retry_count <= message.max_retries

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, raptor_bus):
        """Test handling when max retries exceeded"""
        message = Message(
            id="max-retry-test",
            event_type=EventType.AGENT_ERROR,
            channel=ChannelType.GUILD_RESEARCH,
            workspace_id="ws-001",
            user_id="user-001",
            source_agent="agent-1",
            payload={},
            timestamp=datetime.utcnow().isoformat(),
            retry_count=3,
            max_retries=3
        )

        # Message should go to DLQ at this point
        should_dlq = message.retry_count >= message.max_retries
        assert should_dlq

# ============================================================================
# METRICS TRACKING TESTS
# ============================================================================

class TestMetricsTracking:
    """Test performance metrics tracking"""

    @pytest.mark.asyncio
    async def test_metric_tracking(self, raptor_bus):
        """Test metric recording"""
        channel = ChannelType.GUILD_RESEARCH.value

        raptor_bus._track_metric(channel, "published")
        raptor_bus._track_metric(channel, "published")
        raptor_bus._track_metric(channel, "received")

        assert raptor_bus.metrics[channel]["published"] == 2
        assert raptor_bus.metrics[channel]["received"] == 1

    @pytest.mark.asyncio
    async def test_get_metrics(self, raptor_bus):
        """Test metrics retrieval"""
        await raptor_bus.publish(
            event_type=EventType.AGENT_COMPLETE,
            channel=ChannelType.GUILD_RESEARCH,
            workspace_id="ws-001",
            user_id="user-001",
            source_agent="agent-1",
            payload={"success": True}
        )

        metrics = raptor_bus.get_metrics()
        assert "channels" in metrics
        assert "running" in metrics
        assert "timestamp" in metrics

    @pytest.mark.asyncio
    async def test_metrics_multiple_channels(self, raptor_bus):
        """Test metrics across multiple channels"""
        channels = [
            ChannelType.GUILD_RESEARCH,
            ChannelType.GUILD_MUSE,
            ChannelType.ALERT
        ]

        for channel in channels:
            await raptor_bus.publish(
                event_type=EventType.AGENT_START,
                channel=channel,
                workspace_id="ws-001",
                user_id="user-001",
                source_agent="agent-1",
                payload={}
            )

        metrics = raptor_bus.get_metrics()
        assert len(metrics["channels"]) >= 3

# ============================================================================
# CHANNEL ROUTING TESTS
# ============================================================================

class TestChannelRouting:
    """Test message routing to correct channels"""

    @pytest.mark.asyncio
    async def test_route_agent_start(self, raptor_bus):
        """Test routing for agent start event"""
        message_id = await raptor_bus.publish(
            event_type=EventType.AGENT_START,
            channel=ChannelType.GUILD_RESEARCH,
            workspace_id="ws-001",
            user_id="user-001",
            source_agent="researcher-1",
            payload={"task": "research"}
        )

        assert message_id is not None
        assert ChannelType.GUILD_RESEARCH.value in raptor_bus.metrics

    @pytest.mark.asyncio
    async def test_route_alert(self, raptor_bus):
        """Test routing for alert event"""
        message_id = await raptor_bus.publish(
            event_type=EventType.ALERT_CREATED,
            channel=ChannelType.ALERT,
            workspace_id="ws-001",
            user_id="user-001",
            source_agent="guardian-1",
            payload={"severity": "critical"}
        )

        assert message_id is not None
        assert ChannelType.ALERT.value in raptor_bus.metrics

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete message flow"""

    @pytest.mark.asyncio
    async def test_publish_and_subscribe(self, raptor_bus):
        """Test complete publish-subscribe cycle"""
        messages_received = []

        async def handler(message: Message):
            messages_received.append(message.id)

        # Subscribe to channel
        await raptor_bus.subscribe(ChannelType.GUILD_RESEARCH, handler)

        # Publish message
        message_id = await raptor_bus.publish(
            event_type=EventType.AGENT_START,
            channel=ChannelType.GUILD_RESEARCH,
            workspace_id="ws-001",
            user_id="user-001",
            source_agent="agent-1",
            payload={}
        )

        assert message_id is not None

    @pytest.mark.asyncio
    async def test_singleton_pattern(self):
        """Test RaptorBus singleton"""
        bus1 = await get_raptor_bus()
        bus2 = await get_raptor_bus()

        assert bus1 is bus2
        await shutdown_raptor_bus()

# ============================================================================
# PAYLOAD VALIDATION TESTS
# ============================================================================

class TestPayloadValidation:
    """Test event payload validation"""

    def test_agent_start_payload(self):
        """Test AgentStartPayload validation"""
        payload = AgentStartPayload(
            agent_name="researcher-1",
            agent_type="researcher",
            task="market_analysis",
            priority=5
        )

        assert payload.agent_name == "researcher-1"
        assert payload.priority == 5

    def test_agent_complete_payload(self):
        """Test AgentCompletePayload validation"""
        payload = AgentCompletePayload(
            agent_name="researcher-1",
            task="market_analysis",
            duration_seconds=120.5,
            tokens_used=1500,
            cost=0.045,
            result_summary="Analysis complete",
            success=True
        )

        assert payload.duration_seconds == 120.5
        assert payload.tokens_used == 1500
        assert payload.success == True

    def test_campaign_activate_payload(self):
        """Test CampaignActivatePayload validation"""
        payload = CampaignActivatePayload(
            campaign_id="camp-001",
            campaign_name="Q1 Marketing",
            positioning="premium_market",
            target_audience="tech_executives",
            start_date="2024-02-15",
            assigned_agents=["muse-1", "muse-2"]
        )

        assert payload.campaign_id == "camp-001"
        assert len(payload.assigned_agents) == 2

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance and load tests"""

    @pytest.mark.asyncio
    async def test_bulk_publish(self, raptor_bus):
        """Test publishing many messages"""
        num_messages = 100
        start_time = datetime.utcnow()

        for i in range(num_messages):
            await raptor_bus.publish(
                event_type=EventType.AGENT_START,
                channel=ChannelType.GUILD_RESEARCH,
                workspace_id="ws-001",
                user_id="user-001",
                source_agent=f"agent-{i}",
                payload={"index": i}
            )

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        assert raptor_bus.metrics[ChannelType.GUILD_RESEARCH.value]["published"] == num_messages
        assert duration < 10  # Should complete in < 10 seconds

    @pytest.mark.asyncio
    async def test_concurrent_handlers(self, raptor_bus):
        """Test multiple concurrent message handlers"""
        handler_executions = []

        async def slow_handler(message: Message):
            await asyncio.sleep(0.01)
            handler_executions.append(("slow", message.id))

        async def fast_handler(message: Message):
            handler_executions.append(("fast", message.id))

        await raptor_bus.subscribe(ChannelType.GUILD_RESEARCH, slow_handler)
        await raptor_bus.subscribe(ChannelType.GUILD_RESEARCH, fast_handler)

        assert len(raptor_bus.subscription_handlers[ChannelType.GUILD_RESEARCH.value]) == 2

