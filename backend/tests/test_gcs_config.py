import pytest
from google.cloud import storage

from core.config import get_settings


def test_gcs_gold_bucket_config():
    """Test that the gold bucket name is correctly configured in Settings."""
    settings = get_settings()
    assert settings.GCS_GOLD_BUCKET == "raptorflow-gold-zone-481505"


@pytest.mark.skip(reason="Requires GCP credentials and real bucket access")
def test_gcs_gold_bucket_exists():
    """Verify that the gold bucket actually exists in GCP."""
    client = storage.Client()
    bucket = client.get_bucket("raptorflow-gold-zone-481505")
    assert bucket.exists()
