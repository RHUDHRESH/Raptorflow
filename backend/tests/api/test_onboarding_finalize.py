"""Tests for onboarding finalization endpoint (canonical)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.asyncio
async def test_finalize_success(client: TestClient):
    session_id = "test-session"
    steps = {str(i): {"data": {"field": i}} for i in range(1, 21)}
    metadata = {"workspace_id": "ws-1", "user_id": "user-1"}

    mock_context = MagicMock()
    mock_context.dict.return_value = {"version": "2.0"}

    mock_manifest = MagicMock()
    mock_manifest.dict.return_value = {"version": "2.0", "workspace_id": "ws-1"}

    supabase = MagicMock()
    supabase.table.return_value.update.return_value.eq.return_value.execute = (
        AsyncMock()
    )

    with patch(
        "api.v1.onboarding.session_manager", new=AsyncMock()
    ) as mock_session, patch(
        "api.v1.onboarding.extract_business_context_from_steps",
        return_value=mock_context,
    ), patch(
        "api.v1.onboarding.BCMReducer"
    ) as mock_reducer_cls, patch(
        "api.v1.onboarding.get_supabase_admin", return_value=supabase
    ), patch(
        "api.v1.onboarding.BCMService"
    ) as mock_bcm_service:
        mock_session.get_all_steps.return_value = steps
        mock_session.get_metadata.return_value = metadata
        mock_session.get_progress.return_value = {"completed": 20, "total": 23}
        mock_session.clear_session.return_value = True

        mock_reducer = AsyncMock()
        mock_reducer.reduce.return_value = mock_manifest
        mock_reducer_cls.return_value = mock_reducer

        bcm_service = AsyncMock()
        bcm_service.store_manifest.return_value = True
        mock_bcm_service.return_value = bcm_service

        response = client.post(f"/api/onboarding/{session_id}/finalize")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] == session_id
        assert data["bcm_generated"] is True


@pytest.mark.asyncio
async def test_finalize_insufficient_steps(client: TestClient):
    session_id = "test-session"
    steps = {str(i): {"data": {"field": i}} for i in range(1, 5)}

    with patch("api.v1.onboarding.session_manager", new=AsyncMock()) as mock_session:
        mock_session.get_all_steps.return_value = steps
        mock_session.get_metadata.return_value = {"workspace_id": "ws-1"}
        mock_session.get_progress.return_value = {"completed": 4, "total": 23}

        response = client.post(f"/api/onboarding/{session_id}/finalize")

        assert response.status_code == 400


@pytest.mark.asyncio
async def test_finalize_no_steps(client: TestClient):
    session_id = "test-session"

    with patch("api.v1.onboarding.session_manager", new=AsyncMock()) as mock_session:
        mock_session.get_all_steps.return_value = None

        response = client.post(f"/api/onboarding/{session_id}/finalize")

        assert response.status_code == 404
