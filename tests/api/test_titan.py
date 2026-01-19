"""
Tests for Titan API endpoints
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import os

# Set mock environment variables for Pydantic Settings
os.environ["RAPTORFLOW_SKIP_INIT"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["UPSTASH_REDIS_URL"] = "https://test.upstash.io"
os.environ["UPSTASH_REDIS_TOKEN"] = "test-token"
os.environ["VERTEX_AI_PROJECT_ID"] = "test-project"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["WEBHOOK_SECRET"] = "test-webhook-secret"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "test-key"

from backend.api.v1.titan import router as titan_router
from backend.core.models import User

class TestTitanEndpoints:
    """Test Titan research endpoints"""

    @pytest.fixture
    def app(self, mock_user):
        app = FastAPI()
        app.include_router(titan_router)
        
        # Override auth dependency
        from backend.api.v1.titan import get_current_user
        app.dependency_overrides[get_current_user] = lambda: mock_user
        
        return app

    @pytest.fixture
    def client(self, app):
        return TestClient(app)

    @pytest.fixture
    def mock_user(self):
        return User(
            id="test-user-id",
            email="test@example.com",
            full_name="Test User",
            subscription_tier="pro"
        )

    def test_titan_research_success(self, client, mock_user):
        """Test POST /titan/research - success"""
        mock_result = {
            "query": "test company",
            "mode": "LITE",
            "results": [{"url": "https://test.com", "title": "Test"}],
            "count": 1,
            "timestamp": "2026-01-19T12:00:00Z",
            "metadata": {}
        }
        
        with patch("backend.api.v1.titan.TitanOrchestrator") as mock_class:
            mock_instance = mock_class.return_value
            mock_instance.execute = AsyncMock(return_value=mock_result)
            
            response = client.post(
                "/titan/research",
                json={"query": "test company", "mode": "LITE"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test company"
        assert data["mode"] == "LITE"
        assert len(data["results"]) == 1
        assert data["engine"] == "Titan SOTA Intelligence"

    def test_titan_research_invalid_mode(self, client, mock_user):
        """Test POST /titan/research - invalid mode"""
        with patch("backend.api.v1.titan.get_current_user", return_value=mock_user):
            response = client.post(
                "/titan/research",
                json={"query": "test company", "mode": "INVALID"}
            )

        assert response.status_code == 400
        assert "Invalid mode" in response.json()["detail"]

    def test_titan_research_missing_query(self, client, mock_user):
        """Test POST /titan/research - missing query"""
        with patch("backend.api.v1.titan.get_current_user", return_value=mock_user):
            response = client.post(
                "/titan/research",
                json={"mode": "LITE"}
            )

        # FastAPI Pydantic validation error
        assert response.status_code == 422
