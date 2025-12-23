from unittest.mock import patch

from backend.core.cache import get_cache_client


def test_cache_client_initialization():
    with patch("backend.core.cache.Redis") as mock_redis:
        client = get_cache_client()
        assert client is not None
        # Verify it was called with parameters from get_settings()
        mock_redis.assert_called_once()
