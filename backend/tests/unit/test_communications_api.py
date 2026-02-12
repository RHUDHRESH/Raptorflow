from __future__ import annotations

from typing import Any, Dict, List

import pytest
from fastapi import HTTPException

from backend.api.v1 import communications as communications_api


@pytest.mark.asyncio
async def test_contact_logged_only_when_email_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(communications_api.email_service, "api_key", "")

    response = await communications_api.submit_contact(
        communications_api.ContactRequest(
            name="Jane Doe",
            email="jane@example.com",
            subject="Help",
            message="I need help with onboarding and workspace setup.",
        ),
    )

    assert response.accepted is True
    assert response.status == "logged_only"
    assert response.support_delivery == "skipped"
    assert response.ack_delivery == "skipped"


@pytest.mark.asyncio
async def test_contact_sends_support_and_ack(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: List[Dict[str, Any]] = []

    def fake_send(**kwargs):
        calls.append(kwargs)
        return {"status": "success"}

    monkeypatch.setattr(communications_api.email_service, "api_key", "re_test")
    monkeypatch.setattr(communications_api.email_service, "send", fake_send)
    monkeypatch.setattr(communications_api.settings, "EMAIL_FROM", "support@raptorflow.ai")
    monkeypatch.setattr(communications_api.settings, "SUPPORT_EMAIL_TO", "")

    payload = communications_api.ContactRequest(
        name="  Jane Doe  ",
        email=" jane@example.com ",
        subject="   ",
        message="   Please help me configure Supabase and onboarding flow.   ",
    )
    response = await communications_api.submit_contact(payload)

    assert response.status == "sent"
    assert len(calls) == 2
    assert calls[0]["to"] == "support@raptorflow.ai"
    assert calls[0]["subject"] == "[Contact] General inquiry"
    assert calls[1]["to"] == "jane@example.com"
    assert calls[0]["context"]["name"] == "Jane Doe"
    assert calls[0]["context"]["message"].startswith("Please help")


@pytest.mark.asyncio
async def test_contact_rejects_whitespace_message() -> None:
    payload = communications_api.ContactRequest(
        name="Jane",
        email="jane@example.com",
        subject="Support",
        message="            ",
    )

    with pytest.raises(HTTPException) as exc:
        await communications_api.submit_contact(payload)

    assert exc.value.status_code == 422
    assert exc.value.detail == "Message is too short"

