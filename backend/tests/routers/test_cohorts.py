"""
Comprehensive tests for cohorts router.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.routers import cohorts


@pytest.fixture
def app():
    """Create FastAPI app with cohorts router."""
    app = FastAPI()
    app.include_router(cohorts.router, prefix="/api/v1/cohorts")
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


@pytest.fixture
def sample_cohort():
    """Sample cohort data."""
    return {
        "id": str(uuid4()),
        "name": "Tech Startup Founders",
        "executive_summary": "Early-stage tech founders seeking growth",
        "demographics": {
            "company_size": "1-10",
            "industry": "Technology",
            "revenue": "$0-1M"
        },
        "psychographics": {
            "motivation": "Growth",
            "risk_tolerance": "High"
        },
        "pain_points": ["Limited budget", "Time constraints"],
        "goals": ["Scale quickly", "Raise funding"],
        "tags": ["innovator", "early-adopter", "budget-conscious"]
    }


class TestCohortsRouter:
    """Test cohorts endpoints."""

    def test_generate_cohort_success(self, client, mock_auth, sample_cohort):
        """Test successful cohort generation."""
        with patch('backend.routers.cohorts.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.cohorts.icp_builder_agent.execute',
                   new_callable=AsyncMock) as mock_agent, \
             patch('backend.routers.cohorts.supabase_client.insert',
                   new_callable=AsyncMock) as mock_insert:

            mock_agent.return_value = {
                "status": "success",
                "result": sample_cohort
            }

            mock_insert.return_value = sample_cohort

            response = client.post(
                "/api/v1/cohorts/generate",
                json={
                    "business_context": "SaaS company",
                    "target_market": "B2B tech"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["name"] == "Tech Startup Founders"

    def test_generate_cohort_agent_failure(self, client, mock_auth):
        """Test cohort generation when agent fails."""
        with patch('backend.routers.cohorts.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.cohorts.icp_builder_agent.execute',
                   new_callable=AsyncMock) as mock_agent:

            mock_agent.return_value = {
                "status": "error",
                "error": "Agent failed"
            }

            response = client.post(
                "/api/v1/cohorts/generate",
                json={
                    "business_context": "SaaS company",
                    "target_market": "B2B tech"
                }
            )

            assert response.status_code == 500

    def test_list_cohorts_success(self, client, mock_auth, sample_cohort):
        """Test listing all cohorts for workspace."""
        with patch('backend.routers.cohorts.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.cohorts.supabase_client.fetch_all',
                   new_callable=AsyncMock) as mock_fetch:

            mock_fetch.return_value = [sample_cohort]

            response = client.get("/api/v1/cohorts/list")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["id"] == sample_cohort["id"]

    def test_list_cohorts_empty(self, client, mock_auth):
        """Test listing cohorts when none exist."""
        with patch('backend.routers.cohorts.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.cohorts.supabase_client.fetch_all',
                   new_callable=AsyncMock, return_value=[]):

            response = client.get("/api/v1/cohorts/list")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 0

    def test_get_cohort_by_id_success(self, client, mock_auth, sample_cohort):
        """Test retrieving specific cohort by ID."""
        cohort_id = sample_cohort["id"]

        with patch('backend.routers.cohorts.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.cohorts.supabase_client.fetch_one',
                   new_callable=AsyncMock, return_value=sample_cohort):

            response = client.get(f"/api/v1/cohorts/{cohort_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == cohort_id

    def test_get_cohort_not_found(self, client, mock_auth):
        """Test retrieving non-existent cohort."""
        cohort_id = str(uuid4())

        with patch('backend.routers.cohorts.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.cohorts.supabase_client.fetch_one',
                   new_callable=AsyncMock, return_value=None):

            response = client.get(f"/api/v1/cohorts/{cohort_id}")

            assert response.status_code == 404

    def test_get_psychographics_success(self, client, mock_auth, sample_cohort):
        """Test retrieving cohort psychographics."""
        cohort_id = sample_cohort["id"]

        with patch('backend.routers.cohorts.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.cohorts.supabase_client.fetch_one',
                   new_callable=AsyncMock, return_value=sample_cohort):

            response = client.get(f"/api/v1/cohorts/{cohort_id}/psychographics")

            assert response.status_code == 200
            data = response.json()
            assert "psychographics" in data
            assert "tags" in data

    def test_update_cohort_success(self, client, mock_auth, sample_cohort):
        """Test updating cohort data."""
        cohort_id = sample_cohort["id"]

        with patch('backend.routers.cohorts.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.cohorts.supabase_client.update',
                   new_callable=AsyncMock) as mock_update:

            updated_cohort = sample_cohort.copy()
            updated_cohort["name"] = "Updated Name"
            mock_update.return_value = updated_cohort

            response = client.put(
                f"/api/v1/cohorts/{cohort_id}",
                json={"name": "Updated Name"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated Name"

    def test_delete_cohort_success(self, client, mock_auth):
        """Test deleting a cohort."""
        cohort_id = str(uuid4())

        with patch('backend.routers.cohorts.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.cohorts.supabase_client.delete',
                   new_callable=AsyncMock, return_value=True):

            response = client.delete(f"/api/v1/cohorts/{cohort_id}")

            assert response.status_code == 200

    def test_workspace_isolation(self, client):
        """Test that users can only access cohorts in their workspace."""
        workspace1 = uuid4()
        workspace2 = uuid4()

        auth1 = {
            "user_id": str(uuid4()),
            "workspace_id": workspace1,
            "email": "user1@example.com",
            "role": "authenticated"
        }

        with patch('backend.routers.cohorts.get_current_user_and_workspace',
                   return_value=auth1), \
             patch('backend.routers.cohorts.supabase_client.fetch_all',
                   new_callable=AsyncMock) as mock_fetch:

            # Mock should only return cohorts for workspace1
            mock_fetch.return_value = []

            response = client.get("/api/v1/cohorts/list")

            assert response.status_code == 200
            # Verify workspace_id was passed to query
            mock_fetch.assert_called_once()
            call_args = mock_fetch.call_args
            assert str(workspace1) in str(call_args)
