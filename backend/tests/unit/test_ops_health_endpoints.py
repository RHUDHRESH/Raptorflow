from __future__ import annotations

from typing import Any, Dict, List

from fastapi.testclient import TestClient


def test_ops_health_endpoints_smoke(monkeypatch) -> None:
    """Exercise the `/api/ops/*` endpoints without real DB/Redis."""

    async def fake_initialize_all() -> None:
        return None

    async def fake_shutdown_all() -> None:
        return None

    async def fake_check_health() -> Dict[str, Any]:
        return {
            "bcm_service": {"status": "healthy"},
            "vertex_ai_service": {"status": "healthy"},
        }

    async def fake_pool_stats() -> Dict[str, Any]:
        return {
            "status": "healthy",
            "size": 5,
            "free_size": 5,
            "min_size": 1,
            "max_size": 10,
        }

    class _FakeRedis:
        def ping(self) -> bool:
            return True

        def set(self, *_: Any, **__: Any) -> None:
            return None

        def get(self, *_: Any, **__: Any) -> str:
            return "ok"

        def delete(self, *_: Any, **__: Any) -> None:
            return None

    def fake_get_redis_client() -> _FakeRedis:
        return _FakeRedis()

    def fake_query_stats(*_: Any, **__: Any) -> List[Dict[str, Any]]:
        return [{"query": "select 1", "count": 1, "avg_ms": 0.1}]

    def fake_slow_queries(*_: Any, **__: Any) -> List[Dict[str, Any]]:
        return []

    import backend.api.v1.health as ops_health
    import importlib
    import backend.services.registry as registry_mod
    from backend.app_factory import create_app

    lifespan_mod = importlib.import_module("backend.app.lifespan")

    monkeypatch.setattr(registry_mod.registry, "initialize_all", fake_initialize_all)
    monkeypatch.setattr(registry_mod.registry, "shutdown_all", fake_shutdown_all)
    monkeypatch.setattr(registry_mod.registry, "check_health", fake_check_health)

    # Avoid real Supabase I/O during lifespan startup health-check.
    def fake_get_supabase_client() -> None:
        raise RuntimeError("no supabase in unit test")

    monkeypatch.setattr(lifespan_mod, "get_supabase_client", fake_get_supabase_client)

    monkeypatch.setattr(ops_health, "_safe_pool_stats", fake_pool_stats)
    monkeypatch.setattr(ops_health, "get_redis_client", fake_get_redis_client)
    monkeypatch.setattr(ops_health.query_monitor, "get_stats", fake_query_stats)
    monkeypatch.setattr(ops_health.query_monitor, "get_slow_queries", fake_slow_queries)

    app = create_app(enable_docs=False)

    with TestClient(app) as client:
        resp = client.get("/api/ops/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] in {"healthy", "degraded"}
        assert body["services"]["database"]["status"] == "healthy"
        assert body["services"]["cache"]["status"] == "healthy"

        arch = client.get("/api/ops/ai-architecture")
        assert arch.status_code == 200
        assert arch.json()["status"] == "ok"
