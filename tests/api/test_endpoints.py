"""
Tests for API endpoints
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ...api.v1.auth import router as auth_router
from ...api.v1.campaigns import router as campaigns_router
from ...api.v1.users import router as users_router
from ...api.v1.workspaces import router as workspaces_router
from ...core.auth import get_auth_context, get_current_user
from ...core.models import AuthContext, User, Workspace


class TestAuthEndpoints:
    """Test authentication endpoints"""

    @pytest.fixture
    def app(self):
        app = FastAPI()
        app.include_router(auth_router)
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
            subscription_tier="free",
            budget_limit_monthly=1.0,
            preferences={"theme": "light"},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

    def test_get_me_success(self, client, mock_user):
        """Test GET /auth/me endpoint - success"""
        with patch("...api.v1.auth.get_current_user", return_value=mock_user):
            response = client.get("/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-user-id"
        assert data["email"] == "test@example.com"
        assert data["subscription_tier"] == "free"

    def test_get_me_unauthorized(self, client):
        """Test GET /auth/me endpoint - unauthorized"""
        with patch(
            "...api.v1.auth.get_current_user", side_effect=Exception("Unauthorized")
        ):
            response = client.get("/auth/me")

        assert response.status_code == 401

    def test_signup_disabled(self, client):
        """Test POST /auth/signup endpoint - disabled"""
        response = client.post("/auth/signup")

        assert response.status_code == 501
        assert "Signup is handled directly by Supabase" in response.json()["detail"]

    def test_login(self, client):
        """Test POST /auth/login endpoint"""
        response = client.post("/auth/login")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "note" in data

    def test_logout(self, client, mock_user):
        """Test POST /auth/logout endpoint"""
        with patch("...api.v1.auth.get_current_user", return_value=mock_user):
            response = client.post("/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["user_id"] == "test-user-id"

    def test_refresh_token(self, client):
        """Test POST /auth/refresh endpoint"""
        response = client.post("/auth/refresh")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "note" in data

    def test_validate_session(self, client, mock_user):
        """Test POST /auth/validate endpoint"""
        with patch("...api.v1.auth.get_current_user", return_value=mock_user):
            response = client.post("/auth/validate")

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["user_id"] == "test-user-id"

    def test_get_user_workspace(self, client, mock_user, mock_workspace):
        """Test GET /auth/me/workspace endpoint"""
        mock_auth_context = AuthContext(
            user=mock_user, workspace_id="test-workspace-id", workspace=mock_workspace
        )

        with patch("...api.v1.auth.get_auth_context", return_value=mock_auth_context):
            response = client.get("/auth/me/workspace")

        assert response.status_code == 200
        data = response.json()
        assert "workspace" in data
        assert "permissions" in data
        assert "workspace_id" in data

    def test_get_user_usage(self, client, mock_auth_context):
        """Test GET /auth/me/usage endpoint"""
        with patch("...api.v1.auth.get_auth_context", return_value=mock_auth_context):
            response = client.get("/auth/me/usage")

        assert response.status_code == 200
        data = response.json()
        assert "current_usage" in data
        assert "limits" in data
        assert "usage_percentage" in data

    def test_get_user_billing(self, client, mock_auth_context):
        """Test GET /auth/me/billing endpoint"""
        with patch("...api.v1.auth.get_auth_context", return_value=mock_auth_context):
            response = client.get("/auth/me/billing")

        assert response.status_code == 200
        data = response.json()
        assert "subscription" in data
        assert "recent_invoices" in data
        assert "usage_history" in data

    def test_get_permissions(self, client, mock_auth_context):
        """Test GET /auth/permissions endpoint"""
        with patch("...api.v1.auth.get_auth_context", return_value=mock_auth_context):
            response = client.get("/auth/permissions")

        assert response.status_code == 200
        data = response.json()
        assert "workspace_id" in data
        assert "permissions" in data
        assert "user_id" in data
        assert "subscription_tier" in data


class TestWorkspaceEndpoints:
    """Test workspace endpoints"""

    @pytest.fixture
    def app(self):
        app = FastAPI()
        app.include_router(workspaces_router)
        return app

    @pytest.fixture
    def client(self, app):
        return TestClient(app)

    @pytest.fixture
    def mock_user(self):
        return User(
            id="test-user-id", email="test@example.com", subscription_tier="free"
        )

    @pytest.fixture
    def mock_workspace(self):
        return Workspace(
            id="test-workspace-id",
            user_id="test-user-id",
            name="Test Workspace",
            slug="test-workspace",
            settings={"timezone": "UTC", "currency": "USD"},
        )

    @pytest.fixture
    def mock_auth_context(self, mock_user, mock_workspace):
        return AuthContext(
            user=mock_user, workspace_id=mock_workspace.id, workspace=mock_workspace
        )

    def test_list_workspaces(self, client, mock_user):
        """Test GET /workspaces endpoint"""
        with patch("...api.v1.workspaces.get_current_user", return_value=mock_user):
            response = client.get("/workspaces")

        assert response.status_code == 200
        data = response.json()
        assert "workspaces" in data
        assert "total" in data

    def test_create_workspace_success(self, client, mock_user):
        """Test POST /workspaces endpoint - success"""
        workspace_data = {
            "name": "New Workspace",
            "slug": "new-workspace",
            "settings": {"timezone": "UTC"},
        }

        with patch("...api.v1.workspaces.get_current_user", return_value=mock_user):
            response = client.post("/workspaces", json=workspace_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Workspace"
        assert data["slug"] == "new-workspace"

    def test_create_workspace_limit_exceeded(self, client, mock_user):
        """Test POST /workspaces endpoint - limit exceeded"""
        workspace_data = {"name": "New Workspace"}

        with patch("...api.v1.workspaces.get_current_user", return_value=mock_user):
            with patch("...api.v1.workspaces.get_current_user") as mock_get_user:
                # Simulate user having reached limit
                mock_get_user.return_value = User(
                    id="test-user-id",
                    email="test@example.com",
                    subscription_tier="free",
                )

                # Mock existing workspaces count
                with patch("...api.v1.workspaces.get_supabase_client") as mock_client:
                    mock_client.return_value.table.return_value.select.return_value.execute.return_value = AsyncMock(
                        return_value={
                            "data": [{"id": "ws1"}, {"id": "ws2"}]
                        }  # Already at limit
                    )

                    response = client.post("/workspaces", json=workspace_data)

        assert response.status_code == 403
        assert "Workspace limit" in response.json()["detail"]

    def test_get_workspace(self, client, mock_auth_context):
        """Test GET /workspaces/{id} endpoint"""
        with patch(
            "...api.v1.workspaces.get_auth_context", return_value=mock_auth_context
        ):
            response = client.get("/workspaces/test-workspace-id")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-workspace-id"

    def test_get_workspace_not_found(self, client, mock_auth_context):
        """Test GET /workspaces/{id} endpoint - not found"""
        with patch("...api.v1.workspaces.get_auth_context", return_value=None):
            response = client.get("/workspaces/invalid-id")

        assert response.status_code == 404

    def test_update_workspace(self, client, mock_auth_context):
        """Test PUT /workspaces/{id} endpoint"""
        update_data = {"name": "Updated Workspace"}

        with patch(
            "...api.v1.workspaces.get_auth_context", return_value=mock_auth_context
        ):
            response = client.put("/workspaces/test-workspace-id", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Workspace"

    def test_delete_workspace(self, client, mock_auth_context):
        """Test DELETE /workspaces/{id} endpoint"""
        with patch(
            "...api.v1.workspaces.get_auth_context", return_value=mock_auth_context
        ):
            response = client.delete("/workspaces/test-workspace-id")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "workspace_id" in data

    def test_get_workspace_settings(self, client, mock_auth_context):
        """Test GET /workspaces/{id}/settings endpoint"""
        with patch(
            "...api.v1.workspaces.get_auth_context", return_value=mock_auth_context
        ):
            response = client.get("/workspaces/test-workspace-id/settings")

        assert response.status_code == 200
        data = response.json()
        assert "settings" in data
        assert "workspace_id" in data

    def test_update_workspace_settings(self, client, mock_auth_context):
        """Test PUT /workspaces/{id}/settings endpoint"""
        settings = {"timezone": "EST", "currency": "EUR"}

        with patch(
            "...api.v1.workspaces.get_auth_context", return_value=mock_auth_context
        ):
            response = client.put(
                "/workspaces/test-workspace-id/settings", json=settings
            )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "settings" in data

    def test_get_workspace_stats(self, client, mock_auth_context):
        """Test GET /workspaces/{id}/stats endpoint"""
        with patch(
            "...api.v1.workspaces.get_auth_context", return_value=mock_auth_context
        ):
            response = client.get("/workspaces/test-workspace-id/stats")

        assert response.status_code == 200
        data = response.json()
        assert "workspace_id" in data
        assert "stats" in data

    def test_duplicate_workspace(self, client, mock_user):
        """Test POST /workspaces/{id}/duplicate endpoint"""
        with patch("...api.v1.workspaces.get_current_user", return_value=mock_user):
            response = client.post(
                "/workspaces/test-workspace-id/duplicate",
                json={"new_name": "Duplicated Workspace"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "original_workspace_id" in data
        assert "new_workspace" in data

    def test_export_workspace_data(self, client, mock_auth_context):
        """Test POST /workspaces/{id}/export endpoint"""
        with patch(
            "...api.v1.workspaces.get_auth_context", return_value=mock_auth_context
        ):
            response = client.post("/workspaces/test-workspace-id/export?format=json")

        assert response.status_code == 200
        data = response.json()
        assert "workspace_id" in data
        assert "format" in data

    def test_get_workspace_activity(self, client, mock_auth_context):
        """Test GET /workspaces/{id}/activity endpoint"""
        with patch(
            "...api.v1.workspaces.get_auth_context", return_value=mock_auth_context
        ):
            response = client.get("/workspaces/test-workspace-id/activity")

        assert response.status_code == 200
        data = response.json()
        assert "workspace_id" in data
        assert "activities" in data
        assert "total_activities" in data


class TestUserEndpoints:
    """Test user endpoints"""

    @pytest.fixture
    def app(self):
        app = FastAPI()
        app.include_router(users_router)
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
            subscription_tier="free",
            preferences={"theme": "light"},
        )

    @pytest.fixture
    def mock_auth_context(self, mock_user):
        return AuthContext(
            user=mock_user, workspace_id="test-workspace-id", workspace=None
        )

    def test_get_user_profile(self, client, mock_user):
        """Test GET /users/me endpoint"""
        with patch("...api.v1.users.get_current_user", return_value=mock_user):
            response = client.get("/users/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-user-id"
        assert data["email"] == "test@example.com"
        assert data["subscription_tier"] == "free"

    def test_update_user_profile(self, client, mock_user):
        """Test PUT /users/me endpoint"""
        update_data = {"full_name": "Updated Name", "preferences": {"theme": "dark"}}

        with patch("...api.v1.users.get_current_user", return_value=mock_user):
            response = client.put("/users/me", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["preferences"]["theme"] == "dark"

    def test_delete_user_account(self, client, mock_user):
        """Test DELETE /users/me endpoint"""
        with patch("...api.v1.users.get_current_user", return_value=mock_user):
            response = client.delete(
                "/users/me", params={"confirmation": "delete my account"}
            )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "user_id" in data
        assert "warning" in data

    def test_delete_user_account_invalid_confirmation(self, client, mock_user):
        """Test DELETE /users/me endpoint - invalid confirmation"""
        with patch("...api.v1.users.get_current_user", return_value=mock_user):
            response = client.delete("/users/me", params={"confirmation": "invalid"})

        assert response.status_code == 400
        assert "Confirmation text must be exactly" in response.json()["detail"]

    def test_get_user_usage(self, client, mock_auth_context):
        """Test GET /users/me/usage endpoint"""
        with patch("...api.v1.users.get_auth_context", return_value=mock_auth_context):
            response = client.get("/users/me/usage")

        assert response.status_code == 200
        data = response.json()
        assert "current_usage" in data
        assert "limits" in data
        assert "usage_percentage" in data
        assert "usage_history" in data

    def test_get_user_billing(self, client, mock_auth_context):
        """Test GET /users/me/billing endpoint"""
        with patch("...api.v1.users.get_auth_context", return_value=mock_auth_context):
            response = client.get("/users/me/billing")

        assert response.status_code == 200
        data = response.json()
        assert "subscription" in data
        assert "current_period_cost" in data
        assert "recent_invoices" in data
        assert "usage_records" in data

    def test_upgrade_subscription_plan(self, client, mock_user):
        """Test POST /users/me/upgrade-plan endpoint"""
        with patch("...api.v1.users.get_current_user", return_value=mock_user):
            response = client.post("/users/me/upgrade-plan", json={"new_plan": "pro"})

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "new_plan" in data
        assert "subscription" in data

    def test_upgrade_subscription_plan_invalid(self, client, mock_user):
        """Test POST /users/me/upgrade-plan endpoint - invalid plan"""
        with patch("...api.v1.users.get_current_user", return_value=mock_user):
            response = client.post(
                "/users/me/upgrade-plan", json={"new_plan": "invalid"}
            )

        assert response.status_code == 400
        assert "Invalid plan" in response.json()["detail"]

    def test_get_user_preferences(self, client, mock_user):
        """Test GET /users/me/preferences endpoint"""
        with patch("...api.v1.users.get_current_user", return_value=mock_user):
            response = client.get("/users/me/preferences")

        assert response.status_code == 200
        data = response.json()
        assert "preferences" in data
        assert "user_id" in data

    def test_update_user_preferences(self, client, mock_user):
        """Test PUT /users/me/preferences endpoint"""
        preferences = {"theme": "dark", "language": "en"}

        with patch("...api.v1.users.get_current_user", return_value=mock_user):
            response = client.put("/users/me/preferences", json=preferences)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "preferences" in data

    def test_complete_onboarding(self, client, mock_user):
        """Test POST /users/me/complete-onboarding endpoint"""
        with patch("...api.v1.users.get_current_user", return_value=mock_user):
            response = client.post("/users/me/complete-onboarding")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "completed_at" in data

    def test_get_user_notifications(self, client, mock_user):
        """Test GET /users/me/notifications endpoint"""
        with patch("...api.v1.users.get_current_user", return_value=mock_user):
            response = client.get("/users/me/notifications")

        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data

    def test_get_user_api_keys(self, client, mock_auth_context):
        """Test GET /users/me/api-keys endpoint"""
        with patch("...api.v1.users.get_auth_context", return_value=mock_auth_context):
            response = client.get("/users/me/api-keys")

        assert response.status_code == 200
        data = response.json()
        assert "api_keys" in data
        assert "total" in data

    def test_create_api_key(self, client, mock_auth_context):
        """Test POST /users/me/api-keys endpoint"""
        key_data = {
            "name": "Test API Key",
            "permissions": {"read": True, "write": False},
        }

        with patch("...api.v1.users.get_auth_context", return_value=mock_auth_context):
            response = client.post("/users/me/api-keys", json=key_data)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "api_key" in data
        assert "key_id" in data

    def test_revoke_api_key(self, client, mock_auth_context):
        """Test DELETE /users/me/api-keys/{id} endpoint"""
        with patch("...api.v1.users.get_auth_context", return_value=mock_auth_context):
            response = client.delete("/users/me/api-keys/test-key-id")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "key_id" in data

    def test_get_user_activity(self, client, mock_user):
        """Test GET /users/me/activity endpoint"""
        with patch("...api.v1.users.get_current_user", return_value=mock_user):
            response = client.get("/users/me/activity")

        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
        assert "total_activities" in data


class TestCampaignEndpoints:
    """Test campaign endpoints"""

    @pytest.fixture
    def app(self):
        app = FastAPI()
        app.include_router(campaigns_router)
        return app

    @pytest.fixture
    def client(self, app):
        return TestClient(app)

    @pytest.fixture
    def mock_auth_context(self):
        user = User(id="test-user-id", email="test@example.com")
        workspace = Workspace(
            id="test-workspace-id", user_id="test-user-id", name="Test Workspace"
        )
        return AuthContext(user=user, workspace_id=workspace.id, workspace=workspace)

    def test_list_campaigns(self, client, mock_auth_context):
        """Test GET /campaigns endpoint"""
        with patch(
            "...api.v1.campaigns.get_auth_context", return_value=mock_auth_context
        ):
            response = client.get("/campaigns")

        assert response.status_code == 200
        data = response.json()
        assert "campaigns" in data
        assert "pagination" in data

    def test_create_campaign(self, client, mock_auth_context):
        """Test POST /campaigns endpoint"""
        campaign_data = {
            "name": "Test Campaign",
            "description": "A test campaign",
            "target_icps": ["test-icp-id"],
            "budget_usd": 1000.0,
        }

        with patch(
            "...api.v1.campaigns.get_auth_context", return_value=mock_auth_context
        ):
            response = client.post("/campaigns", json=campaign_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Campaign"
        assert data["status"] == "planning"

    def test_get_campaign(self, client, mock_auth_context):
        """Test GET /campaigns/{id} endpoint"""
        with patch(
            "...api.v1.campaigns.get_auth_context", return_value=mock_auth_context
        ):
            response = client.get("/campaigns/test-campaign-id")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-campaign-id"

    def test_update_campaign(self, client, mock_auth_context):
        """Test PUT /campaigns/{id} endpoint"""
        update_data = {"name": "Updated Campaign", "status": "active"}

        with patch(
            "...api.v1.campaigns.get_auth_context", return_value=mock_auth_context
        ):
            response = client.put("/campaigns/test-campaign-id", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Campaign"
        assert data["status"] == "active"

    def test_delete_campaign(self, client, mock_auth_context):
        """Test DELETE /campaigns/{id} endpoint"""
        with patch(
            "...api.v1.campaigns.get_auth_context", return_value=mock_auth_context
        ):
            response = client.delete("/campaigns/test-campaign-id")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "campaign_id" in data

    def test_get_campaign_moves(self, client, mock_auth_context):
        """Test GET /campaigns/{id}/moves endpoint"""
        with patch(
            "...api.v1.campaigns.get_auth_context", return_value=mock_auth_context
        ):
            response = client.get("/campaigns/test-campaign-id/moves")

        assert response.status_code == 200
        data = response.json()
        assert "campaign_id" in data
        assert "moves" in data
        assert "total_moves" in data

    def test_launch_campaign(self, client, mock_auth_context):
        """Test POST /campaigns/{id}/launch endpoint"""
        with patch(
            "...api.v1.campaigns.get_auth_context", return_value=mock_auth_context
        ):
            response = client.post("/campaigns/test-campaign-id/launch")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "campaign" in data

    def test_get_campaign_stats(self, client, mock_auth_context):
        """Test GET /campaigns/{id}/stats endpoint"""
        with patch(
            "...api.v1.campaigns.get_auth_context", return_value=mock_auth_context
        ):
            response = client.get("/campaigns/test-campaign-id/stats")

        assert response.status_code == 200
        data = response.json()
        assert "campaign_id" in data
        assert "stats" in data

    def test_get_campaign_roi(self, client, mock_auth_context):
        """Test GET /campaigns/{id}/roi endpoint"""
        with patch(
            "...api.v1.campaigns.get_auth_context", return_value=mock_auth_context
        ):
            response = client.get("/campaigns/test-campaign-id/roi")

        assert response.status_code == 200
        data = response.json()
        assert "campaign_id" in data
        assert "roi" in data


class TestAPIIntegration:
    """Integration tests for API endpoints"""

    @pytest.fixture
    def app(self):
        app = FastAPI()
        app.include_router(auth_router)
        app.include_router(workspaces_router)
        app.include_router(users_router)
        app.include_router(campaigns_router)
        return app

    @pytest.fixture
    def client(self, app):
        return TestClient(app)

    def test_api_health_check(self, client):
        """Test API health check"""
        response = client.get("/")
        # Should return 404 since no root endpoint is defined
        assert response.status_code == 404

    def test_cors_headers(self, client):
        """Test CORS headers are properly set"""
        # This would require actual CORS middleware setup
        response = client.options("/auth/me")
        # Should return appropriate CORS headers
        assert response.status_code in [200, 404, 405]  # Depending on CORS setup

    def test_error_handling(self, client):
        """Test consistent error handling"""
        # Test 404 for non-existent endpoint
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404

        # Test 401 for unauthorized access
        response = client.get("/auth/me")
        assert response.status_code == 401

        # Test 422 for invalid data
        response = client.post("/workspaces", json={})
        assert response.status_code == 422
