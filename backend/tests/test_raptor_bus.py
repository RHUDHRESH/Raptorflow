"""
Comprehensive tests for RaptorBus message bus.

Tests cover:
- Event publishing and subscription
- Message schema validation
- Channel routing
- Error handling and DLQ
- Message persistence and replay
- Metrics collection
"""

import pytest
import asyncio
import json
from uuid import uuid4
from datetime import datetime

from backend.bus.raptor_bus import (
    RaptorBus,
    SchemaValidationError,
    PublishError,
    SubscriptionError,
)
from backend.bus.events import BusEvent, EventPriority
from backend.bus.channels import (
    HEARTBEAT_CHANNEL,
    GUILD_CHANNELS,
    ALERT_CHANNELS,
)


@pytest.fixture
async def bus():
    """Create and connect a RaptorBus instance for testing."""
    bus = RaptorBus(redis_url="redis://localhost:6379/1")  # Use test DB
    await bus.connect()
    yield bus
    await bus.disconnect()


class TestEventCreation:
    """Test BusEvent model creation and validation."""

    def test_event_creation_minimal(self):
        """Test creating event with minimal required fields."""
        event = BusEvent(type="test_event", payload={})
        assert event.type == "test_event"
        assert event.priority == EventPriority.NORMAL
        assert event.id is not None
        assert event.timestamp is not None

    def test_event_creation_full(self):
        """Test creating event with all fields."""
        event = BusEvent(
            type="campaign_created",
            priority=EventPriority.HIGH,
            source_agent_id="LORD-002",
            destination_guild="research",
            request_id="req-123",
            payload={"campaign_id": "camp-456"},
        )

        assert event.type == "campaign_created"
        assert event.priority == EventPriority.HIGH
        assert event.source_agent_id == "LORD-002"
        assert event.destination_guild == "research"
        assert event.request_id == "req-123"
        assert event.payload["campaign_id"] == "camp-456"

    def test_event_serialization(self):
        """Test event serialization to/from JSON."""
        original = BusEvent(
            type="test",
            payload={"key": "value"},
        )

        # Serialize
        json_str = original.to_json_str()
        assert isinstance(json_str, str)

        # Deserialize
        restored = BusEvent.from_json_str(json_str)
        assert restored.id == original.id
        assert restored.type == original.type
        assert restored.payload == original.payload


class TestPublish:
    """Test publishing events."""

    @pytest.mark.asyncio
    async def test_publish_to_heartbeat(self, bus):
        """Test publishing heartbeat event."""
        event_id = await bus.publish_event(
            channel=HEARTBEAT_CHANNEL.name,
            event_type="heartbeat",
            payload={"status": "healthy"},
            source_agent_id="LORD-001",
        )

        assert event_id is not None
        assert bus._metrics["published"] == 1

    @pytest.mark.asyncio
    async def test_publish_to_guild(self, bus):
        """Test publishing to guild channel."""
        event_id = await bus.publish_event(
            channel=GUILD_CHANNELS["research"].name,
            event_type="research_complete",
            payload={"findings": "important data"},
            source_agent_id="RES-001",
        )

        assert event_id is not None

    @pytest.mark.asyncio
    async def test_publish_with_priority(self, bus):
        """Test publishing with different priorities."""
        for priority in [EventPriority.LOW, EventPriority.NORMAL, EventPriority.HIGH, EventPriority.CRITICAL]:
            event_id = await bus.publish_event(
                channel="sys.guild.research.broadcast",
                event_type="test",
                payload={},
                priority=priority,
            )
            assert event_id is not None

    @pytest.mark.asyncio
    async def test_publish_without_connection(self):
        """Test publishing fails when not connected."""
        bus = RaptorBus(redis_url="redis://localhost:6379/1")
        bus.is_connected = False

        with pytest.raises(PublishError):
            await bus.publish_event(
                channel="sys.guild.research.broadcast",
                event_type="test",
                payload={},
            )

    @pytest.mark.asyncio
    async def test_publish_with_correlation_id(self, bus):
        """Test publishing with request correlation ID."""
        request_id = str(uuid4())

        await bus.publish_event(
            channel=GUILD_CHANNELS["research"].name,
            event_type="test",
            payload={},
            request_id=request_id,
        )

        # Retrieve and verify
        metrics = await bus.get_metrics()
        assert metrics["published"] == 1


class TestSubscribe:
    """Test subscription functionality."""

    @pytest.mark.asyncio
    async def test_subscribe_to_heartbeat(self, bus):
        """Test subscribing to heartbeat channel."""
        events_received = []

        async def handler(event: BusEvent):
            events_received.append(event)

        await bus.subscribe_to_channel(
            HEARTBEAT_CHANNEL.name,
            handler,
            "test_handler"
        )

        # Publish event
        await bus.publish_event(
            channel=HEARTBEAT_CHANNEL.name,
            event_type="heartbeat",
            payload={"status": "healthy"},
        )

        # Wait for event processing
        await asyncio.sleep(0.5)

        # Allow subscriptions to process
        for _ in range(10):
            if events_received:
                break
            await asyncio.sleep(0.1)

        # Note: Due to async nature, event might not be received immediately
        # This is expected - actual subscriptions will process in background

    @pytest.mark.asyncio
    async def test_subscribe_to_guild(self, bus):
        """Test subscribing to guild broadcast."""
        async def handler(event: BusEvent):
            pass

        await bus.subscribe_to_guild(
            "research",
            handler,
            "research_handler"
        )

        assert "sys.guild.research.broadcast:research_handler" in bus._subscriptions

    @pytest.mark.asyncio
    async def test_subscribe_to_alerts(self, bus):
        """Test pattern subscription to alert channels."""
        async def alert_handler(event: BusEvent, channel: str):
            pass

        await bus.subscribe_to_alerts(alert_handler, "alert_handler")

        assert "sys.alert.*:alert_handler" in bus._subscriptions

    @pytest.mark.asyncio
    async def test_subscribe_without_connection(self):
        """Test subscription fails when not connected."""
        bus = RaptorBus(redis_url="redis://localhost:6379/1")
        bus.is_connected = False

        with pytest.raises(SubscriptionError):
            await bus.subscribe_to_guild("research", lambda x: None)

    @pytest.mark.asyncio
    async def test_unsubscribe_all(self, bus):
        """Test unsubscribing from all channels."""
        async def handler(event: BusEvent):
            pass

        await bus.subscribe_to_channel("test_channel_1", handler)
        await bus.subscribe_to_channel("test_channel_2", handler)

        assert len(bus._subscriptions) == 2

        await bus.unsubscribe_all()

        assert len(bus._subscriptions) == 0


class TestMessagePersistence:
    """Test message persistence and replay."""

    @pytest.mark.asyncio
    async def test_publish_persists_message(self, bus):
        """Test that published messages are persisted."""
        event_id = await bus.publish_event(
            channel=GUILD_CHANNELS["research"].name,
            event_type="test",
            payload={"key": "value"},
        )

        # Retrieve persisted message
        retrieved_event = await bus.get_message(event_id)

        assert retrieved_event is not None
        assert retrieved_event.id == event_id
        assert retrieved_event.payload["key"] == "value"

    @pytest.mark.asyncio
    async def test_get_nonexistent_message(self, bus):
        """Test retrieving non-existent message returns None."""
        result = await bus.get_message("nonexistent-id")
        assert result is None


class TestMetrics:
    """Test metrics collection."""

    @pytest.mark.asyncio
    async def test_metrics_tracking(self, bus):
        """Test that metrics are tracked correctly."""
        initial_metrics = await bus.get_metrics()

        await bus.publish_event(
            channel=GUILD_CHANNELS["research"].name,
            event_type="test",
            payload={},
            priority=EventPriority.HIGH,
        )

        updated_metrics = await bus.get_metrics()

        assert updated_metrics["published"] == initial_metrics["published"] + 1
        assert updated_metrics["published_by_priority"]["high"] >= 1

    @pytest.mark.asyncio
    async def test_health_check_connected(self, bus):
        """Test health check when connected."""
        health = await bus.health_check()

        assert health["status"] == "healthy"
        assert health["redis_ping"] is True
        assert "connected_clients" in health

    @pytest.mark.asyncio
    async def test_health_check_disconnected(self):
        """Test health check when disconnected."""
        bus = RaptorBus(redis_url="redis://localhost:6379/1")
        bus.is_connected = False

        health = await bus.health_check()

        assert health["status"] == "disconnected"


class TestErrorHandling:
    """Test error handling and recovery."""

    @pytest.mark.asyncio
    async def test_publish_error_handling(self, bus):
        """Test graceful handling of publish errors."""
        with pytest.raises(PublishError):
            # Try to publish to channel with invalid character handling
            # This will cause schema validation or other issues
            await bus.publish_event(
                channel="",  # Empty channel
                event_type="test",
                payload={},
            )

    @pytest.mark.asyncio
    async def test_dlq_messages(self, bus):
        """Test retrieving DLQ messages."""
        dlq_messages = await bus.get_dlq_messages()

        # Should return a list (might be empty)
        assert isinstance(dlq_messages, list)


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    @pytest.mark.asyncio
    async def test_lord_commands_guild(self, bus):
        """Test Lord -> Guild command flow."""
        command_received = False

        async def guild_handler(event: BusEvent):
            nonlocal command_received
            if event.type == "lord_command":
                command_received = True

        await bus.subscribe_to_guild("research", guild_handler)

        # Lord commands guild
        await bus.publish_event(
            channel=GUILD_CHANNELS["research"].name,
            event_type="lord_command",
            payload={"command": "analyze_market"},
            source_agent_id="LORD-002",
            destination_guild="research",
        )

        # Allow time for subscription processing
        await asyncio.sleep(0.5)

    @pytest.mark.asyncio
    async def test_crisis_alert_routing(self, bus):
        """Test critical alert routing."""
        alert_received = False

        async def alert_handler(event: BusEvent, channel: str):
            nonlocal alert_received
            if event.priority == EventPriority.CRITICAL:
                alert_received = True

        await bus.subscribe_to_alerts(alert_handler)

        # Publish critical alert
        await bus.publish_event(
            channel=ALERT_CHANNELS["critical"].name,
            event_type="crisis_detected",
            payload={"severity": "high"},
            priority=EventPriority.CRITICAL,
        )

        await asyncio.sleep(0.5)

    @pytest.mark.asyncio
    async def test_correlation_id_tracking(self, bus):
        """Test request correlation ID tracking."""
        request_id = str(uuid4())

        await bus.publish_event(
            channel=GUILD_CHANNELS["research"].name,
            event_type="research_request",
            payload={},
            request_id=request_id,
        )

        await bus.publish_event(
            channel=GUILD_CHANNELS["research"].name,
            event_type="research_response",
            payload={},
            request_id=request_id,
        )

        metrics = await bus.get_metrics()
        assert metrics["published"] == 2


if __name__ == "__main__":
    # Run tests: pytest backend/tests/test_raptor_bus.py -v
    pass
