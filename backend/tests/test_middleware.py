import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from core.middleware import TraceIDMiddleware, get_current_trace_id


def test_trace_id_middleware_propagation():
    app = FastAPI()
    app.add_middleware(TraceIDMiddleware)

    @app.get("/test")
    def test_route():
        trace_id = get_current_trace_id()
        return {"trace_id": trace_id}

    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 200
    assert "X-Trace-ID" in response.headers
    assert response.json()["trace_id"] == response.headers["X-Trace-ID"]
