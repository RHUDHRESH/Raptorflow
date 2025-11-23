"""
Comprehensive tests for onboarding router.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.routers import onboarding


@pytest.fixture
def app():
    """Create FastAPI app with onboarding router."""
    app = FastAPI()
    app.include_router(onboarding.router, prefix="/api/v1/onboarding")
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_auth():
    """Mock authentication dependency."""
    return {
        "user_id": str(uuid4()),
        "workspace_id": uuid4(),
        "email": "test@example.com",
        "role": "authenticated"
    }


class TestOnboardingRouter:
    """Test onboarding endpoints."""

    def test_start_onboarding_success(self, client, mock_auth):
        """Test starting an onboarding session."""
        with patch('backend.routers.onboarding.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.onboarding.supabase_client.insert',
                   new_callable=AsyncMock) as mock_insert:

            mock_insert.return_value = {
                "id": str(uuid4()),
                "status": "in_progress",
                "current_question": 0
            }

            response = client.post(
                "/api/v1/onboarding/start",
                json={"entity_type": "business"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "session_id" in data
            assert data["status"] == "in_progress"

    def test_start_onboarding_invalid_entity_type(self, client, mock_auth):
        """Test starting onboarding with invalid entity type."""
        with patch('backend.routers.onboarding.get_current_user_and_workspace',
                   return_value=mock_auth):

            response = client.post(
                "/api/v1/onboarding/start",
                json={"entity_type": "invalid_type"}
            )

            # Should return validation error
            assert response.status_code in [400, 422]

    def test_submit_answer_success(self, client, mock_auth):
        """Test submitting an answer to onboarding question."""
        session_id = str(uuid4())

        with patch('backend.routers.onboarding.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.onboarding.supabase_client.fetch_one',
                   new_callable=AsyncMock) as mock_fetch, \
             patch('backend.routers.onboarding.supabase_client.update',
                   new_callable=AsyncMock) as mock_update:

            mock_fetch.return_value = {
                "id": session_id,
                "current_question": 0,
                "status": "in_progress",
                "answers": []
            }

            mock_update.return_value = {
                "id": session_id,
                "current_question": 1,
                "status": "in_progress"
            }

            response = client.post(
                f"/api/v1/onboarding/answer/{session_id}",
                json={
                    "question_id": "q1",
                    "answer": "Test answer"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "next_question" in data or "completed" in data

    def test_submit_answer_session_not_found(self, client, mock_auth):
        """Test submitting answer to non-existent session."""
        session_id = str(uuid4())

        with patch('backend.routers.onboarding.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.onboarding.supabase_client.fetch_one',
                   new_callable=AsyncMock, return_value=None):

            response = client.post(
                f"/api/v1/onboarding/answer/{session_id}",
                json={
                    "question_id": "q1",
                    "answer": "Test answer"
                }
            )

            assert response.status_code == 404

    def test_get_profile_success(self, client, mock_auth):
        """Test retrieving onboarding profile."""
        session_id = str(uuid4())

        with patch('backend.routers.onboarding.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.onboarding.supabase_client.fetch_one',
                   new_callable=AsyncMock) as mock_fetch:

            mock_fetch.return_value = {
                "id": session_id,
                "status": "completed",
                "profile_data": {
                    "business_name": "Test Corp",
                    "industry": "Technology"
                }
            }

            response = client.get(f"/api/v1/onboarding/profile/{session_id}")

            assert response.status_code == 200
            data = response.json()
            assert "profile_data" in data

    def test_get_profile_not_found(self, client, mock_auth):
        """Test retrieving non-existent profile."""
        session_id = str(uuid4())

        with patch('backend.routers.onboarding.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.onboarding.supabase_client.fetch_one',
                   new_callable=AsyncMock, return_value=None):

            response = client.get(f"/api/v1/onboarding/profile/{session_id}")

            assert response.status_code == 404

    def test_unauthenticated_request(self, client):
        """Test that unauthenticated requests are rejected."""
        with patch('backend.routers.onboarding.get_current_user_and_workspace',
                   side_effect=Exception("Unauthorized")):

            response = client.post(
                "/api/v1/onboarding/start",
                json={"entity_type": "business"}
            )

            assert response.status_code in [401, 500]
