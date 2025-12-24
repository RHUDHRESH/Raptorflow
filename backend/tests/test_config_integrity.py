from backend.core.config import get_settings


def test_config_load():
    """Verify that settings can be loaded without crashing and have required fields."""
    settings = get_settings()
    assert settings.GCS_INGEST_BUCKET is not None
    assert "placeholder" not in settings.SUPABASE_URL
    assert "placeholder" not in settings.SUPABASE_SERVICE_ROLE_KEY


def test_inference_config():
    """Verify inference configuration exists."""
    settings = get_settings()
    assert settings.INFERENCE_PROVIDER in ["google", "openai", "anthropic"]
    if settings.INFERENCE_PROVIDER == "google":
        assert settings.MODEL_REASONING is not None
