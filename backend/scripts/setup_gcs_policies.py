import storage

from backend.core.config import get_settings


def setup_gcs_policies():
    """
    Configures CORS and Lifecycle policies for RaptorFlow GCS buckets.
    Ensures safe, production-grade storage management.
    """
    settings = get_settings()
    # Note: storage.Client() will use GOOGLE_APPLICATION_CREDENTIALS in prod
    # For local simulation, we assume gcloud auth application-default login
    try:
        client = storage.Client(project=settings.GCP_PROJECT_ID)
    except Exception as e:
        print(f"Warning: Could not initialize GCS client: {e}")
        return

    buckets_to_configure = [
        settings.GCS_INGEST_BUCKET,
        settings.GCS_GOLD_BUCKET,
        settings.GCS_MODEL_BUCKET,
        settings.GCS_LOG_BUCKET,
    ]

    # CORS Configuration
    # Allows frontend (Vercel/Local) to perform direct uploads/downloads
    cors_config = [
        {
            "origin": [
                "*"
            ],  # Recommendation: Replace with ['https://raptorflow.app', 'http://localhost:3000']
            "responseHeader": ["Content-Type", "x-goog-resumable", "Authorization"],
            "method": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "maxAgeSeconds": 3600,
        }
    ]

    # Lifecycle Configuration
    # Automatically delete temporary data or logs older than 30 days to save costs
    retention_rules = [{"action": {"type": "Delete"}, "condition": {"age": 30}}]

    for bucket_name in buckets_to_configure:
        try:
            bucket = client.get_bucket(bucket_name)

            # Apply CORS to all buckets for flexibility
            bucket.cors = cors_config

            # Apply Lifecycle rules specifically to transient data buckets
            if bucket_name in [settings.GCS_LOG_BUCKET, settings.GCS_INGEST_BUCKET]:
                bucket.lifecycle_rules = retention_rules
                print(f"Applying lifecycle rules to {bucket_name}")

            bucket.patch()
            print(f"Successfully configured GCS policies for: {bucket_name}")
        except Exception as e:
            print(
                f"Skipping bucket {bucket_name}: {e} (Ensure bucket exists and you have permissions)"
            )


if __name__ == "__main__":
    setup_gcs_policies()
