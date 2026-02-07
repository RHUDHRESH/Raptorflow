import sys
from unittest.mock import MagicMock, patch

# Prevent crashes from real imports
sys.modules["langchain_google_vertexai"] = MagicMock()

from core.config import Config  # noqa: E402
from inference import get_vertex_api_key  # noqa: E402


def test_get_vertex_api_key_primary():
    """Verify primary key is returned when set."""
    with patch("backend.core.config.get_secret", return_value=None):
        test_config = Config()
        test_config.VERTEX_AI_API_KEY = "primary-key"
        test_config.VERTEX_AI_API_KEY_FALLBACK = "fallback-key"

        with patch("backend.inference.get_settings", return_value=test_config):
            assert get_vertex_api_key() == "primary-key"


def test_get_vertex_api_key_fallback():
    """Verify fallback key is used if primary is missing."""
    with patch("backend.core.config.get_secret", return_value=None):
        test_config = Config()
        test_config.VERTEX_AI_API_KEY = None
        test_config.VERTEX_AI_API_KEY_FALLBACK = "fallback-key"

        with patch("backend.inference.get_settings", return_value=test_config):
            assert get_vertex_api_key() == "fallback-key"
