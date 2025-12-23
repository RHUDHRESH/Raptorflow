import pytest
from unittest.mock import MagicMock, patch
from backend.services.storage_service import GCSLifecycleManager

@pytest.fixture
def lifecycle_manager():
    return GCSLifecycleManager(source_bucket="raw-logs", target_bucket="gold-zone")

def test_archive_logs_logic(lifecycle_manager):
    """Test the logic of archiving logs between buckets."""
    with patch("google.cloud.storage.Client") as mock_client:
        mock_source = MagicMock()
        mock_target = MagicMock()
        mock_client.return_value.get_bucket.side_effect = [mock_source, mock_target]
        
        # Mock blobs
        mock_blob = MagicMock()
        mock_blob.name = "log_1.json"
        mock_source.list_blobs.return_value = [mock_blob]
        
        success = lifecycle_manager.archive_logs(prefix="logs/")
        
        assert success is True
        assert mock_source.copy_blob.called
        assert mock_source.delete_blob.called
