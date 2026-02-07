from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.secrets import get_secret


def test_get_secret_env_fallback():
    """Verify that secret manager falls back to environment variables."""
    with patch(
        "backend.core.secrets.secretmanager.SecretManagerServiceClient"
    ) as mock_client:
        # Mock client failure or missing secret
        mock_instance = mock_client.return_value
        mock_instance.access_secret_version.side_effect = Exception("Not Found")

        with patch("backend.core.secrets.os.getenv", return_value="env_value"):
            val = get_secret("DB_URL")
            assert val == "env_value"


def test_get_secret_gcp_success():
    """Verify that secret manager fetches from GCP correctly."""
    with patch(
        "backend.core.secrets.secretmanager.SecretManagerServiceClient"
    ) as mock_client:
        mock_instance = mock_client.return_value
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "gcp_secret_val"
        mock_instance.access_secret_version.return_value = mock_response

        val = get_secret("UPSTASH_TOKEN")
        assert val == "gcp_secret_val"
