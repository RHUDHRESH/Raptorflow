from uuid import uuid4

import pytest
from pydantic import ValidationError

from models.campaigns import Campaign, CampaignStatus
from models.foundation import BrandKit
from models.moves import Move, MoveStatus
from models.telemetry import TelemetryLog


def test_brand_kit_validation():
    """Test BrandKit model validation."""
    valid_data = {
        "tenant_id": uuid4(),
        "name": "Test Brand",
        "primary_color": "#000000",
        "secondary_color": "#FFFFFF",
        "accent_color": "#FF0000",
    }
    bk = BrandKit(**valid_data)
    assert bk.name == "Test Brand"

    with pytest.raises(ValidationError):
        BrandKit(name="Missing Fields")


def test_campaign_validation():
    """Test Campaign model validation."""
    valid_data = {"tenant_id": uuid4(), "title": "Launch Campaign", "status": "active"}
    cp = Campaign(**valid_data)
    assert cp.status == CampaignStatus.ACTIVE

    with pytest.raises(ValidationError):
        Campaign(title="Invalid Status", status="invalid-status")


def test_move_validation():
    """Test Move model validation."""
    valid_data = {"campaign_id": uuid4(), "title": "Social Post", "status": "pending"}
    mv = Move(**valid_data)
    assert mv.status == MoveStatus.PENDING


def test_telemetry_validation():
    """Test TelemetryLog model validation."""
    valid_data = {
        "tenant_id": uuid4(),
        "entity_type": "move",
        "entity_id": uuid4(),
        "event_type": "execution_start",
    }
    tl = TelemetryLog(**valid_data)
    assert tl.entity_type == "move"
