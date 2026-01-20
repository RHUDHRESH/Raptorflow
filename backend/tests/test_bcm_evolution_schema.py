import pytest
from pydantic import ValidationError
from backend.schemas.bcm_evolution import BusinessContextEverything, EventType

def test_bcm_everything_valid_init():
    """Test initializing the Everything BCM with valid data"""
    data = {
        "ucid": "RF-2026-0001",
        "identity": {
            "name": "RaptorFlow",
            "core_promise": "Industrial Marketing Intelligence"
        },
        "history": {
            "total_events": 10,
            "last_event_id": "uuid-123",
            "significant_milestones": ["Launched Foundation", "Defined ICP"]
        },
        "telemetry": {
            "recent_interactions": [
                {"timestamp": "2026-01-20T08:00:00Z", "type": "SEARCH", "payload": {"query": "marketing strategy"}}
            ]
        }
    }
    
    bcm = BusinessContextEverything(**data)
    assert bcm.ucid == "RF-2026-0001"
    assert bcm.identity.name == "RaptorFlow"
    assert bcm.history.total_events == 10
    assert len(bcm.telemetry.recent_interactions) == 1

def test_bcm_everything_validation():
    """Test validation constraints"""
    # Missing UCID
    with pytest.raises(ValidationError):
        BusinessContextEverything(identity={"name": "Test"})

def test_event_type_enum():
    """Test EventType enum covers everything"""
    assert EventType.STRATEGIC_SHIFT == "STRATEGIC_SHIFT"
    assert EventType.MOVE_COMPLETED == "MOVE_COMPLETED"
    assert EventType.USER_INTERACTION == "USER_INTERACTION"
