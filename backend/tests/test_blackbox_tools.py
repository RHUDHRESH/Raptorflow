import pytest
from unittest.mock import MagicMock, patch
from backend.tools.blackbox_tools import fetch_historical_performance_tool

def test_fetch_historical_performance_tool():
    # 1. Create the mock session and the chain
    mock_session = MagicMock()
    mock_table = MagicMock()
    mock_session.table.return_value = mock_table
    mock_select = MagicMock()
    mock_table.select.return_value = mock_select
    mock_eq = MagicMock()
    mock_select.eq.return_value = mock_eq
    mock_execute = MagicMock()
    mock_eq.execute.return_value = mock_execute
    
    # 2. Set the data
    mock_execute.data = [{"metric_value": 10}, {"metric_value": 20}]
    
    # 3. Patch Vault to return this session
    with patch("backend.tools.blackbox_tools.Vault") as mock_vault_class:
        mock_vault_class.return_value.get_session.return_value = mock_session
        
        res = fetch_historical_performance_tool("campaign-123")
        
        assert res["total_value"] == 30.0
        mock_session.table.assert_called_with("blackbox_outcomes_industrial")