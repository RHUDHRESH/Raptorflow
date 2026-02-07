from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from api.v1.foundation import get_foundation_service
from main import app
from models.foundation import BrandKit

client = TestClient(app)


@pytest.fixture
def mock_service():
    service = AsyncMock()
    # Override the dependency
    app.dependency_overrides[get_foundation_service] = lambda: service
    yield service
    # Clean up overrides after test
    app.dependency_overrides.clear()


def test_create_brand_kit_api(mock_service):
    """Test POST /v1/foundation/brand-kit."""
    bk_id = uuid4()
    tenant_id = uuid4()
    mock_service.create_brand_kit.return_value = BrandKit(
        id=bk_id,
        tenant_id=tenant_id,
        name="API Brand",
        primary_color="#000",
        secondary_color="#000",
        accent_color="#000",
    )

    payload = {
        "tenant_id": str(tenant_id),
        "name": "API Brand",
        "primary_color": "#000",
        "secondary_color": "#000",
        "accent_color": "#000",
    }

    response = client.post("/v1/foundation/brand-kit", json=payload)
    assert response.status_code == 201
    assert response.json()["name"] == "API Brand"


def test_get_brand_kit_api(mock_service):
    """Test GET /v1/foundation/brand-kit/{id}."""
    bk_id = uuid4()
    mock_service.get_brand_kit.return_value = BrandKit(
        id=bk_id,
        tenant_id=uuid4(),
        name="API Brand",
        primary_color="#000",
        secondary_color="#000",
        accent_color="#000",
    )

    response = client.get(f"/v1/foundation/brand-kit/{bk_id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(bk_id)


def test_get_brand_kit_not_found(mock_service):
    """Test GET /v1/foundation/brand-kit/{id} not found."""
    mock_service.get_brand_kit.return_value = None
    response = client.get(f"/v1/foundation/brand-kit/{uuid4()}")
    assert response.status_code == 404
