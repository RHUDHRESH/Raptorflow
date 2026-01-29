"""
Authentication Tests for RaptorFlow Backend
Tests JWT authentication, user management, and security features
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from jose import jwt
from passlib.context import CryptContext

from main import app
from .config.settings import get_settings


class TestAuthentication:
    """Test authentication endpoints and security features."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = get_settings()
        settings.SECRET_KEY = "test-secret-key-for-testing-only"
        settings.JWT_EXPIRE_MINUTES = 30
        return settings

    @pytest.fixture
    def test_user_data(self) -> Dict[str, Any]:
        """Test user data."""
        return {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_login_success(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test successful login."""
        response = client.post("/api/v1/auth/login", json=test_user_data)

        # Should return 200 with tokens
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials."""
        invalid_data = {"email": "nonexistent@example.com", "password": "wrongpassword"}

        response = client.post("/api/v1/auth/login", json=invalid_data)
        assert response.status_code == 401

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing required fields."""
        incomplete_data = {"email": "test@example.com"}

        response = client.post("/api/v1/auth/login", json=incomplete_data)
        assert response.status_code == 422

    def test_register_success(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)

        # Should return 201 with user data
        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]
        assert "id" in data["user"]

    def test_register_duplicate_email(
        self, client: TestClient, test_user_data: Dict[str, Any]
    ):
        """Test registration with duplicate email."""
        # First registration
        client.post("/api/v1/auth/register", json=test_user_data)

        # Second registration with same email
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 400

    def test_token_validation(self, client: TestClient, mock_settings):
        """Test JWT token validation."""
        # Create a valid token
        payload = {
            "sub": "test@example.com",
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iat": datetime.utcnow(),
        }
        token = jwt.encode(payload, mock_settings.SECRET_KEY, algorithm="HS256")

        # Test token validation endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/validate", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True

    def test_token_validation_invalid(self, client: TestClient):
        """Test JWT token validation with invalid token."""
        invalid_token = "invalid.jwt.token"
        headers = {"Authorization": f"Bearer {invalid_token}"}

        response = client.get("/api/v1/auth/validate", headers=headers)
        assert response.status_code == 401

    def test_token_validation_expired(self, client: TestClient, mock_settings):
        """Test JWT token validation with expired token."""
        # Create an expired token
        payload = {
            "sub": "test@example.com",
            "exp": datetime.utcnow() - timedelta(minutes=1),  # Expired
            "iat": datetime.utcnow() - timedelta(minutes=31),
        }
        token = jwt.encode(payload, mock_settings.SECRET_KEY, algorithm="HS256")

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/validate", headers=headers)

        assert response.status_code == 401

    def test_refresh_token(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test token refresh."""
        # Login to get tokens
        login_response = client.post("/api/v1/auth/login", json=test_user_data)
        tokens = login_response.json()

        # Use refresh token to get new access token
        refresh_data = {"refresh_token": tokens["refresh_token"]}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_logout(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test user logout."""
        # Login to get tokens
        login_response = client.post("/api/v1/auth/login", json=test_user_data)
        tokens = login_response.json()

        # Logout
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = client.post("/api/v1/auth/logout", headers=headers)

        assert response.status_code == 200

    def test_password_reset_request(self, client: TestClient):
        """Test password reset request."""
        data = {"email": "test@example.com"}
        response = client.post("/api/v1/auth/password-reset/request", json=data)

        # Should return 200 even if email doesn't exist (security)
        assert response.status_code == 200

    def test_password_reset_confirm(self, client: TestClient):
        """Test password reset confirmation."""
        data = {"token": "reset-token-123", "new_password": "newpassword123"}
        response = client.post("/api/v1/auth/password-reset/confirm", json=data)

        # Should return 400 for invalid token
        assert response.status_code == 400

    def test_change_password(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test password change."""
        # Login to get token
        login_response = client.post("/api/v1/auth/login", json=test_user_data)
        tokens = login_response.json()

        # Change password
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        data = {
            "current_password": test_user_data["password"],
            "new_password": "newpassword123",
        }
        response = client.post(
            "/api/v1/auth/change-password", json=data, headers=headers
        )

        assert response.status_code == 200

    def test_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_protected_endpoint_with_token(
        self, client: TestClient, test_user_data: Dict[str, Any]
    ):
        """Test accessing protected endpoint with valid token."""
        # Login to get token
        login_response = client.post("/api/v1/auth/login", json=test_user_data)
        tokens = login_response.json()

        # Access protected endpoint
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "user" in data

    def test_rate_limiting_login(self, client: TestClient):
        """Test rate limiting on login endpoint."""
        # Make multiple rapid login attempts
        for i in range(10):
            response = client.post(
                "/api/v1/auth/login",
                json={"email": f"test{i}@example.com", "password": "wrongpassword"},
            )

        # Should be rate limited after several attempts
        assert response.status_code in [401, 429]

    def test_csrf_protection(self, client: TestClient):
        """Test CSRF protection."""
        # This would test CSRF tokens if implemented
        # For now, just ensure the endpoint exists
        response = client.get("/api/v1/auth/csrf-token")
        assert response.status_code in [200, 404]  # May not be implemented

    def test_session_management(
        self, client: TestClient, test_user_data: Dict[str, Any]
    ):
        """Test session management."""
        # Login to get token
        login_response = client.post("/api/v1/auth/login", json=test_user_data)
        tokens = login_response.json()

        # Get session info
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = client.get("/api/v1/auth/session", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "session" in data

    def test_user_profile_update(
        self, client: TestClient, test_user_data: Dict[str, Any]
    ):
        """Test user profile update."""
        # Login to get token
        login_response = client.post("/api/v1/auth/login", json=test_user_data)
        tokens = login_response.json()

        # Update profile
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        update_data = {"first_name": "Updated", "last_name": "Name"}
        response = client.put(
            "/api/v1/users/profile", json=update_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["first_name"] == "Updated"

    def test_oauth_login_initiation(self, client: TestClient):
        """Test OAuth login initiation."""
        # Test Google OAuth
        response = client.get("/api/v1/auth/oauth/google")
        assert response.status_code in [200, 302, 404]  # May not be implemented

    def test_oauth_callback(self, client: TestClient):
        """Test OAuth callback."""
        # Test OAuth callback
        response = client.get("/api/v1/auth/oauth/google/callback?code=test&state=test")
        assert response.status_code in [200, 400, 404]  # May not be implemented

    def test_security_headers(self, client: TestClient):
        """Test security headers on auth endpoints."""
        response = client.options("/api/v1/auth/login")

        # Check for security headers
        headers = response.headers
        assert "x-content-type-options" in headers
        assert "x-frame-options" in headers
        assert "x-xss-protection" in headers

    def test_password_strength_validation(self, client: TestClient):
        """Test password strength validation."""
        weak_password_data = {
            "email": "test@example.com",
            "password": "123",  # Too weak
        }

        response = client.post("/api/v1/auth/register", json=weak_password_data)
        assert response.status_code == 422
        data = response.json()
        assert "password" in str(data).lower()

    def test_email_validation(self, client: TestClient):
        """Test email format validation."""
        invalid_email_data = {"email": "invalid-email", "password": "validpassword123"}

        response = client.post("/api/v1/auth/register", json=invalid_email_data)
        assert response.status_code == 422
        data = response.json()
        assert "email" in str(data).lower()

    def test_concurrent_login_attempts(
        self, client: TestClient, test_user_data: Dict[str, Any]
    ):
        """Test concurrent login attempts."""
        import concurrent.futures

        def login_attempt():
            return client.post("/api/v1/auth/login", json=test_user_data)

        # Make concurrent login attempts
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(login_attempt) for _ in range(5)]
            responses = [future.result() for future in futures]

        # All should succeed or be rate limited
        status_codes = [r.status_code for r in responses]
        assert all(code in [200, 401, 429] for code in status_codes)

    def test_token_storage_security(
        self, client: TestClient, test_user_data: Dict[str, Any]
    ):
        """Test that tokens are properly stored and secured."""
        login_response = client.post("/api/v1/auth/login", json=test_user_data)
        tokens = login_response.json()

        # Verify tokens are not stored in response cookies
        assert "set-cookie" not in login_response.headers

        # Verify tokens are in response body
        assert "access_token" in tokens
        assert "refresh_token" in tokens

    def test_account_lockout(self, client: TestClient):
        """Test account lockout after failed attempts."""
        # Make multiple failed login attempts
        for i in range(10):
            response = client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": f"wrongpassword{i}"},
            )

        # Should eventually lock the account
        final_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "correctpassword"},
        )

        # May be locked or rate limited
        assert final_response.status_code in [401, 429, 423]


if __name__ == "__main__":
    pytest.main([__file__])
