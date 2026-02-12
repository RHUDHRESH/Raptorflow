from __future__ import annotations

import importlib

import pytest


@pytest.mark.asyncio
async def test_muse_service_delegates_to_langgraph(monkeypatch: pytest.MonkeyPatch) -> None:
    muse_service_module = importlib.import_module("backend.services.muse_service")

    captured = {}

    async def fake_invoke(**kwargs):
        captured.update(kwargs)
        return {"success": True, "content": "ok", "metadata": {"orchestrator": "langgraph"}}

    monkeypatch.setattr(muse_service_module.langgraph_muse_orchestrator, "invoke", fake_invoke)

    result = await muse_service_module.muse_service.generate(
        workspace_id="11111111-1111-1111-1111-111111111111",
        task="Test task",
        content_type="general",
        tone="professional",
        target_audience="general",
        context={"foo": "bar"},
        max_tokens=700,
        temperature=0.6,
        reasoning_depth="low",
    )

    assert result["success"] is True
    assert result["metadata"]["orchestrator"] == "langgraph"
    assert captured["workspace_id"] == "11111111-1111-1111-1111-111111111111"
    assert captured["reasoning_depth"] == "low"
