from __future__ import annotations

from typing import Any, Dict

from fastapi.testclient import TestClient


def test_app_factory_system_routes_smoke(monkeypatch) -> None:
    """Smoke-test the canonical FastAPI factory without touching external services."""

    # Patch service registry lifecycle hooks so lifespan doesn't do real network I/O.
    async def fake_initialize_all() -> None:
        return None

    async def fake_shutdown_all() -> None:
        return None

    async def fake_check_health() -> Dict[str, Any]:
        return {
            "supabase": {"status": "healthy"},
            "redis": {"status": "healthy"},
        }

    # Patch Supabase client used by startup health-check so it succeeds without network.
    class _FakeQuery:
        def select(self, *_: Any, **__: Any) -> "_FakeQuery":
            return self

        def limit(self, *_: Any, **__: Any) -> "_FakeQuery":
            return self

        def execute(self, *_: Any, **__: Any) -> Dict[str, Any]:
            return {"data": [{"id": "00000000-0000-0000-0000-000000000000"}]}

    class _FakeSupabase:
        def table(self, *_: Any, **__: Any) -> _FakeQuery:
            return _FakeQuery()

    def fake_get_supabase_client() -> _FakeSupabase:
        return _FakeSupabase()

    import importlib

    import backend.api.system as system_api
    import backend.services.registry as registry_mod
    from backend.app_factory import create_app

    # NOTE: `backend.app` exports `lifespan` as a function, so `backend.app.lifespan`
    # as an attribute points at that function, not the module. Import explicitly.
    lifespan_mod = importlib.import_module("backend.app.lifespan")

    monkeypatch.setattr(registry_mod.registry, "initialize_all", fake_initialize_all)
    monkeypatch.setattr(registry_mod.registry, "shutdown_all", fake_shutdown_all)
    monkeypatch.setattr(registry_mod.registry, "check_health", fake_check_health)
    monkeypatch.setattr(system_api.registry, "check_health", fake_check_health)
    monkeypatch.setattr(lifespan_mod, "get_supabase_client", fake_get_supabase_client)

    app = create_app(enable_docs=False)

    with TestClient(app) as client:
        root = client.get("/")
        assert root.status_code == 200
        assert root.json()["status"] == "healthy"

        health = client.get("/health")
        assert health.status_code == 200
        body = health.json()
        assert body["status"] == "healthy"
        assert body["services"]["supabase"]["status"] == "healthy"

        # System router is also exposed under `/api/*`.
        health_api = client.get("/api/health")
        assert health_api.status_code == 200
