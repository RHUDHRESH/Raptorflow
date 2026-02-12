from __future__ import annotations

from typing import Any, Dict
import importlib

import pytest

from backend.api.v1 import scraper as scraper_api
from backend.api.v1 import search as search_api


class _FakeRedis:
    def __init__(self) -> None:
        self.store: Dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self.store.get(key)

    def set(self, key: str, value: str, ex: int | None = None) -> None:
        _ = ex
        self.store[key] = value


@pytest.mark.asyncio
async def test_search_results_use_upstash_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    redis = _FakeRedis()
    monkeypatch.setattr(search_api, "get_redis_client", lambda: redis)

    calls = {"count": 0}

    async def fake_duckduckgo(query: str, max_results: int) -> Dict[str, Any]:
        calls["count"] += 1
        return {
            "results": [
                {
                    "title": f"{query}:{max_results}",
                    "url": "https://example.com/a",
                    "snippet": "cached result",
                    "source": "duckduckgo",
                    "timestamp": "2026-02-12T00:00:00Z",
                    "relevance_score": 0.9,
                }
            ]
        }

    engine = search_api.UnifiedSearchEngine()
    engine.search_engines = {"duckduckgo": fake_duckduckgo}

    first = await engine.search("redis cache", ["duckduckgo"], max_results=5, enable_cache=True)
    second = await engine.search("redis cache", ["duckduckgo"], max_results=5, enable_cache=True)

    assert calls["count"] == 1
    assert first["cache"]["hit"] is False
    assert second["cache"]["hit"] is True

    await engine.client.aclose()


@pytest.mark.asyncio
async def test_search_summary_uses_upstash_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    redis = _FakeRedis()
    monkeypatch.setattr(search_api, "get_redis_client", lambda: redis)

    calls = {"count": 0}

    class _FakeVertexService:
        async def generate_text(self, **_kwargs: Any) -> Dict[str, Any]:
            calls["count"] += 1
            return {
                "status": "success",
                "text": "summary",
                "model": "gemini-test",
                "total_tokens": 12,
                "cost_usd": 0.001,
            }

    vertex_module = importlib.import_module("backend.services.vertex_ai_service")

    monkeypatch.setattr(vertex_module, "vertex_ai_service", _FakeVertexService())

    results = [
        {
            "title": "Result A",
            "url": "https://example.com/a",
            "snippet": "Snippet A",
            "source": "duckduckgo",
            "relevance_score": 0.8,
        }
    ]
    first = await search_api._summarize_search_results(
        query="bcm redis",
        results=results,
        intensity="medium",
        max_items=4,
    )
    second = await search_api._summarize_search_results(
        query="bcm redis",
        results=results,
        intensity="medium",
        max_items=4,
    )

    assert calls["count"] == 1
    assert first["cache_hit"] is False
    assert second["cache_hit"] is True


@pytest.mark.asyncio
async def test_scraper_results_use_upstash_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    redis = _FakeRedis()
    monkeypatch.setattr(scraper_api, "get_redis_client", lambda: redis)

    calls = {"count": 0}

    async def fake_balanced(url: str, user_id: str, legal_basis: str) -> Dict[str, Any]:
        calls["count"] += 1
        return {
            "url": url,
            "user_id": user_id,
            "legal_basis": legal_basis,
            "title": "Example",
            "content": "content",
        }

    scraper = scraper_api.UnifiedScraper()
    monkeypatch.setattr(scraper, "_scrape_balanced", fake_balanced)

    first = await scraper.scrape(
        url="https://example.com",
        user_id="u-1",
        strategy=scraper_api.ScrapingStrategy.BALANCED,
        legal_basis="user_request",
        enable_cache=True,
    )
    second = await scraper.scrape(
        url="https://example.com",
        user_id="u-1",
        strategy=scraper_api.ScrapingStrategy.BALANCED,
        legal_basis="user_request",
        enable_cache=True,
    )

    assert calls["count"] == 1
    assert first["cache_hit"] is False
    assert second["cache_hit"] is True

    for session in scraper.http_sessions:
        await session.aclose()
    scraper.cpu_executor.shutdown(wait=False)
