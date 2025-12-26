from unittest.mock import MagicMock, patch

import pytest

from tools.blackbox_tools import fetch_historical_performance_tool


def test_fetch_historical_performance_tool():
    mock_session = MagicMock()
    mock_table = MagicMock()
    mock_session.table.return_value = mock_table
    mock_select = MagicMock()
    mock_table.select.return_value = mock_select
    mock_eq = MagicMock()
    mock_select.eq.return_value = mock_eq
    mock_execute = MagicMock()
    mock_eq.execute.return_value = mock_execute
    mock_execute.data = [{"metric_value": 10}, {"metric_value": 20}]

    with patch("backend.tools.blackbox_tools.Vault") as mock_vault_class:
        mock_vault_class.return_value.get_session.return_value = mock_session
        res = fetch_historical_performance_tool("campaign-123")
        assert res["total_value"] == 30.0
        mock_session.table.assert_called_with("blackbox_outcomes_industrial")


def test_fetch_brand_kit_alignment_tool():
    mock_session = MagicMock()
    mock_table = MagicMock()
    mock_session.table.return_value = mock_table
    mock_select = MagicMock()
    mock_table.select.return_value = mock_select
    mock_eq = MagicMock()
    mock_select.eq.return_value = mock_eq
    mock_execute = MagicMock()
    mock_eq.execute.return_value = mock_execute
    mock_execute.data = [{"name": "Serious Brand", "primary_color": "#000"}]

    with patch("backend.tools.blackbox_tools.Vault") as mock_vault_class:
        mock_vault_class.return_value.get_session.return_value = mock_session

        # This will fail until implemented
        try:
            from tools.blackbox_tools import fetch_brand_kit_alignment_tool

            res = fetch_brand_kit_alignment_tool("bk-123")
            assert res["brand_kit"]["name"] == "Serious Brand"
            mock_session.table.assert_called_with("foundation_brand_kit")
        except ImportError:
            pytest.fail("fetch_brand_kit_alignment_tool not implemented")
