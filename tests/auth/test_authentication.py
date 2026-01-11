"""
Tests for authentication system
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from ...core.auth import (
    get_auth_context,
    get_current_user,
    get_default_workspace_id,
    get_workspace_for_user,
    get_workspace_id,
    user_owns_workspace,
)
from ...core.jwt import JWTValidator
from ...core.models import AuthContext, JWTPayload, User, Workspace
from ...core.supabase import get_supabase_client


class TestJWTValidator:
    """Test JWT validation functionality"""

    @pytest.fixture
    def validator(self):
        return JWTValidator()

    @pytest.fixture
    def valid_token(self):
        return "Bearer valid.jwt.token"

    @pytest.fixture
    def invalid_token(self):
        return "invalid.token"

    def test_extract_token_valid(self, validator, valid_token):
        """Test extracting valid token"""
        token = validator.extract_token(valid_token)
        assert token == "valid.jwt.token"

    def test_extract_token_invalid(self, validator, invalid_token):
        """Test extracting invalid token"""
        token = validator.extract_token(invalid_token)
        assert token is None

    def test_extract_token_none(self, validator):
        """Test extracting None token"""
        token = validator.extract_token(None)
        assert token is None

    @patch("...core.jwt.jwt.decode")
    def test_verify_token_success(self, mock_decode, validator):
        """Test successful token verification"""
        mock_decode.return_value = {
            "sub": "user-id",
            "email": "test@example.com",
            "exp": datetime.utcnow().timestamp() + 3600,
        }

        payload = validator.verify_token("valid.token")

        assert payload is not None
        assert payload.sub == "user-id"
        assert payload.email == "test@example.com"

    @patch("...core.jwt.jwt.decode")
    def test_verify_token_expired(self, mock_decode, validator):
        """Test expired token verification"""
        mock_decode.side_effect = Exception("Token has expired")

        payload = validator.verify_token("expired.token")

        assert payload is None

    @patch("...core.jwt.jwt.decode")
    def test_verify_token_invalid(self, mock_decode, validator):
        """Test invalid token verification"""
        mock_decode.side_effect = Exception("Invalid token")

        payload = validator.verify_token("invalid.token")

        assert payload is None


class TestAuthentication:
    """Test authentication functions"""

    @pytest.fixture
    def mock_request(self):
        request = MagicMock()
        request.state = MagicMock()
        return request

    @pytest.fixture
    def mock_supabase_client(self):
        client = AsyncMock()
        client.table = MagicMock()
        client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = AsyncMock(
            return_value={
                "data": {
                    "id": "test-user-id",
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "subscription_tier": "free",
                    "budget_limit_monthly": 1.0,
                    "preferences": {"theme": "light"},
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                }
            }
        )
        return client

    @pytest.fixture
    def mock_jwt_validator(self):
        validator = MagicMock()
        validator.extract_token.return_value = "valid.token"
        validator.verify_token.return_value = JWTPayload(
            sub="test-user-id", email="test@example.com", role="authenticated"
        )
        return validator

    @pytest.mark.asyncio
    async def test_get_current_user_success(
        self, mock_request, mock_supabase_client, mock_jwt_validator
    ):
        """Test successful user authentication"""
        with patch("...core.auth.get_jwt_validator", return_value=mock_jwt_validator):
            with patch(
                "...core.auth.get_supabase_client", return_value=mock_supabase_client
            ):
                user = await get_current_user(mock_request, "Bearer valid.token")

        assert user.id == "test-user-id"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.subscription_tier == "free"

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, mock_request):
        """Test authentication with no token"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_request, None)

        assert exc_info.value.status_code == 401
        assert "Authorization header required" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(
        self, mock_request, mock_jwt_validator
    ):
        """Test authentication with invalid token"""
        mock_jwt_validator.extract_token.return_value = None

        with patch("...core.auth.get_jwt_validator", return_value=mock_jwt_validator):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_request, "Bearer invalid.token")

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(
        self, mock_request, mock_supabase_client, mock_jwt_validator
    ):
        """Test authentication when user not found in database"""
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = AsyncMock(
            return_value={"data": None}
        )

        with patch("...core.auth.get_jwt_validator", return_value=mock_jwt_validator):
            with patch(
                "...core.auth.get_supabase_client", return_value=mock_supabase_client
            ):
                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(mock_request, "Bearer valid.token")

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_workspace_id_with_header(
        self, mock_request, mock_supabase_client, mock_user
    ):
        """Test getting workspace ID from header"""
        mock_request.headers = {"x-workspace-id": "test-workspace-id"}
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = AsyncMock(
            return_value={"data": {"id": "test-workspace-id"}}
        )

        with patch("...core.auth.user_owns_workspace", return_value=True):
            workspace_id = await get_workspace_id(
                mock_request, mock_user, "test-workspace-id"
            )

        assert workspace_id == "test-workspace-id"

    @pytest.mark.asyncio
    async def test_get_workspace_id_default(
        self, mock_request, mock_supabase_client, mock_user
    ):
        """Test getting default workspace ID"""
        mock_request.headers = {}
        mock_supabase_client.table.return_value.select.return_value.limit.return_value.single.return_value.execute.return_value = AsyncMock(
            return_value={"data": {"id": "default-workspace-id"}}
        )

        with patch(
            "...core.auth.get_default_workspace_id", return_value="default-workspace-id"
        ):
            workspace_id = await get_workspace_id(mock_request, mock_user)

        assert workspace_id == "default-workspace-id"

    @pytest.mark.asyncio
    async def test_get_workspace_id_invalid_workspace(self, mock_request, mock_user):
        """Test getting workspace ID with invalid workspace"""
        mock_request.headers = {"x-workspace-id": "invalid-workspace-id"}

        with patch("...core.auth.user_owns_workspace", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await get_workspace_id(mock_request, mock_user, "invalid-workspace-id")

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_workspace_id_no_workspace(self, mock_request, mock_user):
        """Test getting workspace ID when no workspace found"""
        mock_request.headers = {}

        with patch("...core.auth.get_default_workspace_id", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await get_workspace_id(mock_request, mock_user)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_auth_context(
        self,
        mock_request,
        mock_supabase_client,
        mock_jwt_validator,
        mock_user,
        mock_workspace,
    ):
        """Test getting auth context"""
        mock_request.headers = {"x-workspace-id": "test-workspace-id"}
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = AsyncMock(
            return_value={"data": {"id": "test-workspace-id"}}
        )

        with patch("...core.auth.get_jwt_validator", return_value=mock_jwt_validator):
            with patch(
                "...core.auth.get_supabase_client", return_value=mock_supabase_client
            ):
                with patch(
                    "...core.auth.get_workspace_for_user", return_value=mock_workspace
                ):
                    auth_context = await get_auth_context(
                        mock_request, mock_user, "test-workspace-id"
                    )

        assert auth_context.user == mock_user
        assert auth_context.workspace_id == "test-workspace-id"
        assert auth_context.workspace == mock_workspace
        assert "read" in auth_context.permissions
        assert "write" in auth_context.permissions


class TestUserWorkspaceRelationship:
    """Test user-workspace relationship functions"""

    @pytest.fixture
    def mock_supabase_client(self):
        client = AsyncMock()
        client.table = MagicMock()
        return client

    @pytest.mark.asyncio
    async def test_user_owns_workspace_true(self, mock_supabase_client):
        """Test user owns workspace - true case"""
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = AsyncMock(
            return_value={"data": {"id": "test-workspace-id"}}
        )

        result = await user_owns_workspace("test-user-id", "test-workspace-id")
        assert result is True

    @pytest.mark.asyncio
    async def test_user_owns_workspace_false(self, mock_supabase_client):
        """Test user owns workspace - false case"""
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = AsyncMock(
            return_value={"data": None}
        )

        result = await user_owns_workspace("test-user-id", "invalid-workspace-id")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_default_workspace_id(self, mock_supabase_client):
        """Test getting default workspace ID"""
        mock_supabase_client.table.return_value.select.return_value.limit.return_value.single.return_value.execute.return_value = AsyncMock(
            return_value={"data": {"id": "default-workspace-id"}}
        )

        result = await get_default_workspace_id("test-user-id")
        assert result == "default-workspace-id"

    @pytest.mark.asyncio
    async def test_get_default_workspace_id_none(self, mock_supabase_client):
        """Test getting default workspace ID when none exists"""
        mock_supabase_client.table.return_value.select.return_value.limit.return_value.single.return_value.execute.return_value = AsyncMock(
            return_value={"data": None}
        )

        result = await get_default_workspace_id("test-user-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_workspace_for_user(self, mock_supabase_client, mock_workspace):
        """Test getting workspace for user"""
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = AsyncMock(
            return_value={"data": mock_workspace.__dict__}
        )

        result = await get_workspace_for_user("test-workspace-id", "test-user-id")

        assert result.id == "test-workspace-id"
        assert result.user_id == "test-user-id"
        assert result.name == "Test Workspace"

    @pytest.mark.asyncio
    async def test_get_workspace_for_user_not_found(self, mock_supabase_client):
        """Test getting workspace for user when not found"""
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = AsyncMock(
            return_value={"data": None}
        )

        result = await get_workspace_for_user("invalid-workspace-id", "test-user-id")
        assert result is None


class TestUserModel:
    """Test User model validation"""

    def test_user_creation_valid(self):
        """Test creating valid user"""
        user = User(
            id="test-user-id",
            email="test@example.com",
            full_name="Test User",
            subscription_tier="free",
            budget_limit_monthly=1.0,
            preferences={"theme": "light"},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        assert user.id == "test-user-id"
        assert user.email == "test@example.com"
        assert user.subscription_tier == "free"
        assert user.preferences["theme"] == "light"

    def test_user_invalid_email(self):
        """Test creating user with invalid email"""
        with pytest.raises(Exception):  # ValidationError
            User(id="test-user-id", email="invalid-email", subscription_tier="free")

    def test_user_invalid_subscription_tier(self):
        """Test creating user with invalid subscription tier"""
        with pytest.raises(Exception):  # ValidationError
            User(
                id="test-user-id", email="test@example.com", subscription_tier="invalid"
            )

    def test_user_invalid_budget(self):
        """Test creating user with invalid budget"""
        with pytest.raises(Exception):  # ValidationError
            User(
                id="test-user-id",
                email="test@example.com",
                subscription_tier="free",
                budget_limit_monthly=-1.0,
            )

    def test_user_preferences_validation(self):
        """Test user preferences validation"""
        # Valid preferences
        user = User(
            id="test-user-id",
            email="test@example.com",
            preferences={"theme": "dark", "language": "en"},
        )
        assert user.preferences["theme"] == "dark"

        # Invalid theme
        with pytest.raises(Exception):  # ValidationError
            User(
                id="test-user-id",
                email="test@example.com",
                preferences={"theme": "invalid"},
            )

        # Invalid language
        with pytest.raises(Exception):  # ValidationError
            User(
                id="test-user-id",
                email="test@example.com",
                preferences={"language": "invalid"},
            )


class TestWorkspaceModel:
    """Test Workspace model validation"""

    def test_workspace_creation_valid(self):
        """Test creating valid workspace"""
        workspace = Workspace(
            id="test-workspace-id",
            user_id="test-user-id",
            name="Test Workspace",
            slug="test-workspace",
            settings={"timezone": "UTC", "currency": "USD"},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        assert workspace.id == "test-workspace-id"
        assert workspace.user_id == "test-user-id"
        assert workspace.name == "Test Workspace"
        assert workspace.slug == "test-workspace"

    def test_workspace_invalid_name(self):
        """Test creating workspace with invalid name"""
        with pytest.raises(Exception):  # ValidationError
            Workspace(
                id="test-workspace-id",
                user_id="test-user-id",
                name="",  # Empty name
                slug="test-workspace",
            )

    def test_workspace_invalid_slug(self):
        """Test creating workspace with invalid slug"""
        with pytest.raises(Exception):  # ValidationError
            Workspace(
                id="test-workspace-id",
                user_id="test-user-id",
                name="Test Workspace",
                slug="Invalid Slug!",  # Contains invalid characters
            )

    def test_workspace_settings_validation(self):
        """Test workspace settings validation"""
        # Valid settings
        workspace = Workspace(
            id="test-workspace-id",
            user_id="test-user-id",
            name="Test Workspace",
            settings={"timezone": "UTC", "currency": "USD", "language": "en"},
        )
        assert workspace.settings["timezone"] == "UTC"

        # Invalid timezone
        with pytest.raises(Exception):  # ValidationError
            Workspace(
                id="test-workspace-id",
                user_id="test-user-id",
                name="Test Workspace",
                settings={"timezone": "Invalid"},
            )

        # Invalid currency
        with pytest.raises(Exception):  # ValidationError
            Workspace(
                id="test-workspace-id",
                user_id="test-user-id",
                name="Test Workspace",
                settings={"currency": "Invalid"},
            )


class TestAuthContext:
    """Test AuthContext model"""

    def test_auth_context_creation(self, mock_user, mock_workspace):
        """Test creating auth context"""
        auth_context = AuthContext(
            user=mock_user, workspace_id=mock_workspace.id, workspace=mock_workspace
        )

        assert auth_context.user == mock_user
        assert auth_context.workspace_id == mock_workspace.id
        assert auth_context.workspace == mock_workspace
        assert "read" in auth_context.permissions
        assert "write" in auth_context.permissions

    def test_auth_context_workspace_ownership_validation(self, mock_user):
        """Test auth context workspace ownership validation"""
        # Create workspace with different user
        other_workspace = Workspace(
            id="other-workspace-id", user_id="other-user-id", name="Other Workspace"
        )

        # This should raise ValidationError
        with pytest.raises(Exception):  # ValidationError
            AuthContext(
                user=mock_user,
                workspace_id=other_workspace.id,
                workspace=other_workspace,
            )

    def test_auth_context_permissions(self, mock_user, mock_workspace):
        """Test auth context permissions"""
        # Free tier user
        free_user = User(
            id="free-user-id", email="free@example.com", subscription_tier="free"
        )

        auth_context = AuthContext(
            user=free_user, workspace_id=mock_workspace.id, workspace=mock_workspace
        )

        assert auth_context.has_permission("read") is True
        assert auth_context.has_permission("write") is True
        assert auth_context.has_permission("delete") is True
        assert auth_context.has_permission("admin") is False

        # Enterprise tier user
        enterprise_user = User(
            id="enterprise-user-id",
            email="enterprise@example.com",
            subscription_tier="enterprise",
        )

        auth_context = AuthContext(
            user=enterprise_user,
            workspace_id=mock_workspace.id,
            workspace=mock_workspace,
        )

        assert auth_context.has_permission("admin") is True


class TestAuthenticationIntegration:
    """Integration tests for authentication"""

    @pytest.mark.asyncio
    async def test_full_authentication_flow(
        self,
        mock_request,
        mock_supabase_client,
        mock_jwt_validator,
        mock_user,
        mock_workspace,
    ):
        """Test full authentication flow"""
        # Setup mocks
        mock_request.headers = {"x-workspace-id": "test-workspace-id"}
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = AsyncMock(
            return_value={"data": mock_user.__dict__}
        )

        with patch("...core.auth.get_jwt_validator", return_value=mock_jwt_validator):
            with patch(
                "...core.auth.get_supabase_client", return_value=mock_supabase_client
            ):
                with patch(
                    "...core.auth.get_workspace_for_user", return_value=mock_workspace
                ):
                    # Step 1: Authenticate user
                    user = await get_current_user(mock_request, "Bearer valid.token")
                    assert user.id == "test-user-id"

                    # Step 2: Get workspace ID
                    workspace_id = await get_workspace_id(
                        mock_request, user, "test-workspace-id"
                    )
                    assert workspace_id == "test-workspace-id"

                    # Step 3: Get auth context
                    auth_context = await get_auth_context(
                        mock_request, user, workspace_id
                    )
                    assert auth_context.user.id == "test-user-id"
                    assert auth_context.workspace_id == "test-workspace-id"

    @pytest.mark.asyncio
    async def test_authentication_with_different_subscription_tiers(
        self, mock_request, mock_supabase_client, mock_jwt_validator
    ):
        """Test authentication with different subscription tiers"""
        tiers = ["free", "starter", "pro", "growth", "enterprise"]

        for tier in tiers:
            # Setup user with specific tier
            user_data = {
                "id": f"user-{tier}",
                "email": f"{tier}@example.com",
                "subscription_tier": tier,
                "budget_limit_monthly": 1.0 if tier == "free" else 10.0,
            }

            mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = AsyncMock(
                return_value={"data": user_data}
            )

            with patch(
                "...core.auth.get_jwt_validator", return_value=mock_jwt_validator
            ):
                with patch(
                    "...core.auth.get_supabase_client",
                    return_value=mock_supabase_client,
                ):
                    user = await get_current_user(mock_request, "Bearer valid.token")
                    assert user.subscription_tier == tier
