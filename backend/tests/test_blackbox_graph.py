import pytest
from uuid import uuid4
from backend.graphs.blackbox_analysis import AnalysisState

def test_analysis_state_definition():
    
    state = {
        "move_id": str(uuid4()),
        "telemetry_data": [],
        "findings": [],
        "outcomes": [],
        "reflection": "",
        "confidence": 0.0
    }
    # TypedDict verification
    assert "move_id" in AnalysisState.__annotations__
    assert "telemetry_data" in AnalysisState.__annotations__
