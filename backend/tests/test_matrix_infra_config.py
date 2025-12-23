from unittest.mock import MagicMock, patch

import pytest

from backend.core.config import get_settings
from backend.core.secrets import get_secret


def test_get_secret_with_gcp_manager(monkeypatch):
    """Verify get_secret correctly calls GCP Secret Manager."""
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")

    # Mock SecretManagerServiceClient
    with patch(
        "google.cloud.secretmanager.SecretManagerServiceClient"
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "secret-value"
        mock_client.access_secret_version.return_value = mock_response

        val = get_secret("MY_SECRET")

        assert val == "secret-value"
        mock_client.access_secret_version.assert_called_once()
        # Verify the path
        call_args = mock_client.access_secret_version.call_args
        assert "projects/test-project/secrets/MY_SECRET/versions/latest" in str(
            call_args
        )


def test_config_retrieves_from_secret_manager():
    """
    RED PHASE: Verify that get_settings() uses get_secret
    (which we'll mock) to fetch sensitive keys.
    """
    with patch("backend.core.config.get_secret") as mock_get_secret:
        # Define what the mock returns for specific keys
        secrets_map = {
            "SUPABASE_URL": "https://secret.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "secret-role-key",
            "DATABASE_URL": "postgresql://user:pass@host:5432/db",
            "UPSTASH_REDIS_REST_URL": "https://secret-upstash.com",
            "UPSTASH_REDIS_REST_TOKEN": "secret-upstash-token",
        }
        mock_get_secret.side_effect = lambda name: secrets_map.get(name)

        settings = get_settings()

        assert settings.SUPABASE_URL == "https://secret.supabase.co"
        assert settings.DATABASE_URL == "postgresql://user:pass@host:5432/db"
        assert settings.UPSTASH_REDIS_REST_URL == "https://secret-upstash.com"
        assert settings.UPSTASH_REDIS_REST_TOKEN == "secret-upstash-token"


def test_module_imports_use_settings():
    """Verify that importing modules that use settings doesn't crash and uses the values."""
    with patch("backend.core.config.get_secret") as mock_get_secret:
        mock_get_secret.return_value = "mocked-secret"

        # We need to reload or carefully import since these might have been imported already
        import importlib

        import backend.db
        import backend.inference
        import backend.tools.image_gen

        importlib.reload(backend.db)
        importlib.reload(backend.inference)
        importlib.reload(backend.tools.image_gen)

        assert backend.db.DB_URI == "mocked-secret"

        # Test get_vertex_api_key in inference
        from backend.inference import get_vertex_api_key

        with patch("backend.inference.get_settings") as mock_get_settings:
            mock_get_settings.return_value.VERTEX_AI_API_KEY = "vertex-key"
            val = get_vertex_api_key()
            assert val == "vertex-key"
            mock_get_settings.assert_called()
