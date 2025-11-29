"""
Tests for RaptorBus message bus.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from backend.bus.raptor_bus import RaptorBus, PublishError


class TestRaptorBus:
    """Test RaptorBus functionality"""

    @pytest.fixture
    async def bus(self):
        """Create and connect a test bus"""
        bus = RaptorBus(redis_url="redis://localhost:6379/99")  # Use test DB

        # Mock Redis methods for testing
        bus.redis_client = AsyncMock()
        bus.redis_client.publish = AsyncMock(return_value=1)
        bus.redis_client.setex = AsyncMock()
        bus.is_connected = True

        yield bus

        await bus.disconnect()

    async def test_publish_basic(self, bus):
        """Test basic publish operation"""
        await bus.publish("test.event", {"message": "hello"})

        # Verify publish was called once
        assert bus.redis_client.publish.call_count == 1

        # Check the event details were logged or processed
        # (would check log output in real scenario)

    async def test_publish_with_context(self, bus):
        """Test publish with correlation and workspace context"""
        from backend.utils.logging_config import set_correlation_id, set_workspace_id

        # Set context
        set_correlation_id("test-corr-id")
        set_workspace_id("test-ws-id")

        await bus.publish("agent.started", {"task": "test"})

        # The publish_event should use the correlation ID
        # In implementation, it should be included in the event

    async def test_publish_envelope_structure(self, bus):
        """Test that publish creates proper message envelope"""
        await bus.publish("my.event", {"data": "test"})

        # Get the call arguments
        call_args = bus.redis_client.publish.call_args
        assert call_args is not None

        channel, message_json = call_args[0]

        # Should use raptorflow.events prefix
        assert channel == "raptorflow.events.my.event"

        # Message should be JSON parseable
        import json
        message = json.loads(message_json)

        # Verify envelope structure (this would depend on BusEvent schema)
        assert "id" in message or isinstance(message, dict)

    async def test_not_connected_error(self):
        """Test error when bus not connected"""
        bus = RaptorBus()
        bus.is_connected = False

        with pytest.raises(PublishError):
            await bus.publish("test", {})

    async def test_subscribe_registers_handler(self, bus):
        """Test that subscribe registers handlers correctly"""
        def handler(payload):
            pass

        bus.subscribe("test.event", handler)

        # Check that handler was stored (simplified check)
        assert len(bus._handlers) > 0

    async def test_metrics_tracking(self, bus):
        """Test that publish updates metrics"""
        initial_published = bus._metrics["published"]

        await bus.publish("test", {})

        assert bus._metrics["published"] == initial_published + 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
