from unittest.mock import MagicMock, patch
from backend.graphs.blackbox_analysis import AnalysisState, ingest_telemetry_node

def test_ingest_telemetry_node():
    # 1. Setup State
    state: AnalysisState = {
        "move_id": "test-move-id",
        "telemetry_data": [],
        "findings": [],
        "outcomes": [],
        "reflection": "",
        "confidence": 1.0,
        "status": "starting"
    }
    
    # 2. Mock Service
    mock_service = MagicMock()
    mock_service.get_agent_audit_log.return_value = [{"id": "t1", "agent_id": "a1"}]
    
    # 3. Execute Node
    with patch("backend.graphs.blackbox_analysis.get_blackbox_service", return_value=mock_service):
        new_state = ingest_telemetry_node(state)
        
        assert len(new_state["telemetry_data"]) == 1
        assert new_state["status"] == "ingested"
        mock_service.get_agent_audit_log.assert_called_once()