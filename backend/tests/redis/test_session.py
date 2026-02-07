"""
Tests for Redis SessionService (canonical).
"""

import json
from unittest.mock import patch

import pytest
import pytest_asyncio

from ...redis.session import SessionService


@pytest_asyncio.fixture
async def session_service() -> SessionService:
    """Session service fixture."""
    return SessionService()


class TestSessionService:
    @pytest.mark.asyncio
    async def test_create_session(self, session_service: SessionService):
        redis = session_service.redis.async_client
        redis.set.return_value = True
        redis.zadd.return_value = 1
        redis.expire.return_value = True

        with patch(
            "backend.redis.session.secrets.token_urlsafe", return_value="sess-123"
        ):
            session_id = await session_service.create_session(
                user_id="user-1", workspace_id="ws-1", metadata={"source": "web"}
            )

        assert session_id == "sess-123"
        redis.set.assert_called_once()
        key_arg = redis.set.call_args[0][0]
        assert key_arg == "session:sess-123"

    @pytest.mark.asyncio
    async def test_get_session(self, session_service: SessionService):
        redis = session_service.redis.async_client
        redis.get.return_value = json.dumps(
            {
                "session_id": "sess-123",
                "user_id": "user-1",
                "workspace_id": "ws-1",
                "created_at": "2024-01-01T00:00:00Z",
                "last_accessed": "2024-01-01T00:00:00Z",
                "metadata": {},
            }
        )
        redis.set.return_value = True

        session = await session_service.get_session("sess-123")

        assert session is not None
        assert session["session_id"] == "sess-123"
        assert session["user_id"] == "user-1"
        redis.get.assert_called_once_with("session:sess-123")
