from unittest.mock import patch

import pytest
from pydantic import ValidationError

from backend.core.config import Config


def test_config_production_requirements_failure():
    """
    FAILING TEST:
    Verify that production config fails if Upstash Redis is missing
    (Wait, currently Config has them as Optional[str] = None in config.py)
    We want them to be REQUIRED for production.
    """
    env = {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "test-key",
        "LLM_PROVIDER": "google",
        "UPSTASH_REDIS_REST_URL": "",  # Explicitly empty to override .env
        "UPSTASH_REDIS_REST_TOKEN": "",
    }
    with patch.dict("os.environ", env, clear=True):
        cfg = Config()
        # This will currently PASS because they are optional.
        # We will update config.py in next task to make them required based on env.
        with pytest.raises(
            ValueError,
            match=r"Production requires Upstash Redis \(UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN\)",
        ):
            cfg.validate_infra()


def test_config_vertex_ai_success():
    """Verify Vertex AI configuration validation."""
    env = {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "test-key",
        "LLM_PROVIDER": "google",
        "LLM_MODEL": "gemini-2.5-flash",
        "UPSTASH_REDIS_REST_URL": "https://test.upstash.io",
        "UPSTASH_REDIS_REST_TOKEN": "test-token",
    }
    with patch.dict("os.environ", env, clear=True):
        cfg = Config()
        assert cfg.LLM_PROVIDER == "google"
        assert cfg.validate_infra() is True
