import pytest
from unittest.mock import patch, MagicMock
from backend.core.cache import get_cache_client

def test_cache_client_initialization():
    with patch("backend.core.cache.Redis") as mock_redis:
        client = get_cache_client()
        assert client is not None
        mock_redis.from_env.assert_called_once()
