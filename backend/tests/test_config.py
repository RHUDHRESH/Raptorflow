from unittest.mock import patch

import pytest
from pydantic import ValidationError

from backend.core.config import Config


def test_config_initialization():
    """Test that Config initializes with default placeholders."""
    with patch.dict("os.environ", {}, clear=True):
        cfg = Config()
        assert cfg.SUPABASE_URL == "https://placeholder.supabase.co"
        assert cfg.GCP_PROJECT_ID == "raptorflow-481505"


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
