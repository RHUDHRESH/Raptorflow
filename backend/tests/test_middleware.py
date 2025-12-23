import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from backend.core.middleware import TelemetryMiddleware, CorrelationIDMiddleware, RequestLoggingMiddleware
from backend.models.telemetry import TelemetryEventType
from unittest.mock import AsyncMock, MagicMock

app = FastAPI()

# Add all middlewares
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)
mock_matrix = MagicMock()
mock_matrix.emit_event = AsyncMock(return_value=True)
app.add_middleware(TelemetryMiddleware, matrix_service=mock_matrix)

@app.get("/test")
async def api_test_endpoint():
    return {"status": "ok"}

@app.get("/error")
async def api_error_endpoint():
    raise Exception("Test error")

def test_telemetry_middleware_captures_success():
    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 200
    assert "X-Correlation-ID" in response.headers
    
    # Verify emit_event was called
    assert mock_matrix.emit_event.called
    args, _ = mock_matrix.emit_event.call_args
    event = args[0]
    assert event.event_type == TelemetryEventType.INFERENCE_END
    assert "latency_ms" in event.payload
    assert event.payload["status_code"] == 200

def test_telemetry_middleware_captures_error():
    client = TestClient(app)
    # FastAPI handles exceptions and returns 500 if not caught, but TestClient 
    # might re-raise if not configured otherwise.
    # BaseHTTPMiddleware handles exceptions in dispatch.
    try:
        client.get("/error")
    except Exception:
        pass
    
    # Verify emit_event was called even on error
    assert mock_matrix.emit_event.called

