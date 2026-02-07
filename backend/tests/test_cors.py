from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_cors_headers_present():
    """Verify that CORS headers are present in the response."""
    response = client.options(
        "/health",
        headers={
            "Origin": "https://raptorflow.vercel.app",
            "Access-Control-Request-Method": "GET",
        },
    )
    # If CORS is not enabled, this might return 405 or 400 depending on FastAPI settings
    # or just lack the headers.
    assert (
        response.headers.get("access-control-allow-origin")
        == "https://raptorflow.vercel.app"
    )
    assert "GET" in response.headers.get("access-control-allow-methods", "")
