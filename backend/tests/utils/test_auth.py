"""
Comprehensive tests for authentication and authorization utilities.
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from jose import jwt

from backend.utils.auth import (
    verify_jwt_token,
    get_user_workspace,
    get_current_user_and_workspace,
    get_optional_user
)
from backend.config.settings import get_settings


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = Mock()
    settings.SUPABASE_JWT_SECRET = "test-secret-key-for-testing-purposes-only"
    return settings


@pytest.fixture
def valid_token(mock_settings):
    """Generate a valid JWT token for testing."""
    user_id = str(uuid4())
    payload = {
        "sub": user_id,
        "email": "test@example.com",
        "role": "authenticated",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, mock_settings.SUPABASE_JWT_SECRET, algorithm="HS256")


@pytest.fixture
def expired_token(mock_settings):
    """Generate an expired JWT token for testing."""
    user_id = str(uuid4())
    payload = {
        "sub": user_id,
        "email": "test@example.com",
        "role": "authenticated",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1)
    }
    return jwt.encode(payload, mock_settings.SUPABASE_JWT_SECRET, algorithm="HS256")


@pytest.mark.asyncio
class TestVerifyJwtToken:
    """Test JWT token verification."""

    async def test_verify_valid_token(self, valid_token, mock_settings):
        """Test verification of a valid JWT token."""
        with patch('backend.utils.auth.get_settings', return_value=mock_settings), \
             patch('backend.utils.auth.get_correlation_id', return_value='test-corr-id'):

            result = await verify_jwt_token(valid_token)

            assert "user_id" in result
            assert result["email"] == "test@example.com"
            assert result["role"] == "authenticated"
            assert "exp" in result

    async def test_verify_expired_token(self, expired_token, mock_settings):
        """Test verification of an expired token."""
        with patch('backend.utils.auth.get_settings', return_value=mock_settings), \
             patch('backend.utils.auth.get_correlation_id', return_value='test-corr-id'):

            with pytest.raises(HTTPException) as exc_info:
                await verify_jwt_token(expired_token)

            assert exc_info.value.status_code == 401
            assert "expired" in exc_info.value.detail.lower()

    async def test_verify_invalid_token(self, mock_settings):
        """Test verification of an invalid token."""
        invalid_token = "invalid.token.here"

        with patch('backend.utils.auth.get_settings', return_value=mock_settings), \
             patch('backend.utils.auth.get_correlation_id', return_value='test-corr-id'):

            with pytest.raises(HTTPException) as exc_info:
                await verify_jwt_token(invalid_token)

            assert exc_info.value.status_code == 401

    async def test_verify_token_without_sub(self, mock_settings):
        """Test verification of token without 'sub' claim."""
        payload = {
            "email": "test@example.com",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        token = jwt.encode(payload, mock_settings.SUPABASE_JWT_SECRET, algorithm="HS256")

        with patch('backend.utils.auth.get_settings', return_value=mock_settings), \
             patch('backend.utils.auth.get_correlation_id', return_value='test-corr-id'):

            with pytest.raises(HTTPException) as exc_info:
                await verify_jwt_token(token)

            assert exc_info.value.status_code == 401
            assert "missing user identifier" in exc_info.value.detail.lower()


@pytest.mark.asyncio
class TestGetUserWorkspace:
    """Test workspace resolution for users."""

    async def test_get_workspace_success(self):
        """Test successful workspace retrieval."""
        user_id = str(uuid4())
        workspace_id = str(uuid4())

        mock_result = {"workspace_id": workspace_id}

        with patch('backend.utils.auth.supabase_client.fetch_one',
                   new_callable=AsyncMock, return_value=mock_result), \
             patch('backend.utils.auth.get_correlation_id', return_value='test-corr-id'):

            result = await get_user_workspace(user_id)

            assert str(result) == workspace_id

    async def test_get_workspace_not_found(self):
        """Test workspace retrieval when user has no workspace."""
        user_id = str(uuid4())

        with patch('backend.utils.auth.supabase_client.fetch_one',
                   new_callable=AsyncMock, return_value=None), \
             patch('backend.utils.auth.get_correlation_id', return_value='test-corr-id'):

            result = await get_user_workspace(user_id)

            assert result is None

    async def test_get_workspace_error(self):
        """Test workspace retrieval with database error."""
        user_id = str(uuid4())

        with patch('backend.utils.auth.supabase_client.fetch_one',
                   new_callable=AsyncMock, side_effect=Exception("Database error")), \
             patch('backend.utils.auth.get_correlation_id', return_value='test-corr-id'):

            result = await get_user_workspace(user_id)

            assert result is None


@pytest.mark.asyncio
class TestGetCurrentUserAndWorkspace:
    """Test the main authentication dependency."""

    async def test_get_current_user_success(self, valid_token):
        """Test successful authentication and workspace resolution."""
        workspace_id = str(uuid4())
        mock_credentials = Mock()
        mock_credentials.credentials = valid_token

        mock_settings = Mock()
        mock_settings.SUPABASE_JWT_SECRET = "test-secret-key-for-testing-purposes-only"

        with patch('backend.utils.auth.get_settings', return_value=mock_settings), \
             patch('backend.utils.auth.get_correlation_id', return_value='test-corr-id'), \
             patch('backend.utils.auth.get_user_workspace',
                   new_callable=AsyncMock, return_value=uuid4()):

            result = await get_current_user_and_workspace(mock_credentials)

            assert "user_id" in result
            assert "workspace_id" in result
            assert "email" in result
            assert result["email"] == "test@example.com"

    async def test_get_current_user_no_workspace(self, valid_token):
        """Test authentication when user has no workspace."""
        mock_credentials = Mock()
        mock_credentials.credentials = valid_token

        mock_settings = Mock()
        mock_settings.SUPABASE_JWT_SECRET = "test-secret-key-for-testing-purposes-only"

        with patch('backend.utils.auth.get_settings', return_value=mock_settings), \
             patch('backend.utils.auth.get_correlation_id', return_value='test-corr-id'), \
             patch('backend.utils.auth.get_user_workspace',
                   new_callable=AsyncMock, return_value=None):

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_and_workspace(mock_credentials)

            assert exc_info.value.status_code == 403
            assert "not associated with a workspace" in exc_info.value.detail.lower()


@pytest.mark.asyncio
class TestGetOptionalUser:
    """Test optional authentication dependency."""

    async def test_optional_user_authenticated(self, valid_token):
        """Test optional auth with valid credentials."""
        mock_credentials = Mock()
        mock_credentials.credentials = valid_token

        mock_settings = Mock()
        mock_settings.SUPABASE_JWT_SECRET = "test-secret-key-for-testing-purposes-only"

        workspace_id = uuid4()

        with patch('backend.utils.auth.get_settings', return_value=mock_settings), \
             patch('backend.utils.auth.get_correlation_id', return_value='test-corr-id'), \
             patch('backend.utils.auth.get_user_workspace',
                   new_callable=AsyncMock, return_value=workspace_id):

            result = await get_optional_user(mock_credentials)

            assert result is not None
            assert "user_id" in result

    async def test_optional_user_no_credentials(self):
        """Test optional auth without credentials."""
        result = await get_optional_user(None)
        assert result is None

    async def test_optional_user_invalid_credentials(self):
        """Test optional auth with invalid credentials."""
        mock_credentials = Mock()
        mock_credentials.credentials = "invalid-token"

        mock_settings = Mock()
        mock_settings.SUPABASE_JWT_SECRET = "test-secret-key-for-testing-purposes-only"

        with patch('backend.utils.auth.get_settings', return_value=mock_settings), \
             patch('backend.utils.auth.get_correlation_id', return_value='test-corr-id'):

            result = await get_optional_user(mock_credentials)

            assert result is None
