import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def mock_env_vars():
    """Mock required environment variables for tests."""
    os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-characters-long!!"
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/postgres"
    os.environ["UPSTASH_REDIS_URL"] = "https://test.upstash.io"
    os.environ["UPSTASH_REDIS_TOKEN"] = "test-token"
    os.environ["GCP_PROJECT_ID"] = "raptorflow-test"
    os.environ["WEBHOOK_SECRET"] = "test-webhook-secret"
    os.environ["VERTEX_AI_PROJECT_ID"] = "raptorflow-test"
    
    yield
    
    # Optional: cleanup
    # os.environ.pop("SECRET_KEY", None)
