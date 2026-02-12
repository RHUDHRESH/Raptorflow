from __future__ import annotations

from typing import Any, Dict

import pytest

from backend.api.v1 import search as search_api


@pytest.mark.asyncio
async def test_search_endpoint_uses_intensity_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: Dict[str, Any] = {}

    async def fake_search(query: str, engines: list[str], max_results: int, enable_cache: bool):
        assert query == "vertex ai benchmarks"
        assert enable_cache is True
        return {
            "query": query,
            "results": [
                {
                    "title": "Result 1",
                    "url": "https://example.com/1",
                    "snippet": "Snippet",
                    "source": "duckduckgo",
                    "timestamp": "2026-02-12T00:00:00Z",
                    "relevance_score": 0.9,
                }
            ],
            "total_results": 1,
            "engines_used": engines,
            "engine_stats": {},
            "response_time": 0.2,
            "timestamp": "2026-02-12T00:00:00Z",
        }

    async def fake_run(*, operation: str, payload: Dict[str, Any], executor):
        captured.update(payload)
        result = await executor()
        result["module"] = operation
        result["orchestrator"] = "langgraph"
        return result

    async def fake_summary(**_kwargs):
        return {"status": "success", "text": "Summary output"}

    monkeypatch.setattr(search_api.search_engine, "search", fake_search)
    monkeypatch.setattr(search_api.langgraph_optional_orchestrator, "run", fake_run)
    monkeypatch.setattr(search_api, "_summarize_search_results", fake_summary)

    result = await search_api.search_endpoint(
        q="vertex ai benchmarks",
        engines=None,
        max_results=None,
        intensity="high",
        execution_mode="swarm",
        summarize=True,
        enable_cache=True,
    )

    assert captured["intensity"] == "high"
    assert captured["execution_mode"] == "swarm"
    assert captured["engines"] == ["duckduckgo", "brave", "searx"]
    assert captured["max_results"] == 40
    assert result["search_profile"]["execution_mode"] == "swarm"
    assert result["summary"]["status"] == "success"


@pytest.mark.asyncio
async def test_search_endpoint_without_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_search(query: str, engines: list[str], max_results: int, enable_cache: bool):
        return {
            "query": query,
            "results": [],
            "total_results": 0,
            "engines_used": engines,
            "engine_stats": {},
            "response_time": 0.1,
            "timestamp": "2026-02-12T00:00:00Z",
        }

    async def fake_run(*, operation: str, payload: Dict[str, Any], executor):
        result = await executor()
        result["module"] = operation
        result["orchestrator"] = "langgraph"
        return result

    monkeypatch.setattr(search_api.search_engine, "search", fake_search)
    monkeypatch.setattr(search_api.langgraph_optional_orchestrator, "run", fake_run)

    result = await search_api.search_endpoint(
        q="test",
        engines="duckduckgo",
        max_results=5,
        intensity="low",
        execution_mode="single",
        summarize=False,
        enable_cache=False,
    )

    assert "summary" not in result
    assert result["search_profile"]["intensity"] == "low"
