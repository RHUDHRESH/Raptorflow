from __future__ import annotations

import pytest

from backend.ai.hub.contracts import SafetyDecision, TaskRequestV1, ToolPolicy
from backend.ai.hub.runtime import AIHubRuntime
from backend.services.exceptions import ValidationError


@pytest.mark.asyncio
async def test_ai_hub_runtime_runs_with_tool_and_trace() -> None:
    async def fake_generate(request: TaskRequestV1, prompt: str):
        assert request.workspace_id == "ws-test"
        assert "intent" in prompt.lower()
        return {
            "status": "success",
            "text": "Generated strategic response with context evidence.",
            "input_tokens": 50,
            "output_tokens": 90,
            "total_tokens": 140,
            "cost_usd": 0.001,
            "generation_time_seconds": 0.1,
            "model": "fake-model",
            "backend": "fake-backend",
            "fallback_reason": "",
        }

    runtime = AIHubRuntime(model_generator=fake_generate)
    request = TaskRequestV1(
        workspace_id="ws-test",
        intent="Create campaign launch plan",
        inputs={"text": "launch soon"},
        requested_tools=["echo_context"],
        tool_policy=ToolPolicy(allowed_tools={"echo_context"}),
    )

    result = await runtime.run_task(request)

    assert result.status.value in {"success", "partial"}
    assert result.output
    assert result.trace_id
    assert result.safety_decision in {SafetyDecision.ALLOW, SafetyDecision.REVIEW}

    trace = runtime.get_trace(result.trace_id)
    assert trace is not None
    assert trace["state_transitions"][0] == "INTAKE"
    assert any(call.get("tool") == "echo_context" for call in trace["tool_calls"])

    context = runtime.get_context(result.trace_id)
    assert context is not None
    layers = {node["layer"] for node in context["nodes"]}
    assert "policy" in layers
    assert "task" in layers


@pytest.mark.asyncio
async def test_ai_hub_runtime_rejects_disallowed_tool() -> None:
    async def fake_generate(request: TaskRequestV1, prompt: str):
        return {
            "status": "success",
            "text": "unused",
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "generation_time_seconds": 0.0,
            "model": "fake-model",
            "backend": "fake-backend",
            "fallback_reason": "",
        }

    runtime = AIHubRuntime(model_generator=fake_generate)
    request = TaskRequestV1(
        workspace_id="ws-test",
        intent="Hash this",
        inputs={"text": "hello"},
        requested_tools=["stable_hash"],
        tool_policy=ToolPolicy(allowed_tools={"echo_context"}),
    )
    with pytest.raises(ValidationError):
        await runtime.run_task(request)


@pytest.mark.asyncio
async def test_ai_hub_runtime_feedback_promotes_memory() -> None:
    async def fake_generate(request: TaskRequestV1, prompt: str):
        return {
            "status": "success",
            "text": "Quality response",
            "input_tokens": 20,
            "output_tokens": 40,
            "total_tokens": 60,
            "cost_usd": 0.0,
            "generation_time_seconds": 0.02,
            "model": "fake-model",
            "backend": "fake-backend",
            "fallback_reason": "",
        }

    runtime = AIHubRuntime(model_generator=fake_generate)
    request = TaskRequestV1(workspace_id="ws-test", intent="Draft copy")
    result = await runtime.run_task(request)
    feedback = await runtime.submit_feedback(
        workspace_id="ws-test",
        run_id=result.trace_id,
        score=5,
        comment="Excellent",
    )
    assert feedback["status"] == "promoted"


@pytest.mark.asyncio
async def test_ai_hub_runtime_denies_tools_when_allowlist_is_empty() -> None:
    async def fake_generate(request: TaskRequestV1, prompt: str):
        return {
            "status": "success",
            "text": "unused",
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "generation_time_seconds": 0.0,
            "model": "fake-model",
            "backend": "fake-backend",
            "fallback_reason": "",
        }

    runtime = AIHubRuntime(model_generator=fake_generate)
    request = TaskRequestV1(
        workspace_id="ws-test",
        intent="Inspect workspace context",
        requested_tools=["echo_context"],
        tool_policy=ToolPolicy(),
    )
    with pytest.raises(ValidationError):
        await runtime.run_task(request)


@pytest.mark.asyncio
async def test_ai_hub_runtime_replays_idempotent_requests() -> None:
    calls = {"count": 0}

    async def fake_generate(request: TaskRequestV1, prompt: str):
        calls["count"] += 1
        return {
            "status": "success",
            "text": "Idempotent output",
            "input_tokens": 1,
            "output_tokens": 1,
            "total_tokens": 2,
            "cost_usd": 0.0,
            "generation_time_seconds": 0.01,
            "model": "fake-model",
            "backend": "fake-backend",
            "fallback_reason": "",
        }

    runtime = AIHubRuntime(model_generator=fake_generate)
    request = TaskRequestV1(
        workspace_id="ws-test",
        intent="Generate mission statement",
        idempotency_key="same-request",
    )

    first = await runtime.run_task(request)
    second = await runtime.run_task(request)

    assert calls["count"] == 1
    assert first.trace_id == second.trace_id
    assert second.metadata.get("idempotent_replay") is True


@pytest.mark.asyncio
async def test_ai_hub_runtime_rejects_idempotency_key_reuse_with_new_payload() -> None:
    async def fake_generate(request: TaskRequestV1, prompt: str):
        return {
            "status": "success",
            "text": "result",
            "input_tokens": 1,
            "output_tokens": 1,
            "total_tokens": 2,
            "cost_usd": 0.0,
            "generation_time_seconds": 0.01,
            "model": "fake-model",
            "backend": "fake-backend",
            "fallback_reason": "",
        }

    runtime = AIHubRuntime(model_generator=fake_generate)
    first = TaskRequestV1(
        workspace_id="ws-test",
        intent="Write launch positioning",
        idempotency_key="same-key",
    )
    second = TaskRequestV1(
        workspace_id="ws-test",
        intent="Write retention playbook",
        idempotency_key="same-key",
    )

    await runtime.run_task(first)
    with pytest.raises(ValidationError):
        await runtime.run_task(second)
