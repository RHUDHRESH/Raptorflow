"""
Tests for Redis SessionService.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from ...redis.client import RedisClient
from ...redis.session import SessionService
from ...redis.session_models import SessionData


@pytest_asyncio.fixture
async def session_service(mock_redis: AsyncMock) -> SessionService:
    """Session service fixture."""
    return SessionService(mock_redis)


class TestSessionService:
    """Test cases for SessionService."""

    @pytest_asyncio.asyncio.async_test
    async def test_create_session(
        self, session_service: SessionService, test_session_data: SessionData
    ):
        """Test session creation."""
        # Setup mock
        session_service.redis.set.return_value = True

        # Test
        result = await session_service.create_session(
            user_id=test_session_data.user_id,
            workspace_id=test_session_data.workspace_id,
            metadata={"source": "web"},
        )

        # Assertions
        assert result is not None
        assert len(result) == 36  # UUID length

        # Verify Redis call
        session_service.redis.set.assert_called_once()
        call_args = session_service.redis.set.call_args
        assert call_args[0][0].startswith("session:")
        assert "test-user-456" in call_args[0][1]
        assert "test-workspace-789" in call_args[0][1]

    @pytest_asyncio.asyncio.async_test
    async def test_get_session_existing(
        self, session_service: SessionService, test_session_data: SessionData
    ):
        """Test getting existing session."""
        # Setup mock
        session_json = test_session_data.to_json()
        session_service.redis.get.return_value = session_json

        # Test
        result = await session_service.get_session(test_session_data.session_id)

        # Assertions
        assert result is not None
        assert result.session_id == test_session_data.session_id
        assert result.user_id == test_session_data.user_id
        assert result.workspace_id == test_session_data.workspace_id

        # Verify Redis call
        session_service.redis.get.assert_called_once_with(
            f"session:{test_session_data.session_id}"
        )

    @pytest_asyncio.asyncio.async_test
    async def test_get_session_nonexistent(self, session_service: SessionService):
        """Test getting non-existent session."""
        # Setup mock
        session_service.redis.get.return_value = None

        # Test
        result = await session_service.get_session("nonexistent-session")

        # Assertions
        assert result is None

        # Verify Redis call
        session_service.redis.get.assert_called_once_with("session:nonexistent-session")

    @pytest_asyncio.asyncio.async_test
    async def test_update_session(
        self, session_service: SessionService, test_session_data: SessionData
    ):
        """Test session update."""
        # Setup mock
        session_service.redis.set.return_value = True
        session_service.redis.get.return_value = test_session_data.to_json()

        # Test
        updates = {
            "current_agent": "new-agent",
            "messages": [{"role": "assistant", "content": "Hello back!"}],
        }
        result = await session_service.update_session(
            test_session_data.session_id, updates
        )

        # Assertions
        assert result is not None
        assert result.current_agent == "new-agent"
        assert len(result.messages) == 2

        # Verify Redis calls
        session_service.redis.get.assert_called_once_with(
            f"session:{test_session_data.session_id}"
        )
        session_service.redis.set.assert_called_once()

    @pytest_asyncio.asyncio.async_test
    async def test_update_session_nonexistent(self, session_service: SessionService):
        """Test updating non-existent session."""
        # Setup mock
        session_service.redis.get.return_value = None

        # Test
        with pytest.raises(ValueError, match="Session not found"):
            await session_service.update_session(
                "nonexistent-session", {"current_agent": "new-agent"}
            )

    @pytest_asyncio.asyncio.async_test
    async def test_delete_session(
        self, session_service: SessionService, test_session_data: SessionData
    ):
        """Test session deletion."""
        # Setup mock
        session_service.redis.delete.return_value = 1

        # Test
        result = await session_service.delete_session(test_session_data.session_id)

        # Assertions
        assert result is True

        # Verify Redis call
        session_service.redis.delete.assert_called_once_with(
            f"session:{test_session_data.session_id}"
        )

    @pytest_asyncio.asyncio.async_test
    async def test_delete_session_nonexistent(self, session_service: SessionService):
        """Test deleting non-existent session."""
        # Setup mock
        session_service.redis.delete.return_value = 0

        # Test
        result = await session_service.delete_session("nonexistent-session")

        # Assertions
        assert result is False

    @pytest_asyncio.asyncio.async_test
    async def test_extend_session(
        self, session_service: SessionService, test_session_data: SessionData
    ):
        """Test session extension."""
        # Setup mock
        session_service.redis.get.return_value = test_session_data.to_json()
        session_service.redis.set.return_value = True
        session_service.redis.expire.return_value = True

        # Test
        result = await session_service.extend_session(
            test_session_data.session_id, 3600
        )

        # Assertions
        assert result is not None
        assert result.expires_at > test_session_data.expires_at

        # Verify Redis calls
        session_service.redis.get.assert_called_once()
        session_service.redis.set.assert_called_once()
        session_service.redis.expire.assert_called_once()

    @pytest_asyncio.asyncio.async_test
    async def test_extend_session_nonexistent(self, session_service: SessionService):
        """Test extending non-existent session."""
        # Setup mock
        session_service.redis.get.return_value = None

        # Test
        with pytest.raises(ValueError, match="Session not found"):
            await session_service.extend_session("nonexistent-session", 3600)

    @pytest_asyncio.asyncio.async_test
    async def test_session_expiry(self, session_service: SessionService):
        """Test session expiry behavior."""
        # Create expired session
        expired_session = SessionData(
            session_id="expired-session",
            user_id="test-user",
            workspace_id="test-workspace",
            current_agent="test-agent",
            messages=[],
            context={},
            created_at=datetime.utcnow() - timedelta(hours=2),
            last_active_at=datetime.utcnow() - timedelta(hours=2),
            expires_at=datetime.utcnow() - timedelta(hours=1),  # Expired
        )

        # Setup mock
        session_service.redis.get.return_value = expired_session.to_json()

        # Test
        result = await session_service.get_session("expired-session")

        # Assertions
        assert result is None  # Should return None for expired session

        # Verify Redis cleanup
        session_service.redis.delete.assert_called_once_with("session:expired-session")

    @pytest_asyncio.asyncio.async_test
    async def test_session_with_large_data(self, session_service: SessionService):
        """Test session with large message history."""
        # Create session with many messages
        large_session = SessionData(
            session_id="large-session",
            user_id="test-user",
            workspace_id="test-workspace",
            current_agent="test-agent",
            messages=[{"role": "user", "content": f"Message {i}"} for i in range(1000)],
            context={"large_data": "x" * 10000},
            created_at=datetime.utcnow(),
            last_active_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )

        # Setup mock
        session_service.redis.get.return_value = large_session.to_json()

        # Test
        result = await session_service.get_session("large-session")

        # Assertions
        assert result is not None
        assert len(result.messages) == 1000
        assert len(result.context["large_data"]) == 10000

    @pytest_asyncio.asyncio.async_test
    async def test_concurrent_session_operations(self, session_service: SessionService):
        """Test concurrent session operations."""
        import asyncio

        # Setup mock
        session_service.redis.set.return_value = True
        session_service.redis.get.return_value = None

        # Create multiple sessions concurrently
        tasks = []
        for i in range(10):
            task = session_service.create_session(
                user_id=f"user-{i}",
                workspace_id="test-workspace",
                metadata={"index": i},
            )
            tasks.append(task)

        # Execute concurrently
        results = await asyncio.gather(*tasks)

        # Assertions
        assert len(results) == 10
        assert all(len(result) == 36 for result in results)  # All UUIDs
        assert len(set(results)) == 10  # All unique

        # Verify Redis was called 10 times
        assert session_service.redis.set.call_count == 10

    @pytest_asyncio.asyncio.async_test
    async def test_session_error_handling(self, session_service: SessionService):
        """Test error handling in session operations."""
        # Setup mock to raise exception
        session_service.redis.get.side_effect = Exception("Redis error")

        # Test
        with pytest.raises(Exception, match="Redis error"):
            await session_service.get_session("test-session")

    @pytest_asyncio.asyncio.async_test
    async def test_session_data_serialization(self, session_service: SessionService):
        """Test session data serialization/deserialization."""
        # Create session with complex data
        complex_session = SessionData(
            session_id="complex-session",
            user_id="test-user",
            workspace_id="test-workspace",
            current_agent="test-agent",
            messages=[
                {
                    "role": "user",
                    "content": "Hello",
                    "metadata": {"timestamp": 1234567890},
                },
                {"role": "assistant", "content": "Hi there!", "confidence": 0.95},
            ],
            context={
                "preferences": {"theme": "dark", "language": "en"},
                "features": ["feature1", "feature2"],
                "nested": {"key": {"subkey": "value"}},
            },
            created_at=datetime.utcnow(),
            last_active_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )

        # Setup mock
        session_service.redis.get.return_value = complex_session.to_json()

        # Test
        result = await session_service.get_session("complex-session")

        # Assertions
        assert result is not None
        assert result.session_id == complex_session.session_id
        assert len(result.messages) == 2
        assert result.messages[0]["metadata"]["timestamp"] == 1234567890
        assert result.messages[1]["confidence"] == 0.95
        assert result.context["preferences"]["theme"] == "dark"
        assert result.context["features"] == ["feature1", "feature2"]
        assert result.context["nested"]["key"]["subkey"] == "value"
