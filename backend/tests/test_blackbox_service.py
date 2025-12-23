import sys
import time
from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from uuid import uuid4
from datetime import datetime

# Hierarchical mock for google.cloud.bigquery
mock_google = MagicMock()
sys.modules["google"] = mock_google
sys.modules["google.cloud"] = mock_google.cloud
sys.modules["google.cloud.bigquery"] = mock_google.cloud.bigquery

from backend.core.vault import Vault
from backend.services.blackbox_service import BlackboxService, trace_agent
from backend.models.blackbox import BlackboxTelemetry

def test_blackbox_service_instantiation():
    mock_vault = MagicMock(spec=Vault)
    service = BlackboxService(vault=mock_vault)
    assert service.vault == mock_vault
    assert hasattr(service, "log_telemetry")

def test_blackbox_service_bigquery_client_initialization():
    mock_vault = MagicMock(spec=Vault)
    mock_vault.project_id = "test-project"
    service = BlackboxService(vault=mock_vault)
    
    client = service._get_bigquery_client()
    assert client is not None
    mock_google.cloud.bigquery.Client.assert_called_once_with(project="test-project")

def test_blackbox_service_log_telemetry_supabase():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    
    # Chain: session.table().insert().execute()
    mock_query_builder = MagicMock()
    mock_session.table.return_value = mock_query_builder
    mock_query_builder.insert.return_value = mock_query_builder
    mock_query_builder.execute.return_value = MagicMock() # Sync execute
    
    service = BlackboxService(vault=mock_vault)
    
    telemetry = BlackboxTelemetry(
        move_id=uuid4(),
        agent_id="test-agent",
        trace={"steps": ["thought"]},
        tokens=10,
        latency=0.1
    )
    
    service.log_telemetry(telemetry)
    
    mock_session.table.assert_called_once_with("blackbox_telemetry_industrial")
    mock_query_builder.insert.assert_called_once()
    mock_query_builder.execute.assert_called_once()

def test_blackbox_service_stream_to_bigquery():
    mock_vault = MagicMock()
    mock_vault.project_id = "test-project"
    service = BlackboxService(vault=mock_vault)
    
    telemetry = BlackboxTelemetry(
        move_id=uuid4(),
        agent_id="test-agent",
        trace={"steps": ["thought"]},
        tokens=10,
        latency=0.1
    )
    
    with patch("google.cloud.bigquery.Client") as mock_client_init:
        mock_bq_client = mock_client_init.return_value
        mock_bq_client.insert_rows_json.return_value = [] # No errors
        
        service.stream_to_bigquery(telemetry)
        
        mock_bq_client.insert_rows_json.assert_called_once()
        args, kwargs = mock_bq_client.insert_rows_json.call_args
        assert "telemetry_stream" in args[0]

def test_trace_agent_decorator():
    mock_service = MagicMock()
    
    # Decorate a dummy function
    @trace_agent(service=mock_service, agent_id="test-decorator-agent")
    def dummy_agent(move_id, input_data):
        return {"output": "ok", "usage": {"total_tokens": 50}}
    
    move_id = uuid4()
    result = dummy_agent(move_id, {"some": "input"})
    
    assert result["output"] == "ok"
    mock_service.log_telemetry.assert_called_once()
    telemetry = mock_service.log_telemetry.call_args[0][0]
    assert telemetry.agent_id == "test-decorator-agent"
    assert telemetry.move_id == move_id
    assert telemetry.tokens == 50