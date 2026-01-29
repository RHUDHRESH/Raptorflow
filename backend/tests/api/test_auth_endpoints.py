"""
Comprehensive tests for authentication endpoints
Tests success paths, failure paths, and edge cases
"""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from backend.core.models import User
from backend.main import app
from backend.services.profile_service import ProfileError

client = TestClient(app)


class TestAuthEndpoints:
    """Test authentication endpoints with comprehensive coverage"""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing"""
        return User(
            id="test-user-123",
            email="test@example.com",
            full_name="Test User",
            avatar_url=None,
            subscription_tier="free",
            role="user",
        )

    @pytest.fixture
    def mock_profile_response(self):
        """Create a mock profile verification response"""
        return {
            "profile_exists": True,
            "workspace_exists": True,
            "workspace_id": "test-workspace-123",
            "subscription_plan": "pro",
            "subscription_status": "active",
            "needs_payment": False,
        }

    @pytest.fixture
    def mock_ensure_response(self):
        """Create a mock ensure profile response"""
        return {
            "user_id": "test-user-123",
            "workspace_id": "test-workspace-123",
            "subscription_plan": "pro",
            "subscription_status": "active",
        }

    # ==================== SUCCESS TESTS ====================

    @patch("backend.api.v1.auth.get_current_user")
    @patch("backend.services.profile_service.ProfileService.ensure_profile")
    def test_ensure_profile_success(
        self, mock_ensure, mock_get_user, mock_user, mock_ensure_response
    ):
        """Test successful profile creation"""
        mock_get_user.return_value = mock_user
        mock_ensure.return_value = mock_ensure_response

        response = client.post("/api/v1/auth/ensure-profile")

        assert response.status_code == 200
        data = response.json()
        assert data["workspace_id"] == "test-workspace-123"
        assert data["subscription_plan"] == "pro"
        assert data["subscription_status"] == "active"

    @patch("backend.api.v1.auth.get_current_user")
    @patch("backend.services.profile_service.ProfileService.verify_profile")
    def test_verify_profile_success(
        self, mock_verify, mock_get_user, mock_user, mock_profile_response
    ):
        """Test successful profile verification"""
        mock_get_user.return_value = mock_user
        mock_verify.return_value = mock_profile_response

        response = client.get("/api/v1/auth/verify-profile")

        assert response.status_code == 200
        data = response.json()
        assert data["profile_exists"] is True
        assert data["workspace_exists"] is True
        assert data["needs_payment"] is False

    @patch("backend.api.v1.auth.get_current_user")
    def test_get_current_user_success(self, mock_get_user, mock_user):
        """Test successful current user retrieval"""
        mock_get_user.return_value = mock_user

        response = client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-user-123"
        assert data["email"] == "test@example.com"

    # ==================== FAILURE TESTS ====================

    @patch("backend.api.v1.auth.get_current_user")
    @patch("backend.services.profile_service.ProfileService.ensure_profile")
    def test_ensure_profile_service_error(self, mock_ensure, mock_get_user, mock_user):
        """Test profile service error handling"""
        mock_get_user.return_value = mock_user
        mock_ensure.side_effect = ProfileError(
            "Profile creation failed",
            "PROFILE_CREATION_ERROR",
            {"user_id": mock_user.id},
        )

        response = client.post("/api/v1/auth/ensure-profile")

        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "PROFILE_CREATION_ERROR"
        assert "Profile creation failed" in data["message"]
        assert data["context"]["user_id"] == "test-user-123"

    @patch("backend.api.v1.auth.get_current_user")
    @patch("backend.services.profile_service.ProfileService.verify_profile")
    def test_verify_profile_service_error(self, mock_verify, mock_get_user, mock_user):
        """Test profile verification service error"""
        mock_get_user.return_value = mock_user
        mock_verify.side_effect = ProfileError(
            "Profile verification failed",
            "PROFILE_VERIFICATION_ERROR",
            {"user_id": mock_user.id},
        )

        response = client.get("/api/v1/auth/verify-profile")

        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "PROFILE_VERIFICATION_ERROR"

    @patch("backend.api.v1.auth.get_current_user")
    @patch("backend.services.profile_service.ProfileService.ensure_profile")
    def test_ensure_profile_unexpected_error(
        self, mock_ensure, mock_get_user, mock_user
    ):
        """Test unexpected error handling"""
        mock_get_user.return_value = mock_user
        mock_ensure.side_effect = Exception("Database connection failed")

        response = client.post("/api/v1/auth/ensure-profile")

        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]

    # ==================== EDGE CASE TESTS ====================

    @patch("backend.api.v1.auth.get_current_user")
    @patch("backend.services.profile_service.ProfileService.verify_profile")
    def test_verify_profile_missing_workspace(
        self, mock_verify, mock_get_user, mock_user
    ):
        """Test profile verification when workspace is missing"""
        mock_get_user.return_value = mock_user
        mock_verify.return_value = {
            "profile_exists": True,
            "workspace_exists": False,
            "workspace_id": None,
            "subscription_plan": "free",
            "subscription_status": "trial",
            "needs_payment": True,
        }

        response = client.get("/api/v1/auth/verify-profile")

        assert response.status_code == 200
        data = response.json()
        assert data["workspace_exists"] is False
        assert data["needs_payment"] is True

    @patch("backend.api.v1.auth.get_current_user")
    @patch("backend.services.profile_service.ProfileService.verify_profile")
    def test_verify_profile_missing_profile(
        self, mock_verify, mock_get_user, mock_user
    ):
        """Test profile verification when profile is missing"""
        mock_get_user.return_value = mock_user
        mock_verify.return_value = {
            "profile_exists": False,
            "workspace_exists": False,
            "workspace_id": None,
            "subscription_plan": None,
            "subscription_status": None,
            "needs_payment": True,
            "error": "Profile not found",
        }

        response = client.get("/api/v1/auth/verify-profile")

        assert response.status_code == 200
        data = response.json()
        assert data["profile_exists"] is False
        assert data["error"] == "Profile not found"

    @patch("backend.api.v1.auth.get_current_user")
    @patch("backend.services.profile_service.ProfileService.verify_profile")
    def test_verify_subscription_states(self, mock_verify, mock_get_user, mock_user):
        """Test various subscription states"""
        mock_get_user.return_value = mock_user

        # Test trial state
        mock_verify.return_value = {
            "profile_exists": True,
            "workspace_exists": True,
            "workspace_id": "test-workspace",
            "subscription_plan": "pro",
            "subscription_status": "trialing",
            "needs_payment": False,
        }
        response = client.get("/api/v1/auth/verify-profile")
        assert response.status_code == 200
        assert response.json()["subscription_status"] == "trialing"

        # Test past_due state
        mock_verify.return_value = {
            "profile_exists": True,
            "workspace_exists": True,
            "workspace_id": "test-workspace",
            "subscription_plan": "pro",
            "subscription_status": "past_due",
            "needs_payment": True,
        }
        response = client.get("/api/v1/auth/verify-profile")
        assert response.status_code == 200
        assert response.json()["needs_payment"] is True

    # ==================== AUTHENTICATION TESTS ====================

    def test_unprotected_endpoint_access(self):
        """Test that unprotected endpoints work without authentication"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401  # Should require authentication

    @patch("backend.api.v1.auth.get_current_user")
    def test_switch_workspace_success(self, mock_get_user, mock_user):
        """Test successful workspace switching"""
        mock_get_user.return_value = mock_user

        with patch("backend.core.supabase_mgr.get_supabase_client") as mock_client:
            mock_supabase = Mock()
            mock_client.return_value = mock_supabase

            # Mock workspace ownership check
            mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = {
                "id": "test-workspace",
                "name": "Test Workspace",
                "owner_id": "test-user-123",
            }

            response = client.post(
                "/api/v1/auth/switch-workspace?workspace_id=test-workspace"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["workspace_id"] == "test-workspace"
            assert "switched successfully" in data["message"]

    @patch("backend.api.v1.auth.get_current_user")
    def test_switch_workspace_not_found(self, mock_get_user, mock_user):
        """Test workspace switching when workspace not found"""
        mock_get_user.return_value = mock_user

        with patch("backend.core.supabase_mgr.get_supabase_client") as mock_client:
            mock_supabase = Mock()
            mock_client.return_value = mock_supabase

            # Mock workspace not found
            mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = (
                None
            )

            # Mock membership check also fails
            mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = (
                None
            )

            response = client.post(
                "/api/v1/auth/switch-workspace?workspace_id=nonexistent"
            )

            assert response.status_code == 404
            data = response.json()
            assert "not found or access denied" in data["detail"]

    # ==================== INTEGRATION TESTS ====================

    @patch("backend.api.v1.auth.get_current_user")
    @patch("backend.services.profile_service.ProfileService.ensure_profile")
    @patch("backend.services.profile_service.ProfileService.verify_profile")
    def test_full_profile_flow(
        self,
        mock_verify,
        mock_ensure,
        mock_get_user,
        mock_user,
        mock_ensure_response,
        mock_profile_response,
    ):
        """Test complete profile creation and verification flow"""
        mock_get_user.return_value = mock_user
        mock_ensure.return_value = mock_ensure_response
        mock_verify.return_value = mock_profile_response

        # First ensure profile
        ensure_response = client.post("/api/v1/auth/ensure-profile")
        assert ensure_response.status_code == 200

        # Then verify profile
        verify_response = client.get("/api/v1/auth/verify-profile")
        assert verify_response.status_code == 200

        data = verify_response.json()
        assert data["profile_exists"] is True
        assert data["workspace_exists"] is False  # Mock data shows no workspace

    # ==================== LOGGING TESTS ====================

    @patch("backend.api.v1.auth.logger")
    @patch("backend.api.v1.auth.get_current_user")
    @patch("backend.services.profile_service.ProfileService.verify_profile")
    def test_logging_on_success(
        self, mock_verify, mock_get_user, mock_logger, mock_user, mock_profile_response
    ):
        """Test that success operations are logged correctly"""
        mock_get_user.return_value = mock_user
        mock_verify.return_value = mock_profile_response

        response = client.get("/api/v1/auth/verify-profile")

        assert response.status_code == 200
        mock_logger.info.assert_called_with(
            "Profile verification successful for user %s", mock_user.id
        )

    @patch("backend.api.v1.auth.logger")
    @patch("backend.api.v1.auth.get_current_user")
    @patch("backend.services.profile_service.ProfileService.verify_profile")
    def test_logging_on_failure(
        self, mock_verify, mock_get_user, mock_logger, mock_user
    ):
        """Test that failures are logged correctly"""
        mock_get_user.return_value = mock_user
        mock_verify.side_effect = ProfileError("Test error", "TEST_ERROR")

        response = client.get("/api/v1/auth/verify-profile")

        assert response.status_code == 422
        mock_logger.error.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
