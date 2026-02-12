from __future__ import annotations

import pytest
from fastapi import HTTPException

from backend.api.v1 import workspace_guard


class _Settings:
    def __init__(self, enforce: bool):
        self.ENFORCE_BCM_READY_GATE = enforce


def test_require_workspace_id_validation() -> None:
    with pytest.raises(HTTPException) as exc_missing:
        workspace_guard.require_workspace_id(None)
    assert exc_missing.value.status_code == 400

    with pytest.raises(HTTPException) as exc_invalid:
        workspace_guard.require_workspace_id("not-a-uuid")
    assert exc_invalid.value.status_code == 400

    value = workspace_guard.require_workspace_id("11111111-1111-1111-1111-111111111111")
    assert value == "11111111-1111-1111-1111-111111111111"


def test_enforce_bcm_ready_skips_when_feature_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(workspace_guard, "get_settings", lambda: _Settings(False))
    workspace_guard.enforce_bcm_ready("11111111-1111-1111-1111-111111111111")


def test_enforce_bcm_ready_accepts_ready_workspace(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(workspace_guard, "get_settings", lambda: _Settings(True))
    monkeypatch.setattr(
        workspace_guard,
        "get_workspace_row",
        lambda _workspace_id: {"id": _workspace_id, "settings": {"bcm_ready": True}},
    )
    workspace_guard.enforce_bcm_ready("11111111-1111-1111-1111-111111111111")


def test_enforce_bcm_ready_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(workspace_guard, "get_settings", lambda: _Settings(True))
    monkeypatch.setattr(
        workspace_guard,
        "get_workspace_row",
        lambda _workspace_id: {"id": _workspace_id, "settings": {}},
    )
    monkeypatch.setattr(workspace_guard.bcm_service, "get_latest", lambda _workspace_id: None)

    with pytest.raises(HTTPException) as exc:
        workspace_guard.enforce_bcm_ready("11111111-1111-1111-1111-111111111111")

    assert exc.value.status_code == 412
