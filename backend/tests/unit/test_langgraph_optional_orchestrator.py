from __future__ import annotations

import pytest

from backend.agents.langgraph_optional_orchestrator import langgraph_optional_orchestrator
from backend.config import settings
from backend.services.exceptions import ServiceUnavailableError


@pytest.mark.asyncio
async def test_optional_orchestrator_blocks_disabled_search(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ENABLE_SEARCH_MODULE", False)

    async def _executor():
        return {"results": []}

    with pytest.raises(ServiceUnavailableError):
        await langgraph_optional_orchestrator.run(
            operation="search",
            payload={"q": "test"},
            executor=_executor,
        )


@pytest.mark.asyncio
async def test_optional_orchestrator_executes_enabled_module(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ENABLE_SEARCH_MODULE", True)
    monkeypatch.setattr(settings, "AI_EXECUTION_MODE", "swarm")
    monkeypatch.setattr(settings, "AI_DEFAULT_INTENSITY", "high")

    async def _executor():
        return {"results": [{"title": "ok"}]}

    result = await langgraph_optional_orchestrator.run(
        operation="search",
        payload={"q": "test"},
        executor=_executor,
    )

    assert result["module"] == "search"
    assert result["orchestrator"] == "langgraph"
    assert result["execution_mode"] == "swarm"
    assert result["intensity"] == "high"
    assert result["results"][0]["title"] == "ok"
