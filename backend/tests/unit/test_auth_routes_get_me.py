from __future__ import annotations

from typing import Any, Dict, Optional

import pytest
from fastapi import HTTPException

from backend.api.v1.auth import routes


class _AsyncAuthService:
    async def get_user(self, token: Optional[str]) -> Optional[Dict[str, Any]]:
        if token == "valid-token":
            return {"id": "user-1", "email": "user@example.com", "user_metadata": {"full_name": "Async User"}}
        return None


class _SyncAuthService:
    def get_user(self, token: Optional[str]) -> Optional[Dict[str, Any]]:
        if token == "valid-token":
            return {"id": "user-2", "email": "sync@example.com", "user_metadata": {}}
        return None


@pytest.mark.asyncio
async def test_get_me_supports_async_auth_services(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(routes, "get_auth_service", lambda: _AsyncAuthService())

    user = await routes.get_me(authorization="Bearer valid-token", cookie_access=None)

    assert user["id"] == "user-1"
    assert user["email"] == "user@example.com"
    assert user["account"]["profile_complete"] is True


@pytest.mark.asyncio
async def test_get_me_supports_sync_auth_services(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(routes, "get_auth_service", lambda: _SyncAuthService())

    user = await routes.get_me(authorization="Bearer valid-token", cookie_access=None)

    assert user["id"] == "user-2"
    assert user["email"] == "sync@example.com"
    assert user["account"]["profile_complete"] is False
    assert "full_name" in user["account"]["missing_required_fields"]


@pytest.mark.asyncio
async def test_get_me_rejects_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(routes, "get_auth_service", lambda: _AsyncAuthService())

    with pytest.raises(HTTPException) as exc:
        await routes.get_me(authorization=None, cookie_access=None)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_me_rejects_invalid_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(routes, "get_auth_service", lambda: _AsyncAuthService())

    with pytest.raises(HTTPException) as exc:
        await routes.get_me(authorization="Bearer invalid-token", cookie_access=None)

    assert exc.value.status_code == 401
