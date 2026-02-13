from __future__ import annotations

import json
from typing import Any, Dict

import pytest
from fastapi import BackgroundTasks

from backend.api.v1 import scraper as scraper_api


@pytest.mark.asyncio
async def test_scraper_endpoint_applies_low_profile_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_payload: Dict[str, Any] = {}

    async def fake_scrape(
        url: str,
        user_id: str,
        strategy,
        legal_basis: str,
        **_: Any,
    ):
        return {
            "url": url,
            "user_id": user_id,
            "status": "success",
            "strategy": strategy.value,
            "processing_time": 0.12,
            "timestamp": "2026-02-12T00:00:00Z",
        }

    async def fake_run(*, operation: str, payload: Dict[str, Any], executor):
        captured_payload.update(payload)
        result = await executor()
        result["module"] = operation
        result["orchestrator"] = "langgraph"
        return result

    monkeypatch.setattr(scraper_api.unified_scraper, "scrape", fake_scrape)
    monkeypatch.setattr(scraper_api.langgraph_optional_orchestrator, "run", fake_run)

    response = await scraper_api.scrape_endpoint(
        {
            "url": "https://example.com",
            "user_id": "11111111-1111-1111-1111-111111111111",
            "intensity": "low",
            "execution_mode": "single",
        },
        BackgroundTasks(),
    )
    body = json.loads(response.body.decode())

    assert captured_payload["intensity"] == "low"
    assert captured_payload["execution_mode"] == "single"
    assert captured_payload["strategy"] == "conservative"
    assert body["status"] == "success"
    assert body["strategy"] == "conservative"
    assert body["intensity"] == "low"
    assert body["execution_mode"] == "single"
