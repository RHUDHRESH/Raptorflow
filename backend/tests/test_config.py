import pytest
from pydantic import ValidationError
from unittest.mock import patch
from backend.core.config import Config


def test_config_missing_required():
    """Test that Config fails when required fields are missing."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValidationError):
            Config()


def test_config_success():
    """Test that Config initializes correctly with required fields."""
    env = {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "test-key",
    }
    with patch.dict("os.environ", env, clear=True):
        cfg = Config()
        assert cfg.SUPABASE_URL == "https://test.supabase.co"
        assert cfg.GCP_PROJECT_ID == "raptorflow-481505"


def test_config_infra_validation_failure():
    """Test custom infra validation for OpenAI provider."""
    env = {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "test-key",
        "LLM_PROVIDER": "openai",
    }
    with patch.dict("os.environ", env, clear=True):
        cfg = Config()
        with pytest.raises(ValueError, match="OPENAI_API_KEY must be set"):
            cfg.validate_infra()


def test_config_infra_validation_success():
    """Test custom infra validation success."""
    env = {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "test-key",
        "LLM_PROVIDER": "openai",
        "OPENAI_API_KEY": "sk-test",
    }
    with patch.dict("os.environ", env, clear=True):
        cfg = Config()
        assert cfg.validate_infra() is True
