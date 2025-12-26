from unittest.mock import MagicMock, patch

import pytest

from core.vault import Vault


def test_vault_get_secret_fallback_to_env():
    """Test that vault falls back to env vars if Secret Manager fails."""
    with patch(
        "google.cloud.secretmanager.SecretManagerServiceClient"
    ) as mock_client, patch("os.getenv") as mock_getenv:

        # Mock Secret Manager failure
        mock_client.return_value.access_secret_version.side_effect = Exception(
            "Not found"
        )

        # Mock env var
        mock_getenv.return_value = "env-secret-value"

        vault = Vault()
        secret = vault.get_secret("TEST_SECRET")

        assert secret == "env-secret-value"
        mock_getenv.assert_called_with("TEST_SECRET")


def test_vault_get_secret_success():
    """Test that vault successfully retrieves secret from Secret Manager."""
    with patch("google.cloud.secretmanager.SecretManagerServiceClient") as mock_client:
        mock_inst = mock_client.return_value
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "gcp-secret-value"
        mock_inst.access_secret_version.return_value = mock_response

        vault = Vault()
        # Clear cache for test
        from core.vault import get_vault

        secret = vault.get_secret("REAL_SECRET")

        assert secret == "gcp-secret-value"
