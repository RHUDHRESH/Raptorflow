from backend.core.config import get_settings

def test_gcp_project_id_is_set():
    settings = get_settings()
    assert settings.GCP_PROJECT_ID == "raptorflow-481505"
    assert settings.GCP_REGION == "europe-west1"


def test_gcs_buckets_defined():
    settings = get_settings()
    assert settings.GCS_INGEST_BUCKET.startswith("raptorflow-")
    assert settings.GCS_GOLD_BUCKET.startswith("raptorflow-")
