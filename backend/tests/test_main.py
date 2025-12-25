from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_check():
    """Test the system health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_correlation_id_middleware():
    """Test that correlation ID is propagated."""
    response = client.get("/health")
    assert "X-Correlation-ID" in response.headers


def test_exception_handler():
    """Test custom exception handling."""
    from backend.core.exceptions import RaptorFlowError

    @app.get("/trigger-error")
    async def trigger_error():
        raise RaptorFlowError("Custom Error", status_code=400)

    response = client.get("/trigger-error")
    assert response.status_code == 400
    assert response.json()["error"] == "Custom Error"
