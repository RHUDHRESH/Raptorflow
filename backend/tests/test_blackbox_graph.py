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

def test_analysis_state_accumulation():
    state1: AnalysisState = {
        "move_id": "test",
        "telemetry_data": [{"id": 1}],
        "findings": ["initial"],
        "outcomes": [],
        "reflection": "",
        "confidence": 0.0,
        "status": "start"
    }
    
    state2: AnalysisState = {
        "telemetry_data": [{"id": 2}],
        "findings": ["new"],
        "reflection": "updated"
    }
    
    # In LangGraph, the StateGraph handles this accumulation via operator.add
    # We simulate it here by showing the logic we expect the graph to follow
    import operator
    
    combined_telemetry = operator.add(state1["telemetry_data"], state2["telemetry_data"])
    combined_findings = operator.add(state1["findings"], state2["findings"])
    
    assert len(combined_telemetry) == 2
    assert len(combined_findings) == 2
    assert combined_findings == ["initial", "new"]
