from __future__ import annotations

import importlib

import pytest

from backend.agents.langgraph_context_orchestrator import (
    format_bcm_row,
    langgraph_context_orchestrator,
)


def test_format_bcm_row() -> None:
    row = {
        "manifest": {"foundation": {"company": "Acme"}, "meta": {"synthesized": True}},
        "version": 2,
        "checksum": "abc",
        "token_estimate": 123,
        "created_at": "2026-02-12T00:00:00Z",
    }
    payload = format_bcm_row(row)
    assert payload["version"] == 2
    assert payload["checksum"] == "abc"
    assert payload["token_estimate"] == 123
    assert payload["synthesized"] is True


@pytest.mark.asyncio
async def test_context_orchestrator_seed_rebuild_reflect(monkeypatch: pytest.MonkeyPatch) -> None:
    services_pkg = importlib.import_module("backend.services")
    reflector_module = importlib.import_module("backend.services.bcm_reflector")

    class FakeBCMService:
        @staticmethod
        async def seed_from_business_context_async(workspace_id: str, business_context):
            assert workspace_id == "11111111-1111-1111-1111-111111111111"
            return {"manifest": {"foundation": {"company": "Acme"}}, "version": 1}

        @staticmethod
        async def rebuild_async(workspace_id: str):
            assert workspace_id == "11111111-1111-1111-1111-111111111111"
            return {"manifest": {"foundation": {"company": "Acme"}}, "version": 2}

    async def fake_reflect(workspace_id: str):
        assert workspace_id == "11111111-1111-1111-1111-111111111111"
        return {"status": "reflected", "workspace_id": workspace_id}

    monkeypatch.setattr(services_pkg, "bcm_service", FakeBCMService())
    monkeypatch.setattr(reflector_module, "reflect", fake_reflect)

    seed_row = await langgraph_context_orchestrator.seed(
        "11111111-1111-1111-1111-111111111111",
        {"company_name": "Acme"},
    )
    rebuild_row = await langgraph_context_orchestrator.rebuild(
        "11111111-1111-1111-1111-111111111111",
    )
    reflect_result = await langgraph_context_orchestrator.reflect(
        "11111111-1111-1111-1111-111111111111",
    )

    assert seed_row["version"] == 1
    assert rebuild_row["version"] == 2
    assert reflect_result["status"] == "reflected"

