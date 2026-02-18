from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from backend.ai.hub.contracts import TaskRequestV1
from backend.ai.hub.runtime import AIHubRuntime
from backend.api.v1.ai_hub.job_store import InMemoryJobStore
from backend.api.v1.ai_hub import routes as hub_routes


@pytest.fixture
def hub_client(monkeypatch: pytest.MonkeyPatch):
    async def fake_generate(request: TaskRequestV1, prompt: str):
        return {
            "status": "success",
            "text": "Hub response",
            "input_tokens": 10,
            "output_tokens": 20,
            "total_tokens": 30,
            "cost_usd": 0.0,
            "generation_time_seconds": 0.01,
            "model": "fake-model",
            "backend": "fake-backend",
            "fallback_reason": "",
        }

    runtime = AIHubRuntime(model_generator=fake_generate)
    monkeypatch.setattr(hub_routes, "runtime", runtime)
    monkeypatch.setattr(hub_routes, "job_store", InMemoryJobStore(max_entries=50))

    app = FastAPI()
    app.include_router(hub_routes.router, prefix="/api")
    return TestClient(app)


def test_hub_run_endpoint(hub_client: TestClient) -> None:
    response = hub_client.post(
        "/api/ai/hub/v1/tasks/run",
        json={
            "workspace_id": "ws-api",
            "intent": "Create a positioning summary",
            "inputs": {"topic": "positioning"},
            "allowed_tools": ["echo_context"],
            "requested_tools": ["echo_context"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"success", "partial"}
    assert body["trace_id"]
    assert body["run_id"] == body["trace_id"]
    assert body["workspace_id"] == "ws-api"
    assert isinstance(body["tool_trace_summary"], list)
    assert "bcm_writes" in body
    assert "usage" in body


def test_hub_async_endpoint_returns_job(hub_client: TestClient) -> None:
    response = hub_client.post(
        "/api/ai/hub/v1/tasks/run-async",
        json={
            "workspace_id": "ws-api",
            "intent": "Create a sequencing plan",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["job_id"]
    assert body["status"] in {"queued", "running", "succeeded"}

    job = hub_client.get(f"/api/ai/hub/v1/jobs/{body['job_id']}")
    assert job.status_code == 200
    assert job.json()["job_id"] == body["job_id"]


def test_hub_capabilities_endpoint(hub_client: TestClient) -> None:
    response = hub_client.get("/api/ai/hub/v1/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert body["runtime_version"] == "v1"
    assert "execution_modes" in body
    assert "tool_specs" in body
    assert "policy_profiles" in body


def test_hub_run_rejects_unknown_policy(hub_client: TestClient) -> None:
    response = hub_client.post(
        "/api/ai/hub/v1/tasks/run",
        json={
            "workspace_id": "ws-api",
            "intent": "Create a summary",
            "policy_profile": "unknown-profile",
        },
    )
    assert response.status_code == 400
