from __future__ import annotations

import importlib

import pytest

from backend.agents.langgraph_muse_orchestrator import (
    langgraph_muse_orchestrator,
    resolve_generation_profile,
)


def test_resolve_generation_profile_caps_and_bounds() -> None:
    resolved = resolve_generation_profile(
        max_tokens=5000,
        temperature=0.95,
        reasoning_depth="low",
        intensity="low",
        execution_mode="single",
    )
    assert resolved["reasoning_depth"] == "low"
    assert resolved["intensity"] == "low"
    assert resolved["execution_mode"] == "single"
    assert resolved["effective_max_tokens"] == 500
    assert resolved["effective_temperature"] == 0.5


def test_resolve_generation_profile_defaults_unknown_depth() -> None:
    resolved = resolve_generation_profile(
        max_tokens=900,
        temperature=0.1,
        reasoning_depth="unknown",
        intensity="high",
        execution_mode="council",
    )
    assert resolved["reasoning_depth"] == "unknown"
    assert resolved["effective_max_tokens"] == 1125
    assert resolved["effective_temperature"] == 0.4
    assert resolved["execution_mode"] == "council"


@pytest.mark.asyncio
async def test_langgraph_orchestrator_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    services_pkg = importlib.import_module("backend.services")
    bcm_generation_logger_module = importlib.import_module("backend.services.bcm_generation_logger")
    bcm_memory_module = importlib.import_module("backend.services.bcm_memory")
    bcm_reflector_module = importlib.import_module("backend.services.bcm_reflector")
    prompt_compiler_module = importlib.import_module("backend.services.prompt_compiler")
    vertex_ai_module = importlib.import_module("backend.services.vertex_ai_service")
    config_module = importlib.import_module("backend.config")

    class FakeBCMService:
        @staticmethod
        def get_manifest_fast(workspace_id: str):
            assert workspace_id == "11111111-1111-1111-1111-111111111111"
            return {"version": 4, "foundation": {"company": "Acme"}}

    class FakeVertexService:
        @staticmethod
        async def generate_with_system(**kwargs):
            assert kwargs["workspace_id"] == "11111111-1111-1111-1111-111111111111"
            assert kwargs["max_tokens"] == 1000
            assert kwargs["temperature"] == 0.8
            return {
                "status": "success",
                "text": "Generated output",
                "total_tokens": 321,
                "cost_usd": 0.12,
                "model": "gemini-test",
                "model_type": "generative",
                "generation_time_seconds": 0.42,
            }

        @staticmethod
        async def generate_text(**kwargs):
            raise AssertionError("Structured prompt path should be used when manifest exists")

    monkeypatch.setattr(services_pkg, "bcm_service", FakeBCMService())
    monkeypatch.setattr(bcm_memory_module, "get_relevant_memories", lambda _ws, limit=0: [{"k": limit}])
    monkeypatch.setattr(
        prompt_compiler_module,
        "get_or_compile_system_prompt",
        lambda **_kwargs: "SYSTEM PROMPT",
    )
    monkeypatch.setattr(
        prompt_compiler_module,
        "build_user_prompt",
        lambda **_kwargs: "USER PROMPT",
    )
    monkeypatch.setattr(vertex_ai_module, "vertex_ai_service", FakeVertexService())
    monkeypatch.setattr(config_module.settings, "AI_EXECUTION_MODE", "single")
    monkeypatch.setattr(config_module.settings, "AI_DEFAULT_INTENSITY", "medium")
    monkeypatch.setattr(
        bcm_generation_logger_module,
        "log_generation",
        lambda **_kwargs: {"id": "gen-123"},
    )
    monkeypatch.setattr(bcm_reflector_module, "should_auto_reflect", lambda _workspace_id: False)

    result = await langgraph_muse_orchestrator.invoke(
        workspace_id="11111111-1111-1111-1111-111111111111",
        task="Write launch copy",
        content_type="email",
        tone="direct",
        target_audience="founders",
        context={"stage": "seed"},
        max_tokens=1800,
        temperature=0.95,
        reasoning_depth="medium",
        intensity="medium",
        execution_mode="single",
    )

    assert result["success"] is True
    assert result["content"] == "Generated output"
    assert result["tokens_used"] == 321
    assert result["metadata"]["generation_id"] == "gen-123"
    assert result["metadata"]["orchestrator"] == "langgraph"
    assert result["metadata"]["execution_mode"] == "single"
