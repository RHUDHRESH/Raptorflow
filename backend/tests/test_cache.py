from unittest.mock import MagicMock, patch

from backend.core.cache import get_cache_client, get_cache_manager


def test_cache_client_initialization():
    with patch("backend.core.cache.Redis") as mock_redis:
        client = get_cache_client()
        assert client is not None
        mock_redis.assert_called_once()


def test_cache_manager_json_logic():
    """Verify CacheManager handles JSON serialization."""
    mock_redis = MagicMock()
    mock_redis.get.return_value = '{"foo": "bar"}'

    manager = get_cache_manager()
    manager.client = mock_redis

    # Test Set
    manager.set_json("test_key", {"foo": "bar"})
    mock_redis.set.assert_called_once()

    # Test Get
    result = manager.get_json("test_key")
    assert result == {"foo": "bar"}
    mock_redis.get.assert_called_with("test_key")
