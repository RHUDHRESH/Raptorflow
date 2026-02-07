"""
Tests for Onboarding Session Manager

Comprehensive tests for Redis-based onboarding session management.
"""

import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.redis.session_manager import (
    OnboardingSessionManager,
    get_onboarding_session_manager,
)


class TestOnboardingSessionManager:
    """Test suite for OnboardingSessionManager."""

    @pytest.fixture
    def session_manager(self):
        """Create session manager instance."""
        return OnboardingSessionManager()

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        mock_client.set.return_value = True
        mock_client.get.return_value = None
        mock_client.delete.return_value = 1
        mock_client.exists.return_value = 1
        mock_client.expire.return_value = True
        mock_client.ttl.return_value = 3600
        return mock_client

    @pytest.fixture
    def sample_step_data(self):
        """Sample step data for testing."""
        return {
            "company_name": "Test Corp",
            "industry": "Technology",
            "stage": "Seed",
            "employees": 10,
            "revenue": 100000,
        }

    @pytest.mark.asyncio
    async def test_save_step_success(
        self, session_manager, mock_redis, sample_step_data
    ):
        """Test successful step saving."""
        with patch.object(session_manager.redis, "async_client", mock_redis):
            with patch.object(session_manager.redis, "set_json", return_value=True):
                result = await session_manager.save_step(
                    "test_session", 1, sample_step_data
                )

                assert result is True
                session_manager.redis.set_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_step_invalid_step_id(self, session_manager, sample_step_data):
        """Test saving step with invalid step ID."""
        result = await session_manager.save_step("test_session", 0, sample_step_data)
        assert result is False

        result = await session_manager.save_step("test_session", 24, sample_step_data)
        assert result is False

    @pytest.mark.asyncio
    async def test_save_step_invalid_data(self, session_manager):
        """Test saving step with invalid data."""
        result = await session_manager.save_step("test_session", 1, "invalid_data")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_step_success(self, session_manager, sample_step_data):
        """Test successful step retrieval."""
        step_data = {
            "step_id": 1,
            "data": sample_step_data,
            "saved_at": datetime.utcnow().isoformat(),
            "version": 1,
        }

        with patch.object(session_manager.redis, "get_json", return_value=step_data):
            result = await session_manager.get_step("test_session", 1)

            assert result is not None
            assert result["step_id"] == 1
            assert result["data"] == sample_step_data

    @pytest.mark.asyncio
    async def test_get_step_not_found(self, session_manager):
        """Test retrieving non-existent step."""
        with patch.object(session_manager.redis, "get_json", return_value=None):
            result = await session_manager.get_step("test_session", 1)
            assert result is None

    @pytest.mark.asyncio
    async def test_update_progress_new_session(self, session_manager):
        """Test updating progress for new session."""
        with patch.object(session_manager.redis, "get_json", return_value=None):
            with patch.object(session_manager.redis, "set_json", return_value=True):
                result = await session_manager.update_progress("test_session", 5)

                assert result["completed"] == 5
                assert result["total"] == 23
                assert "percentage" in result
                assert result["percentage"] == round((5 / 23) * 100, 2)

    @pytest.mark.asyncio
    async def test_update_progress_existing_session(self, session_manager):
        """Test updating progress for existing session."""
        existing_progress = {
            "completed": 3,
            "total": 23,
            "started_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
        }

        with patch.object(
            session_manager.redis, "get_json", return_value=existing_progress
        ):
            with patch.object(session_manager.redis, "set_json", return_value=True):
                result = await session_manager.update_progress("test_session", 7)

                assert result["completed"] == 7
                assert result["percentage"] == round((7 / 23) * 100, 2)

    @pytest.mark.asyncio
    async def test_update_progress_lower_step(self, session_manager):
        """Test updating progress with lower step number."""
        existing_progress = {
            "completed": 10,
            "total": 23,
            "started_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
        }

        with patch.object(
            session_manager.redis, "get_json", return_value=existing_progress
        ):
            with patch.object(session_manager.redis, "set_json", return_value=True):
                result = await session_manager.update_progress("test_session", 5)

                # Should not decrease progress
                assert result["completed"] == 10

    @pytest.mark.asyncio
    async def test_get_all_steps(self, session_manager, sample_step_data):
        """Test retrieving all steps for a session."""
        step_data = {
            "step_id": 1,
            "data": sample_step_data,
            "saved_at": datetime.utcnow().isoformat(),
            "version": 1,
        }

        with patch.object(session_manager.redis, "get_json", return_value=step_data):
            result = await session_manager.get_all_steps("test_session")

            assert isinstance(result, dict)
            # Should call get_step for all 23 steps
            assert session_manager.redis.get_json.call_count == 23

    @pytest.mark.asyncio
    async def test_delete_session(self, session_manager):
        """Test deleting a session."""
        with patch.object(session_manager.redis, "delete", return_value=1):
            result = await session_manager.delete_session("test_session")

            assert result is True
            # Should call delete for all steps + progress + metadata
            assert (
                session_manager.redis.delete.call_count == 25
            )  # 23 steps + progress + metadata

    @pytest.mark.asyncio
    async def test_set_metadata(self, session_manager):
        """Test setting session metadata."""
        with patch.object(session_manager.redis, "set_json", return_value=True):
            result = await session_manager.set_metadata(
                "test_session", "user123", "workspace456"
            )

            assert result is True
            session_manager.redis.set_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_metadata(self, session_manager):
        """Test retrieving session metadata."""
        metadata = {
            "session_id": "test_session",
            "user_id": "user123",
            "workspace_id": "workspace456",
            "started_at": datetime.utcnow().isoformat(),
        }

        with patch.object(session_manager.redis, "get_json", return_value=metadata):
            result = await session_manager.get_metadata("test_session")

            assert result is not None
            assert result["user_id"] == "user123"
            assert result["workspace_id"] == "workspace456"

    @pytest.mark.asyncio
    async def test_get_session_summary(self, session_manager, sample_step_data):
        """Test getting complete session summary."""
        progress = {
            "completed": 5,
            "total": 23,
            "percentage": 21.74,
            "last_updated": datetime.utcnow().isoformat(),
        }

        metadata = {
            "session_id": "test_session",
            "user_id": "user123",
            "workspace_id": "workspace456",
            "started_at": datetime.utcnow().isoformat(),
        }

        step_data = {
            "step_id": 1,
            "data": sample_step_data,
            "saved_at": datetime.utcnow().isoformat(),
            "version": 1,
        }

        with patch.object(session_manager, "get_progress", return_value=progress):
            with patch.object(session_manager, "get_metadata", return_value=metadata):
                with patch.object(
                    session_manager, "get_all_steps", return_value={"1": step_data}
                ):
                    result = await session_manager.get_session_summary("test_session")

                    assert result["session_id"] == "test_session"
                    assert result["progress"] == progress
                    assert result["metadata"] == metadata
                    assert result["stats"]["completed_steps"] == 1
                    assert result["stats"]["total_steps"] == 23
                    assert result["stats"]["completion_percentage"] == round(
                        (1 / 23) * 100, 2
                    )

    @pytest.mark.asyncio
    async def test_health_check_success(self, session_manager):
        """Test successful health check."""
        with patch.object(session_manager.redis, "ping", return_value=True):
            with patch.object(session_manager.redis, "set_json", return_value=True):
                with patch.object(
                    session_manager.redis, "get_json", return_value={"test": True}
                ):
                    with patch.object(session_manager.redis, "delete", return_value=1):
                        result = await session_manager.health_check()

                        assert result["overall_healthy"] is True
                        assert result["redis_connection"] is True
                        assert result["set_operation"] is True
                        assert result["get_operation"] is True
                        assert result["delete_operation"] is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, session_manager):
        """Test health check failure."""
        with patch.object(
            session_manager.redis, "ping", side_effect=Exception("Connection failed")
        ):
            result = await session_manager.health_check()

            assert result["overall_healthy"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_retry_mechanism(self, session_manager, sample_step_data):
        """Test retry mechanism for Redis operations."""
        # Mock Redis to fail twice then succeed
        call_count = 0

        async def mock_set_json(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ConnectionError("Connection failed")
            return True

        with patch.object(session_manager.redis, "set_json", side_effect=mock_set_json):
            result = await session_manager.save_step(
                "test_session", 1, sample_step_data
            )

            assert result is True
            assert call_count == 3  # Should retry 2 times and succeed on 3rd

    def test_singleton_pattern(self):
        """Test singleton pattern for session manager."""
        manager1 = get_onboarding_session_manager()
        manager2 = get_onboarding_session_manager()

        assert manager1 is manager2

    @pytest.mark.asyncio
    async def test_ttl_configuration(
        self, session_manager, mock_redis, sample_step_data
    ):
        """Test that TTL is correctly applied to all operations."""
        with patch.object(session_manager.redis, "async_client", mock_redis):
            with patch.object(session_manager.redis, "set_json") as mock_set:
                await session_manager.save_step("test_session", 1, sample_step_data)

                # Verify TTL is passed to set_json
                mock_set.assert_called_once()
                call_args = mock_set.call_args
                assert call_args[1]["ex"] == session_manager.SESSION_TTL

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, session_manager, sample_step_data):
        """Test concurrent operations on the same session."""
        with patch.object(session_manager.redis, "set_json", return_value=True):
            # Create multiple concurrent save operations
            tasks = []
            for i in range(1, 6):
                task = session_manager.save_step("test_session", i, sample_step_data)
                tasks.append(task)

            results = await asyncio.gather(*tasks)

            # All operations should succeed
            assert all(results) is True
            assert len(results) == 5

    @pytest.mark.asyncio
    async def test_session_cleanup(self, session_manager):
        """Test session cleanup functionality."""
        with patch.object(session_manager, "delete_session", return_value=True):
            result = await session_manager.cleanup_expired_sessions()

            # Should return 0 as Redis handles TTL automatically
            assert result == 0


if __name__ == "__main__":
    pytest.main([__file__])
