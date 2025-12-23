from unittest.mock import MagicMock, patch
from uuid import uuid4

from backend.graphs.blackbox_analysis import AnalysisState, ingest_telemetry_node


def test_analysis_state_definition():
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
        "status": "start",
    }

    state2 = {
        "telemetry_data": [{"id": 2}],
        "findings": ["new"],
        "reflection": "updated",
    }

    import operator

    combined_telemetry = operator.add(
        state1["telemetry_data"], state2["telemetry_data"]
    )
    combined_findings = operator.add(state1["findings"], state2["findings"])

    assert len(combined_telemetry) == 2
    assert len(combined_findings) == 2
    assert combined_findings == ["initial", "new"]


def test_ingest_telemetry_node():
    mock_session = MagicMock()
    mock_data = [{"id": "t1", "agent_id": "a1", "tokens": 10}]

    # Mocking the chained calls: session.table().select().eq().execute()
    mock_query = MagicMock()
    mock_session.table.return_value = mock_query
    mock_query.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.execute.return_value = MagicMock(data=mock_data)

    with patch("backend.core.vault.Vault") as mock_vault_class:
        mock_vault_instance = mock_vault_class.return_value
        mock_vault_instance.get_session.return_value = mock_session
        move_id = str(uuid4())
        state: AnalysisState = {"move_id": move_id, "telemetry_data": []}

        result = ingest_telemetry_node(state)

        assert "telemetry_data" in result
        assert len(result["telemetry_data"]) == 1
        assert result["telemetry_data"][0]["id"] == "t1"
        mock_session.table.assert_called_with("blackbox_telemetry_industrial")


