from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from models.foundation import BrandKit
from services.foundation_service import FoundationService


@pytest.fixture
def mock_vault():
    vault = MagicMock()
    # vault.get_session returns the session (sync or async depending on impl)
    vault.get_session = AsyncMock()
    return vault


@pytest.mark.asyncio
async def test_create_brand_kit(mock_vault):
    """Test successful brand kit creation."""
    session = MagicMock()
    mock_vault.get_session.return_value = session

    mock_execute = MagicMock()
    mock_execute.data = [
        {
            "id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "name": "Test",
            "primary_color": "#000",
            "secondary_color": "#000",
            "accent_color": "#000",
        }
    ]

    # Chain: session.table().insert().execute()
    session.table.return_value.insert.return_value.execute = AsyncMock(
        return_value=mock_execute
    )

    service = FoundationService(mock_vault)
    bk = BrandKit(
        tenant_id=uuid4(),
        name="Test",
        primary_color="#000",
        secondary_color="#000",
        accent_color="#000",
    )

    result = await service.create_brand_kit(bk)
    assert result.name == "Test"
    session.table.assert_called_with("foundation_brand_kit")


@pytest.mark.asyncio
async def test_get_brand_kit_none(mock_vault):
    """Test retrieving non-existent brand kit."""
    session = MagicMock()
    mock_vault.get_session.return_value = session

    mock_execute = MagicMock()
    mock_execute.data = []

    # Chain: session.table().select().eq().execute()
    session.table.return_value.select.return_value.eq.return_value.execute = AsyncMock(
        return_value=mock_execute
    )

    service = FoundationService(mock_vault)
    result = await service.get_brand_kit(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_validate_brand_kit_invalid(mock_vault):
    """Test brand kit validation with missing fields."""
    service = FoundationService(mock_vault)
    service.get_brand_kit = AsyncMock(return_value=None)

    result = await service.validate_brand_kit(uuid4())
    assert result is False
