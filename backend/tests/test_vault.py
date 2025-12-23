import pytest
from unittest.mock import MagicMock, patch
from backend.core.vault import Vault


@pytest.mark.asyncio
async def test_vault_initialization_missing_env():
    """Test that Vault fails to initialize when env vars are missing."""
    with patch.dict("os.environ", {}, clear=True):
        vault = Vault()
        msg = "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set."
        with pytest.raises(ValueError, match=msg):
            await vault.initialize()


@pytest.mark.asyncio
async def test_vault_get_secret_success():
    """Test successful secret retrieval from GCP Secret Manager."""
    path = "backend.core.vault.secretmanager.SecretManagerServiceClient"
    with patch(path) as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "secret-value"
        mock_instance.access_secret_version.return_value = mock_response

        with patch.dict("os.environ", {"GCP_PROJECT_ID": "test-project"}):
            vault = Vault()
            secret = await vault.get_secret("test-secret")
            assert secret == "secret-value"
            mock_instance.access_secret_version.assert_called_once()


@pytest.mark.asyncio
async def test_vault_health_check_unhealthy():
    """Test health check when services are down."""
    with patch("backend.core.vault.Vault.get_session") as mock_session:
        mock_session.side_effect = Exception("Connection error")

        with patch("backend.core.vault.Vault._get_secret_client") as mock_get_sc:
            mock_secret_instance = MagicMock()
            mock_secret_instance.list_secrets.side_effect = Exception("Auth error")
            mock_get_sc.return_value = mock_secret_instance

            with patch.dict("os.environ", {"GCP_PROJECT_ID": "test-project"}):
                vault = Vault()
                status = await vault.health_check()
                assert "unhealthy" in status["supabase"]
                assert "unhealthy" in status["gcp_secrets"]
