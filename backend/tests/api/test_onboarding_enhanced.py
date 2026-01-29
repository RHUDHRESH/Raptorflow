"""
Tests for Enhanced Onboarding API

Tests the enhanced onboarding API with Redis session management,
field validation, timeout handling, and retry logic.
"""

import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from main import app


class TestOnboardingEnhancedAPI:
    """Test suite for enhanced onboarding API."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_session_manager(self):
        """Mock session manager."""
        manager = AsyncMock()
        manager.set_metadata.return_value = True
        manager.update_progress.return_value = {"completed": 0, "total": 23}
        manager.get_progress.return_value = {
            "completed": 5,
            "total": 23,
            "percentage": 21.74,
        }
        manager.get_step.return_value = {
            "step_id": 1,
            "data": {"company_name": "Test Corp"},
            "saved_at": datetime.utcnow().isoformat(),
        }
        manager.get_all_steps.return_value = {
            "1": {"step_id": 1, "data": {"company_name": "Test Corp"}},
            "2": {"step_id": 2, "data": {"industry": "Technology"}},
        }
        manager.get_metadata.return_value = {
            "session_id": "test_session",
            "user_id": "user123",
            "workspace_id": "workspace456",
        }
        manager.get_session_summary.return_value = {
            "session_id": "test_session",
            "progress": {"completed": 5, "total": 23},
            "metadata": {"user_id": "user123"},
            "stats": {"completed_steps": 5, "total_steps": 23},
        }
        manager.delete_session.return_value = True
        manager.health_check.return_value = {"overall_healthy": True}
        return manager

    def test_create_session_enhanced_success(self, client, mock_session_manager):
        """Test successful enhanced session creation."""
        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.post(
                "/api/v1/onboarding/session?workspace_id=workspace456&user_id=user123"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["workspace_id"] == "workspace456"
            assert data["user_id"] == "user123"
            assert "session_id" in data
            assert "progress" in data
            assert "metadata" in data
            assert "created_at" in data
            assert data["api_version"] == "enhanced_v2"

    def test_create_session_invalid_workspace(self, client):
        """Test session creation with invalid workspace ID."""
        response = client.post("/api/v1/onboarding/session?workspace_id=")

        assert response.status_code == 422  # Validation error

    def test_update_step_enhanced_success(self, client, mock_session_manager):
        """Test successful enhanced step update."""
        step_data = {
            "company_name": "Test Corp",
            "industry": "Technology",
            "stage": "Seed",
        }

        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.post(
                "/api/v1/onboarding/test_session/steps/1",
                json={"data": step_data, "version": 1, "workspace_id": "workspace456"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["session_id"] == "test_session"
            assert data["step_id"] == 1
            assert data["version"] == 1
            assert "progress" in data
            assert "validation" in data
            assert data["validation"]["data_size"] > 0
            assert data["validation"]["fields_count"] == 3
            assert data["validation"]["workspace_validated"] is True

    def test_update_step_empty_data(self, client):
        """Test step update with empty data."""
        response = client.post(
            "/api/v1/onboarding/test_session/steps/1", json={"data": {}, "version": 1}
        )

        assert response.status_code == 422  # Validation error
        assert "Data must be a non-empty dictionary" in response.text

    def test_update_step_invalid_data_type(self, client):
        """Test step update with invalid data type."""
        response = client.post(
            "/api/v1/onboarding/test_session/steps/1",
            json={"data": "invalid", "version": 1},
        )

        assert response.status_code == 422  # Validation error

    def test_update_step_workspace_mismatch(self, client, mock_session_manager):
        """Test step update with workspace mismatch."""
        mock_session_manager.get_metadata.return_value = {
            "session_id": "test_session",
            "workspace_id": "different_workspace",
        }

        step_data = {"company_name": "Test Corp"}

        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.post(
                "/api/v1/onboarding/test_session/steps/1",
                json={"data": step_data, "version": 1, "workspace_id": "workspace456"},
            )

            assert response.status_code == 403
            assert "Workspace ID mismatch" in response.text

    @pytest.mark.asyncio
    async def test_ai_agent_timeout_wrapper_success(self):
        """Test AI agent wrapper with successful execution."""
        from api.v1.onboarding import execute_ai_agent_with_timeout

        # Mock successful agent
        mock_agent = AsyncMock()
        mock_result = {"status": "success", "data": "test"}
        mock_agent.classify_document.return_value = mock_result

        with patch("api.v1.onboarding.evidence_classifier", mock_agent):
            result = await execute_ai_agent_with_timeout(
                "evidence_classifier", "classify_document", {"test": "data"}
            )

            assert result == mock_result
            mock_agent.classify_document.assert_called_once_with({"test": "data"})

    @pytest.mark.asyncio
    async def test_ai_agent_timeout_wrapper_timeout(self):
        """Test AI agent wrapper with timeout."""
        from api.v1.onboarding import execute_ai_agent_with_timeout
        from fastapi import HTTPException

        # Mock agent that times out
        mock_agent = AsyncMock()
        mock_agent.classify_document.side_effect = asyncio.TimeoutError()

        with patch("api.v1.onboarding.evidence_classifier", mock_agent):
            with pytest.raises(HTTPException) as exc_info:
                await execute_ai_agent_with_timeout(
                    "evidence_classifier", "classify_document", {"test": "data"}
                )

            assert "AI processing timeout" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_ai_agent_timeout_wrapper_retry(self):
        """Test AI agent wrapper with retry logic."""
        from api.v1.onboarding import execute_ai_agent_with_timeout

        # Mock agent that fails twice then succeeds
        mock_agent = AsyncMock()
        mock_result = {"status": "success", "data": "test"}
        mock_agent.classify_document.side_effect = [
            Exception("First failure"),
            Exception("Second failure"),
            mock_result,
        ]

        with patch("api.v1.onboarding.evidence_classifier", mock_agent):
            result = await execute_ai_agent_with_timeout(
                "evidence_classifier", "classify_document", {"test": "data"}
            )

            assert result == mock_result
            assert mock_agent.classify_document.call_count == 3

    def test_classify_evidence_enhanced_success(self, client, mock_session_manager):
        """Test enhanced evidence classification."""
        evidence_data = {"content": "Test content", "type": "document"}

        mock_agent = AsyncMock()
        mock_agent.classify_document.return_value = {"classification": "business"}

        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            with patch(
                "api.v1.onboarding.execute_ai_agent_with_timeout"
            ) as mock_wrapper:
                mock_wrapper.return_value = {"classification": "business"}

                response = client.post(
                    "/api/v1/onboarding/test_session/classify-evidence",
                    json=evidence_data,
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "classification" in data

    def test_classify_evidence_session_not_found(self, client, mock_session_manager):
        """Test evidence classification with session not found."""
        mock_session_manager.get_metadata.return_value = None

        evidence_data = {"content": "Test", "type": "document"}

        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.post(
                "/api/v1/onboarding/test_session/classify-evidence", json=evidence_data
            )

            assert response.status_code == 404
            assert "Session not found" in response.text

    def test_extract_facts_enhanced_success(self, client, mock_session_manager):
        """Test enhanced fact extraction."""
        evidence_list = [
            {"content": "Company revenue is $10M", "source": "doc1"},
            {"content": "Company has 50 employees", "source": "doc2"},
        ]

        mock_agent = AsyncMock()
        mock_result = MagicMock()
        mock_result.facts = [{"fact": "revenue $10M"}, {"fact": "50 employees"}]
        mock_agent.extract_facts_from_evidence.return_value = mock_result

        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            with patch(
                "api.v1.onboarding.execute_ai_agent_with_timeout"
            ) as mock_wrapper:
                mock_wrapper.return_value = mock_result

                response = client.post(
                    "/api/v1/onboarding/test_session/extract-facts", json=evidence_list
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "extraction_result" in data

    def test_detect_contradictions_enhanced_success(self, client, mock_session_manager):
        """Test enhanced contradiction detection."""
        facts = [
            {"fact": "Revenue is $10M", "confidence": 0.9},
            {"fact": "Revenue is $5M", "confidence": 0.8},
        ]

        mock_agent = AsyncMock()
        mock_result = MagicMock()
        mock_result.contradictions = [{"type": "revenue_mismatch"}]
        mock_agent.detect_contradictions.return_value = mock_result

        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            with patch(
                "api.v1.onboarding.execute_ai_agent_with_timeout"
            ) as mock_wrapper:
                mock_wrapper.return_value = mock_result

                response = client.post(
                    "/api/v1/onboarding/test_session/detect-contradictions", json=facts
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "contradiction_result" in data

    def test_session_health_check_success(self, client, mock_session_manager):
        """Test session health check."""
        mock_session_manager.get_metadata.return_value = {
            "session_id": "test_session",
            "started_at": datetime.utcnow().isoformat(),
        }
        mock_session_manager.health_check.return_value = {
            "overall_healthy": True,
            "redis_connection": True,
        }
        mock_session_manager.get_session_summary.return_value = {
            "stats": {"completed_steps": 5, "total_steps": 23}
        }

        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.get("/api/v1/onboarding/test_session/health")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["session_id"] == "test_session"
            assert "session_health" in data
            assert "redis_health" in data
            assert data["session_health"]["exists"] is True
            assert data["redis_health"]["overall_healthy"] is True

    def test_session_health_check_not_found(self, client, mock_session_manager):
        """Test health check for non-existent session."""
        mock_session_manager.get_metadata.return_value = None

        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.get("/api/v1/onboarding/test_session/health")

            assert response.status_code == 404
            assert "Session not found" in response.text

    def test_finalize_session_enhanced_success(self, client, mock_session_manager):
        """Test enhanced session finalization."""
        mock_session_manager.get_all_steps.return_value = {
            "1": {"data": {"company": "Test Corp"}},
            "2": {"data": {"industry": "Tech"}},
        }
        mock_session_manager.get_metadata.return_value = {
            "session_id": "test_session",
            "user_id": "user123",
        }
        mock_session_manager.get_progress.return_value = {
            "completed": 2,
            "total": 23,
            "percentage": 8.7,
        }

        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.post("/api/v1/onboarding/test_session/finalize")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["session_id"] == "test_session"
            assert "business_context" in data
            assert data["completed_steps"] == 2
            assert data["total_steps"] == 23
            assert data["api_version"] == "enhanced_v2"
            assert "finalized_at" in data

    def test_finalize_session_no_steps(self, client, mock_session_manager):
        """Test finalizing session with no step data."""
        mock_session_manager.get_all_steps.return_value = {}

        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.post("/api/v1/onboarding/test_session/finalize")

            assert response.status_code == 404
            assert "No step data found" in response.text

    @pytest.mark.asyncio
    async def test_field_validation_step_request(self):
        """Test StepUpdateRequest field validation."""
        from api.v1.onboarding import StepUpdateRequest
        from pydantic import ValidationError

        # Valid request
        valid_data = {
            "data": {"company": "Test Corp"},
            "version": 1,
            "workspace_id": "workspace123",
        }
        request = StepUpdateRequest(**valid_data)
        assert request.data == {"company": "Test Corp"}
        assert request.version == 1

        # Invalid data (empty)
        with pytest.raises(ValidationError) as exc_info:
            StepUpdateRequest(data={}, version=1)
        assert "Data must be a non-empty dictionary" in str(exc_info.value)

        # Invalid data (wrong type)
        with pytest.raises(ValidationError) as exc_info:
            StepUpdateRequest(data="invalid", version=1)
        assert "Data must be a non-empty dictionary" in str(exc_info.value)

    def test_enhanced_error_responses(self, client, mock_session_manager):
        """Test enhanced error responses with proper details."""
        # Test 404 for session not found
        mock_session_manager.get_metadata.return_value = None

        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.get("/api/v1/onboarding/nonexistent/progress")

            assert response.status_code == 404
            error_detail = response.json()["detail"]
            assert "Session not found" in error_detail

        # Test 400 for invalid step ID
        response = client.post(
            "/api/v1/onboarding/test_session/steps/0",
            json={"data": {"test": "data"}, "version": 1},
        )

        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "Invalid step ID" in error_detail
        assert "between 1 and 23" in error_detail


if __name__ == "__main__":
    pytest.main([__file__])
