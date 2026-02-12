from __future__ import annotations

from typing import Any, Dict

import pytest

from backend.api.v1 import workspaces as workspaces_api


def _complete_answers() -> Dict[str, Any]:
    return {
        "company_name": "Acme Labs",
        "company_website": "https://acme.test",
        "industry": "SaaS",
        "business_stage": "Seed",
        "company_description": "We help teams ship faster.",
        "primary_offer": "AI planning platform",
        "core_problem": "Teams miss deadlines due to poor coordination.",
        "ideal_customer_title": "VP Engineering",
        "ideal_customer_profile": "B2B teams with 20-200 employees.",
        "top_pain_points": ["Missed deadlines", "No visibility"],
        "top_goals": ["Ship faster", "Improve predictability"],
        "key_differentiator": "Signal fusion from code and ops systems.",
        "competitors": ["Asana", "Monday"],
        "brand_tone": ["Direct", "Confident"],
        "banned_phrases": ["Synergy"],
        "channel_priorities": ["LinkedIn", "Email", "YouTube"],
        "geographic_focus": "US",
        "pricing_model": "Per-seat",
        "proof_points": ["120 teams", "2.1M ARR"],
        "acquisition_goal": "60 SQLs/month",
        "constraints_and_guardrails": ["No unverified legal claims"],
    }


def test_normalize_onboarding_answers() -> None:
    raw = {
        "company_name": "  Acme  ",
        "top_pain_points": "pain a, pain b\npain c",
        "channel_priorities": ["LinkedIn", "LinkedIn", "Email"],
    }
    normalized = workspaces_api._normalize_onboarding_answers(raw)

    assert normalized["company_name"] == "Acme"
    assert normalized["top_pain_points"] == ["pain a", "pain b", "pain c"]
    assert normalized["channel_priorities"] == ["LinkedIn", "Email"]


def test_missing_required_steps() -> None:
    answers = workspaces_api._normalize_onboarding_answers({"company_name": "Acme"})
    missing = workspaces_api._missing_required_steps(answers)

    assert "company_name" not in missing
    assert "industry" in missing
    assert len(missing) > 1


def test_build_business_context() -> None:
    workspace_row = {"name": "Workspace A", "slug": "workspace-a"}
    context = workspaces_api._build_business_context(workspace_row, _complete_answers())

    assert context["company_profile"]["name"] == "Acme Labs"
    assert context["intelligence"]["positioning"]["uvp"]
    assert context["intelligence"]["messaging"]["oneLiner"]
    assert len(context["intelligence"]["icps"]) == 1
    assert len(context["intelligence"]["channels"]) >= 1


def test_build_onboarding_status_self_heals_when_bcm_exists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_get_latest(_workspace_id: str):
        return {"version": 1}

    monkeypatch.setattr(workspaces_api.bcm_service, "get_latest", fake_get_latest)

    settings = {
        "onboarding": {
            "schema_version": "2026.02",
            "completed": False,
            "answers": _complete_answers(),
            "updated_at": "2026-02-12T00:00:00Z",
        },
        "bcm_ready": False,
    }
    status_payload = workspaces_api._build_onboarding_status(
        workspace_id="11111111-1111-1111-1111-111111111111",
        settings=settings,
    )

    assert status_payload.completed is True
    assert status_payload.bcm_ready is True
    assert status_payload.completion_pct == 100
