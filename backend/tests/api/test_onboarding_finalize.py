"""
Tests for Onboarding Finalize Endpoint

Comprehensive tests for the onboarding finalization system including
BCM generation, caching, persistence, and embedding workflows.
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from main import app


class TestOnboardingFinalize:
    """Test suite for onboarding finalize endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_session_manager(self):
        """Mock session manager."""
        manager = AsyncMock()
        manager.get_metadata.return_value = {
            "session_id": "test_session",
            "workspace_id": "workspace123",
            "user_id": "user456",
        }
        manager.get_all_steps.return_value = {
            "step_1": {"data": {"company_name": "Test Corp"}},
            "step_2": {"data": {"industry": "technology"}},
            "step_3": {"data": {"description": "Test description"}},
            # ... more steps
        }
        manager.save_step.return_value = True
        manager.delete_session.return_value = True
        manager.health_check.return_value = {"overall_healthy": True}
        return manager

    @pytest.fixture
    def mock_bcm_reducer(self):
        """Mock BCM reducer."""
        reducer = AsyncMock()

        # Create mock manifest
        mock_manifest = MagicMock()
        mock_manifest.version.value = "2.0"
        mock_manifest.checksum = "abc123"
        mock_manifest.completion_percentage = 85.0
        mock_manifest.dict.return_value = {
            "version": "2.0",
            "workspace_id": "workspace123",
            "company": {"name": "Test Corp"},
            "completion_percentage": 85.0,
            "checksum": "abc123",
        }
        mock_manifest.json.return_value = (
            '{"version": "2.0", "company": {"name": "Test Corp"}}'
        )

        reducer.reduce.return_value = mock_manifest
        return reducer

    @pytest.fixture
    def mock_services(self):
        """Mock external services."""
        supabase_client = AsyncMock()
        upstash_client = AsyncMock()
        vertex_ai_client = AsyncMock()

        # Mock Supabase responses
        supabase_client.execute.return_value = [{"next_version": 1}]

        # Mock Upstash responses
        upstash_client.set_json.return_value = True
        upstash_client.get_json.return_value = None
        upstash_client.async_client.ping.return_value = True
        upstash_client.async_client.lpush.return_value = 1
        upstash_client.async_client.brpop.return_value = None

        # Mock Vertex AI
        vertex_ai_client.health_check.return_value = True

        return {
            "supabase": supabase_client,
            "upstash": upstash_client,
            "vertex_ai": vertex_ai_client,
        }

    @pytest.fixture
    def sample_session_data(self):
        """Sample session data for testing."""
        return {
            "step_1": {
                "data": {
                    "company_name": "TechCorp Solutions",
                    "industry": "technology",
                    "description": "AI-powered analytics platform",
                    "stage": "series_a",
                }
            },
            "step_2": {"data": {"mission": "Transform data into insights"}},
            "step_3": {"data": {"contradictions": []}},
            "step_4": {"data": {"truth_sheet": {}}},
            "step_5": {"data": {"research": {}}},
            "step_6": {"data": {"pricing": {}}},
            "step_7": {"data": {"competitors": []}},
            "step_8": {"data": {"ladder": {}}},
            "step_9": {"data": {"category": {}}},
            "step_10": {"data": {"capabilities": {}}},
            "step_11": {"data": {"matrix": {}}},
            "step_12": {"data": {"positioning": {}}},
            "step_13": {"data": {"focus": {}}},
            "step_14": {"data": {"icps": []}},
            "step_15": {"data": {"process": {}}},
            "step_16": {"data": {"messaging": {}}},
            "step_17": {"data": {"soundbites": []}},
            "step_18": {"data": {"hierarchy": {}}},
            "step_19": {"data": {"augmentation": {}}},
            "step_20": {"data": {"channels": {}}},
            "step_21": {"data": {"market": {}}},
            "step_22": {"data": {"todos": {}}},
            "step_23": {"data": {"synthesis": {}}},
        }

    def test_finalize_success(
        self, client, mock_session_manager, mock_bcm_reducer, mock_services
    ):
        """Test successful onboarding finalization."""
        # Mock session data to have enough steps (>= 50% completion)
        mock_session_manager.get_all_steps.return_value = {
            f"step_{i}": {"data": {"test": f"data_{i}"}}
            for i in range(1, 13)  # 12 steps = 52% completion
        }

        with patch("api.v1.onboarding_finalize.session_manager", mock_session_manager):
            with patch("api.v1.onboarding_finalize.bcm_reducer", mock_bcm_reducer):
                with patch(
                    "api.v1.onboarding_finalize.supabase_client",
                    mock_services["supabase"],
                ):
                    with patch(
                        "api.v1.onboarding_finalize.upstash_client",
                        mock_services["upstash"],
                    ):
                        with patch(
                            "api.v1.onboarding_finalize.vertex_ai_client",
                            mock_services["vertex_ai"],
                        ):
                            response = client.post(
                                "/api/v1/onboarding/test_session/finalize",
                                json={
                                    "session_id": "test_session",
                                    "generate_bcm": True,
                                    "cache_bcm": True,
                                    "persist_bcm": True,
                                    "enqueue_embeddings": True,
                                },
                            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["session_id"] == "test_session"
        assert data["workspace_id"] == "workspace123"
        assert data["completion_percentage"] == 52.17  # 12/23 * 100
        assert data["bcm_generated"] is True
        assert data["bcm_cached"] is True
        assert data["bcm_persisted"] is True
        assert data["embeddings_enqueued"] is True
        assert data["business_context"] is not None
        assert data["bcm_version"] == "2.0"
        assert data["bcm_checksum"] == "abc123"
        assert "finalized_at" in data
        assert "processing_time_ms" in data

    def test_finalize_insufficient_completion(self, client, mock_session_manager):
        """Test finalization with insufficient completion."""
        # Mock session with insufficient steps (< 50% completion)
        mock_session_manager.get_all_steps.return_value = {
            f"step_{i}": {"data": {"test": f"data_{i}"}}
            for i in range(1, 10)  # 9 steps = 39% completion
        }

        with patch("api.v1.onboarding_finalize.session_manager", mock_session_manager):
            response = client.post(
                "/api/v1/onboarding/test_session/finalize",
                json={"session_id": "test_session", "generate_bcm": True},
            )

        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "Session incomplete" in error_detail
        assert "39.0% completed" in error_detail

    def test_finalize_session_not_found(self, client, mock_session_manager):
        """Test finalization with non-existent session."""
        mock_session_manager.get_metadata.return_value = None

        with patch("api.v1.onboarding_finalize.session_manager", mock_session_manager):
            response = client.post(
                "/api/v1/onboarding/nonexistent/finalize",
                json={"session_id": "nonexistent", "generate_bcm": True},
            )

        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]

    def test_finalize_no_workspace_id(self, client, mock_session_manager):
        """Test finalization with missing workspace ID."""
        mock_session_manager.get_metadata.return_value = {
            "session_id": "test_session"
            # No workspace_id
        }

        with patch("api.v1.onboarding_finalize.session_manager", mock_session_manager):
            response = client.post(
                "/api/v1/onboarding/test_session/finalize",
                json={"session_id": "test_session", "generate_bcm": True},
            )

        assert response.status_code == 400
        assert "Workspace ID not found" in response.json()["detail"]

    def test_finalize_no_step_data(self, client, mock_session_manager):
        """Test finalization with no step data."""
        mock_session_manager.get_metadata.return_value = {
            "session_id": "test_session",
            "workspace_id": "workspace123",
        }
        mock_session_manager.get_all_steps.return_value = {}

        with patch("api.v1.onboarding_finalize.session_manager", mock_session_manager):
            response = client.post(
                "/api/v1/onboarding/test_session/finalize",
                json={"session_id": "test_session", "generate_bcm": True},
            )

        assert response.status_code == 400
        assert "No step data found" in response.json()["detail"]

    def test_finalize_bcm_generation_failure(
        self, client, mock_session_manager, mock_bcm_reducer
    ):
        """Test finalization with BCM generation failure."""
        mock_session_manager.get_all_steps.return_value = {
            f"step_{i}": {"data": {"test": f"data_{i}"}} for i in range(1, 13)
        }

        mock_bcm_reducer.reduce.side_effect = Exception("BCM generation failed")

        with patch("api.v1.onboarding_finalize.session_manager", mock_session_manager):
            with patch("api.v1.onboarding_finalize.bcm_reducer", mock_bcm_reducer):
                response = client.post(
                    "/api/v1/onboarding/test_session/finalize",
                    json={"session_id": "test_session", "generate_bcm": True},
                )

        assert response.status_code == 500
        assert "BCM generation failed" in response.json()["detail"]

    def test_finalize_minimal_options(
        self, client, mock_session_manager, mock_bcm_reducer, mock_services
    ):
        """Test finalization with minimal options."""
        mock_session_manager.get_all_steps.return_value = {
            f"step_{i}": {"data": {"test": f"data_{i}"}} for i in range(1, 13)
        }

        with patch("api.v1.onboarding_finalize.session_manager", mock_session_manager):
            with patch("api.v1.onboarding_finalize.bcm_reducer", mock_bcm_reducer):
                with patch(
                    "api.v1.onboarding_finalize.supabase_client",
                    mock_services["supabase"],
                ):
                    with patch(
                        "api.v1.onboarding_finalize.upstash_client",
                        mock_services["upstash"],
                    ):
                        response = client.post(
                            "/api/v1/onboarding/test_session/finalize",
                            json={
                                "session_id": "test_session",
                            },
                        )

        assert response.status_code == 200
        data = response.json()

        # Should use default values
        assert data["bcm_generated"] is True  # Default True
        assert data["bcm_cached"] is True  # Default True
        assert data["bcm_persisted"] is True  # Default True
        assert data["embeddings_enqueued"] is True  # Default True

    def test_finalize_no_bcm_generation(self, client, mock_session_manager):
        """Test finalization without BCM generation."""
        mock_session_manager.get_all_steps.return_value = {
            f"step_{i}": {"data": {"test": f"data_{i}"}} for i in range(1, 13)
        }

        with patch("api.v1.onboarding_finalize.session_manager", mock_session_manager):
            response = client.post(
                "/api/v1/onboarding/test_session/finalize",
                json={"session_id": "test_session", "generate_bcm": False},
            )

        assert response.status_code == 200
        data = response.json()

        assert data["bcm_generated"] is False
        assert data["business_context"] is None
        assert data["bcm_version"] is None
        assert data["bcm_checksum"] is None

    def test_rebuild_bcm_success(self, client, mock_services):
        """Test BCM rebuild endpoint."""
        # Mock cached BCM
        mock_services["upstash"].get_json.return_value = {
            "version": "2.0",
            "workspace_id": "workspace123",
            "completion_percentage": 85.0,
            "checksum": "abc123",
        }

        with patch(
            "api.v1.onboarding_finalize.upstash_client", mock_services["upstash"]
        ):
            response = client.post(
                "/api/v1/onboarding/context/rebuild",
                json={"workspace_id": "workspace123", "force_rebuild": False},
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["workspace_id"] == "workspace123"
        assert data["version"] == "2.0"
        assert data["checksum"] == "abc123"
        assert data["cached"] is True

    def test_rebuild_bcm_force(self, client, mock_services):
        """Test BCM rebuild with force flag."""
        mock_services["upstash"].get_json.return_value = None  # No cached BCM

        with patch(
            "api.v1.onboarding_finalize.upstash_client", mock_services["upstash"]
        ):
            response = client.post(
                "/api/v1/onboarding/context/rebuild",
                json={"workspace_id": "workspace123", "force_rebuild": True},
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["cached"] is False
        assert "implementation pending" in data.get("message", "")

    def test_get_bcm_manifest_cached(self, client, mock_services):
        """Test getting BCM manifest from cache."""
        mock_services["upstash"].get_json.return_value = {
            "version": "2.0",
            "workspace_id": "workspace123",
            "completion_percentage": 85.0,
            "checksum": "abc123",
            "company": {"name": "Test Corp"},
        }

        with patch(
            "api.v1.onboarding_finalize.upstash_client", mock_services["upstash"]
        ):
            response = client.get(
                "/api/v1/onboarding/context/manifest",
                params={"workspace_id": "workspace123", "include_raw": "true"},
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["workspace_id"] == "workspace123"
        assert data["version"] == "2.0"
        assert data["checksum"] == "abc123"
        assert data["cached"] is True
        assert data["manifest"] is not None
        assert data["manifest"]["company"]["name"] == "Test Corp"

    def test_get_bcm_manifest_not_found(self, client, mock_services):
        """Test getting BCM manifest when not found."""
        mock_services["upstash"].get_json.return_value = None

        with patch(
            "api.v1.onboarding_finalize.supabase_client", mock_services["supabase"]
        ):
            mock_services["supabase"].execute.return_value = []  # No results

            with patch(
                "api.v1.onboarding_finalize.upstash_client", mock_services["upstash"]
            ):
                response = client.get(
                    "/api/v1/onboarding/context/manifest",
                    params={"workspace_id": "nonexistent"},
                )

        assert response.status_code == 404
        assert "BCM not found" in response.json()["detail"]

    def test_get_finalization_status(self, client, mock_session_manager, mock_services):
        """Test getting finalization status."""
        mock_session_manager.get_metadata.return_value = {
            "session_id": "test_session",
            "workspace_id": "workspace123",
        }
        mock_session_manager.get_step.return_value = {
            "finalized": True,
            "finalized_at": "2026-01-27T06:30:00Z",
        }
        mock_session_manager.get_all_steps.return_value = {
            f"step_{i}": {"data": {"test": f"data_{i}"}} for i in range(1, 13)
        }

        # Mock BCM status
        mock_services["upstash"].get_json.return_value = {
            "version": "2.0",
            "checksum": "abc123",
            "completion_percentage": 85.0,
        }

        with patch("api.v1.onboarding_finalize.session_manager", mock_session_manager):
            with patch(
                "api.v1.onboarding_finalize.upstash_client", mock_services["upstash"]
            ):
                response = client.get("/api/v1/onboarding/test_session/status")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["session_id"] == "test_session"
        assert data["workspace_id"] == "workspace123"
        assert data["finalized"] is True
        assert data["completion_percentage"] == 52.17  # 12/23 * 100
        assert data["completed_steps"] == 12
        assert data["total_steps"] == 23
        assert data["bcm_status"]["exists"] is True
        assert data["bcm_status"]["version"] == "2.0"

    def test_get_finalization_status_not_finalized(self, client, mock_session_manager):
        """Test getting status for non-finalized session."""
        mock_session_manager.get_metadata.return_value = {
            "session_id": "test_session",
            "workspace_id": "workspace123",
        }
        mock_session_manager.get_step.return_value = None  # No step 0 data

        with patch("api.v1.onboarding_finalize.session_manager", mock_session_manager):
            response = client.get("/api/v1/onboarding/test_session/status")

        assert response.status_code == 200
        data = response.json()

        assert data["finalized"] is False
        assert data["bcm_status"] is None

    def test_cleanup_session_success(self, client, mock_session_manager):
        """Test successful session cleanup."""
        mock_session_manager.get_step.return_value = {"finalized": True}
        mock_session_manager.delete_session.return_value = True

        with patch("api.v1.onboarding_finalize.session_manager", mock_session_manager):
            response = client.delete("/api/v1/onboarding/test_session/cleanup")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["session_id"] == "test_session"
        assert "cleaned_at" in data

    def test_cleanup_session_not_finalized(self, client, mock_session_manager):
        """Test cleanup for non-finalized session."""
        mock_session_manager.get_step.return_value = None

        with patch("api.v1.onboarding_finalize.session_manager", mock_session_manager):
            response = client.delete("/api/v1/onboarding/test_session/cleanup")

        assert response.status_code == 400
        assert "Session must be finalized" in response.json()["detail"]

    def test_health_check_success(self, client, mock_services):
        """Test successful health check."""
        # Mock all services as healthy
        mock_services["upstash"].async_client.ping.return_value = True
        mock_services["vertex_ai"].health_check.return_value = True

        with patch("api.v1.onboarding_finalize.session_manager", mock_session_manager):
            with patch(
                "api.v1.onboarding_finalize.supabase_client", mock_services["supabase"]
            ):
                with patch(
                    "api.v1.onboarding_finalize.upstash_client",
                    mock_services["upstash"],
                ):
                    with patch(
                        "api.v1.onboarding_finalize.vertex_ai_client",
                        mock_services["vertex_ai"],
                    ):
                        response = client.get("/api/v1/onboarding/finalize/health")

        assert response.status_code == 200
        data = response.json()

        assert data["overall_healthy"] is True
        assert data["redis_connection"] is True
        assert data["supabase_connection"] is True
        assert data["upstash_connection"] is True
        assert "checked_at" in data

    def test_health_check_failure(self, client, mock_services):
        """Test health check with failures."""
        # Mock some services as unhealthy
        mock_services["upstash"].async_client.ping.side_effect = Exception("Redis down")
        mock_services["vertex_ai"].health_check.side_effect = Exception(
            "Vertex AI down"
        )

        with patch("api.v1.onboarding_finalize.session_manager", mock_session_manager):
            with patch(
                "api.v1.onboarding_finalize.supabase_client", mock_services["supabase"]
            ):
                with patch(
                    "api.v1.onboarding_finalize.upstash_client",
                    mock_services["upstash"],
                ):
                    with patch(
                        "api.v1.onboarding_finalize.vertex_ai_client",
                        mock_services["vertex_ai"],
                    ):
                        response = client.get("/api/v1/onboarding/finalize/health")

        assert response.status_code == 200
        data = response.json()

        assert data["overall_healthy"] is False
        assert data["redis_connection"] is True  # Session manager health
        assert data["supabase_connection"] is True
        assert data["upstash_connection"] is False
        assert data["vertex_ai_connection"] is False

    @pytest.mark.asyncio
    async def test_get_session_workspace_id_success(self, mock_session_manager):
        """Test getting workspace ID from session."""
        from api.v1.onboarding_finalize import get_session_workspace_id

        mock_session_manager.get_metadata.return_value = {
            "workspace_id": "workspace123"
        }

        workspace_id = await get_session_workspace_id("test_session")
        assert workspace_id == "workspace123"

    @pytest.mark.asyncio
    async def test_get_session_workspace_id_not_found(self, mock_session_manager):
        """Test getting workspace ID for non-existent session."""
        from api.v1.onboarding_finalize import get_session_workspace_id

        mock_session_manager.get_metadata.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_session_workspace_id("nonexistent")

        assert exc_info.value.status_code == 404
        assert "Session not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_session_completion_success(self, mock_session_manager):
        """Test session completion validation with sufficient steps."""
        from api.v1.onboarding_finalize import validate_session_completion

        mock_session_manager.get_all_steps.return_value = {
            f"step_{i}": {"data": {"test": f"data_{i}"}}
            for i in range(1, 13)  # 12 steps = 52% completion
        }

        percentage = await validate_session_completion("test_session")
        assert percentage == 52.17

    @pytest.mark.asyncio
    async def test_validate_session_completion_insufficient(self, mock_session_manager):
        """Test session completion validation with insufficient steps."""
        from api.v1.onboarding_finalize import validate_session_completion

        mock_session_manager.get_all_steps.return_value = {
            f"step_{i}": {"data": {"test": f"data_{i}"}}
            for i in range(1, 10)  # 9 steps = 39% completion
        }

        with pytest.raises(HTTPException) as exc_info:
            await validate_session_completion("test_session")

        assert exc_info.value.status_code == 400
        assert "Session incomplete" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_session_completion_no_data(self, mock_session_manager):
        """Test session completion validation with no data."""
        from api.v1.onboarding_finalize import validate_session_completion

        mock_session_manager.get_all_steps.return_value = {}

        with pytest.raises(HTTPException) as exc_info:
            await validate_session_completion("test_session")

        assert exc_info.value.status_code == 400
        assert "No step data found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_cache_bcm_in_redis_success(self, mock_services):
        """Test successful BCM caching in Redis."""
        from api.v1.onboarding_finalize import cache_bcm_in_redis

        mock_manifest = MagicMock()
        mock_manifest.dict.return_value = {"test": "data"}

        mock_services["upstash"].set_json.return_value = True

        result = await cache_bcm_in_redis("workspace123", mock_manifest)
        assert result is True

    @pytest.mark.asyncio
    async def test_persist_bcm_to_supabase_success(self, mock_services):
        """Test successful BCM persistence to Supabase."""
        from api.v1.onboarding_finalize import persist_bcm_to_supabase

        mock_manifest = MagicMock()
        mock_manifest.dict.return_value = {"test": "data"}

        mock_services["supabase"].execute.return_value = [{"next_version": 1}]
        mock_services["supabase"].execute.return_value = [{"id": "123", "version": 1}]

        result = await persist_bcm_to_supabase("workspace123", mock_manifest)
        assert result is True

    @pytest.mark.asyncio
    async def test_enqueue_embedding_generation_success(self, mock_services):
        """Test successful embedding generation enqueue."""
        from api.v1.onboarding_finalize import enqueue_embedding_generation

        mock_manifest = MagicMock()
        mock_manifest.version.value = "2.0"
        mock_manifest.checksum = "abc123"

        mock_services["upstash"].async_client.lpush.return_value = 1

        result = await enqueue_embedding_generation("workspace123", mock_manifest)
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__])
