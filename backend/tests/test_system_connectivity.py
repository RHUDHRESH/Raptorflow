import sys
from unittest.mock import AsyncMock, MagicMock, patch

# CRITICAL: Prevent numpy/pandas crashes in Python 3.14 environment
sys.modules["numpy"] = MagicMock()
sys.modules["pandas"] = MagicMock()
sys.modules["langchain_google_vertexai"] = MagicMock()
sys.modules["google.cloud"] = MagicMock()
sys.modules["google.cloud.storage"] = MagicMock()
sys.modules["google.cloud.bigquery"] = MagicMock()
sys.modules["google.cloud.secretmanager"] = MagicMock()

from uuid import uuid4  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

# Import app AFTER mocking
from main import app  # noqa: E402

client = TestClient(app)


def test_foundation_state_sync_scaffolding():
    """Verify state sync endpoint routing by mocking the service return."""
    tenant_id = str(uuid4())
    mock_data = {"positioning": "SOTA", "icps": []}

    # We mock the entire FoundationService dependency to ensure test stability
    # across environment changes.
    with patch("backend.api.v1.foundation.FoundationService") as mock_service_class:
        mock_instance = mock_service_class.return_value
        mock_instance.save_state = AsyncMock(
            return_value=MagicMock(tenant_id=tenant_id, data=mock_data)
        )
        mock_instance.get_state = AsyncMock(
            return_value=MagicMock(tenant_id=tenant_id, data=mock_data)
        )

        # Save
        response = client.post(
            "/v1/foundation/state", json={"tenant_id": tenant_id, "data": mock_data}
        )
        assert response.status_code == 200

        # Retrieve
        response = client.get(f"/v1/foundation/state/{tenant_id}")
        assert response.status_code == 200
        assert response.json()["data"] == mock_data


def test_cache_manager_logic():
    """Verify CacheManager scaffolding."""
    from core.cache import CacheManager

    mock_redis = MagicMock()
    mock_redis.get.return_value = '{"status": "success"}'

    manager = CacheManager(client=mock_redis)

    key = "test_json_key"
    val = {"status": "success"}
    manager.set_json(key, val)
    assert manager.get_json(key) == val
    mock_redis.set.assert_called_once()
