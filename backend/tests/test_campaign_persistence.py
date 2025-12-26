from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from models.campaigns import Campaign, CampaignStatus
from services.campaign_service import CampaignService


@pytest.mark.asyncio
async def test_campaign_service_save_campaign():
    import services.campaign_service

    mock_cursor = AsyncMock()
    mock_conn = MagicMock()
    mock_conn.commit = AsyncMock()
    mock_cursor_ctx = MagicMock()
    mock_cursor_ctx.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_conn.cursor.return_value = mock_cursor_ctx

    mock_db_ctx = MagicMock()
    mock_db_ctx.__aenter__ = AsyncMock(return_value=mock_conn)

    with patch(
        "backend.services.campaign_service.get_db_connection", return_value=mock_db_ctx
    ):
        service = CampaignService()
        campaign = Campaign(
            tenant_id=uuid4(), title="Test Campaign", objective="Verification"
        )

        await service.save_campaign(campaign)

        mock_cursor.execute.assert_called_once()
        assert "INSERT INTO campaigns" in mock_cursor.execute.call_args[0][0]
        mock_conn.commit.assert_called_once()
