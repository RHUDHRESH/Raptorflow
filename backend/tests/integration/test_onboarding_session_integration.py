"""
Integration tests for Onboarding Session Manager with API

Tests the complete flow from API endpoints to Redis storage.
"""

import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from main import app


class TestOnboardingSessionIntegration:
    """Integration tests for onboarding session management."""

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
        return manager

    def test_create_session_success(self, client, mock_session_manager):
        """Test successful session creation."""
        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.post(
                "/api/v1/onboarding/session?workspace_id=workspace456&user_id=user123"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["workspace_id"] == "workspace456"
            assert data["user_id"] == "user123"
            assert "session_id" in data
            assert "progress" in data
            assert "metadata" in data
            assert "created_at" in data

    def test_create_session_missing_workspace(self, client):
        """Test session creation without workspace ID."""
        response = client.post("/api/v1/onboarding/session")

        assert response.status_code == 422  # Validation error

    def test_update_step_success(self, client, mock_session_manager):
        """Test successful step update."""
        step_data = {
            "company_name": "Test Corp",
            "industry": "Technology",
            "stage": "Seed",
        }

        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.post(
                "/api/v1/onboarding/test_session/steps/1",
                json={"data": step_data, "version": 1},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["session_id"] == "test_session"
            assert data["step_id"] == 1
            assert "progress" in data
            assert "updated_at" in data

    def test_update_step_invalid_id(self, client):
        """Test step update with invalid step ID."""
        step_data = {"company_name": "Test Corp"}

        response = client.post(
            "/api/v1/onboarding/test_session/steps/0",
            json={"data": step_data, "version": 1},
        )

        assert response.status_code == 400
        assert "Invalid step ID" in response.json()["detail"]

    def test_update_step_invalid_id_high(self, client):
        """Test step update with step ID too high."""
        step_data = {"company_name": "Test Corp"}

        response = client.post(
            "/api/v1/onboarding/test_session/steps/24",
            json={"data": step_data, "version": 1},
        )

        assert response.status_code == 400
        assert "Invalid step ID" in response.json()["detail"]

    def test_get_progress_success(self, client, mock_session_manager):
        """Test getting session progress."""
        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.get("/api/v1/onboarding/test_session/progress")

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test_session"
            assert "progress" in data
            assert data["progress"]["completed"] == 5

    def test_get_step_success(self, client, mock_session_manager):
        """Test getting specific step data."""
        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.get("/api/v1/onboarding/test_session/steps/1")

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test_session"
            assert data["step_id"] == 1
            assert "data" in data
            assert data["data"]["step_id"] == 1

    def test_get_step_invalid_id(self, client):
        """Test getting step with invalid ID."""
        response = client.get("/api/v1/onboarding/test_session/steps/0")

        assert response.status_code == 400
        assert "Invalid step ID" in response.json()["detail"]

    def test_get_session_summary_success(self, client, mock_session_manager):
        """Test getting session summary."""
        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.get("/api/v1/onboarding/test_session/summary")

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test_session"
            assert "progress" in data
            assert "metadata" in data
            assert "stats" in data

    def test_finalize_session_success(self, client, mock_session_manager):
        """Test session finalization."""
        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.post("/api/v1/onboarding/test_session/finalize")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["session_id"] == "test_session"
            assert "business_context" in data
            assert data["completed_steps"] == 2
            assert data["total_steps"] == 23
            assert "finalized_at" in data

    def test_finalize_session_no_data(self, client, mock_session_manager):
        """Test finalizing session with no step data."""
        mock_session_manager.get_all_steps.return_value = {}

        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.post("/api/v1/onboarding/test_session/finalize")

            assert response.status_code == 404
            assert "No step data found" in response.json()["detail"]

    def test_delete_session_success(self, client, mock_session_manager):
        """Test session deletion."""
        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.delete("/api/v1/onboarding/test_session")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["session_id"] == "test_session"
            assert "deleted_at" in data

    def test_delete_session_not_found(self, client, mock_session_manager):
        """Test deleting non-existent session."""
        mock_session_manager.delete_session.return_value = False

        with patch("api.v1.onboarding.session_manager", mock_session_manager):
            response = client.delete("/api/v1/onboarding/test_session")

            assert response.status_code == 404
            assert "Session not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_complete_flow(self, mock_session_manager):
        """Test complete onboarding flow."""
        # This would test the full flow from session creation to finalization
        # In a real scenario, you'd use actual Redis operations

        # 1. Create session
        await mock_session_manager.set_metadata("session123", "user123", "workspace456")
        await mock_session_manager.update_progress("session123", 0)

        # 2. Save multiple steps
        for step_id in range(1, 4):
            step_data = {
                "step_id": step_id,
                "data": {"field": f"value_{step_id}"},
                "saved_at": datetime.utcnow().isoformat(),
            }
            await mock_session_manager.save_step("session123", step_id, step_data)

        # 3. Get progress
        progress = await mock_session_manager.get_progress("session123")
        assert progress["completed"] >= 3

        # 4. Get all steps
        all_steps = await mock_session_manager.get_all_steps("session123")
        assert len(all_steps) >= 3

        # 5. Finalize session
        summary = await mock_session_manager.get_session_summary("session123")
        assert summary["session_id"] == "session123"

        # 6. Clean up
        deleted = await mock_session_manager.delete_session("session123")
        assert deleted is True


if __name__ == "__main__":
    pytest.main([__file__])
