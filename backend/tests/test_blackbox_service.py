import sys
import time
from unittest.mock import MagicMock, AsyncMock, patch, ANY
import pytest
from uuid import uuid4
from datetime import datetime

# Hierarchical mock for google.cloud dependencies WITHOUT breaking google.cloud namespace
if "google" not in sys.modules:
    sys.modules["google"] = MagicMock()
if "google.cloud" not in sys.modules:
    sys.modules["google.cloud"] = MagicMock()

mock_bigquery = MagicMock()
sys.modules["google.cloud.bigquery"] = mock_bigquery

mock_secretmanager = MagicMock()
sys.modules["google.cloud.secretmanager"] = mock_secretmanager

# Mock supabase
sys.modules["supabase"] = MagicMock()

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
    mock_bigquery.Client.assert_called_once_with(project="test-project")

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

def test_blackbox_service_get_agent_audit_log():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    
    mock_query_builder = MagicMock()
    mock_session.table.return_value = mock_query_builder
    mock_query_builder.select.return_value = mock_query_builder
    mock_query_builder.eq.return_value = mock_query_builder
    mock_query_builder.order.return_value = mock_query_builder
    mock_query_builder.limit.return_value = mock_query_builder
    
    mock_response = MagicMock()
    mock_response.data = [{"id": "test-id", "agent_id": "test-agent"}]
    mock_query_builder.execute.return_value = mock_response
    
    service = BlackboxService(vault=mock_vault)
    logs = service.get_agent_audit_log("test-agent")
    
    assert len(logs) == 1
    assert logs[0]["agent_id"] == "test-agent"
    mock_session.table.assert_called_with("blackbox_telemetry_industrial")

def test_telemetry_capture_integrity():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    mock_vault.project_id = "test-project"
    
    mock_query_builder = MagicMock()
    mock_session.table.return_value = mock_query_builder
    mock_query_builder.insert.return_value = mock_query_builder
    mock_query_builder.execute.return_value = MagicMock()
    
    service = BlackboxService(vault=mock_vault)
    
    telemetry = BlackboxTelemetry(
        move_id=uuid4(),
        agent_id="integrity-test-agent",
        trace={"test": "data"},
        tokens=100,
        latency=1.5
    )
    
    with patch("google.cloud.bigquery.Client") as mock_client_init:
        mock_bq_client = mock_client_init.return_value
        mock_bq_client.insert_rows_json.return_value = []
        
        service.log_telemetry(telemetry)
        
        # Verify Supabase call
        mock_session.table.assert_called_with("blackbox_telemetry_industrial")
        mock_query_builder.insert.assert_called_once()
        
        # Verify BigQuery call
        mock_bq_client.insert_rows_json.assert_called_once()
        args, _ = mock_bq_client.insert_rows_json.call_args
        assert "telemetry_stream" in args[0]
        assert args[1][0]["agent_id"] == "integrity-test-agent"

def test_bigquery_streaming_latency():
    mock_vault = MagicMock()
    mock_vault.project_id = "test-project"
    service = BlackboxService(vault=mock_vault)
    
    telemetry = BlackboxTelemetry(
        move_id=uuid4(),
        agent_id="latency-test-agent",
        trace={"test": "data"},
        tokens=10,
        latency=0.1
    )
    
    with patch("google.cloud.bigquery.Client") as mock_client_init:
        mock_bq_client = mock_client_init.return_value
        
        # Simulate a fast response
        start_time = time.time()
        service.stream_to_bigquery(telemetry)
        duration = time.time() - start_time
        
        # In a unit test with mocks, this should be extremely fast (< 50ms)
        assert duration < 0.05
        mock_bq_client.insert_rows_json.assert_called_once()

def test_blackbox_service_calculate_move_cost():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    
    mock_query_builder = MagicMock()
    mock_session.table.return_value = mock_query_builder
    mock_query_builder.select.return_value = mock_query_builder
    mock_query_builder.eq.return_value = mock_query_builder
    
    mock_response = MagicMock()
    mock_response.data = [{"tokens": 100}, {"tokens": 250}]
    mock_query_builder.execute.return_value = mock_response
    
    service = BlackboxService(vault=mock_vault)
    move_id = uuid4()
    total_tokens = service.calculate_move_cost(move_id)
    
    assert total_tokens == 350
    mock_session.table.assert_called_with("blackbox_telemetry_industrial")
    mock_query_builder.eq.assert_called_with("move_id", str(move_id))

def test_blackbox_service_upsert_learning_embedding():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    
    mock_query_builder = MagicMock()
    mock_session.table.return_value = mock_query_builder
    mock_query_builder.insert.return_value = mock_query_builder
    mock_query_builder.execute.return_value = MagicMock()
    
    service = BlackboxService(vault=mock_vault)
    
    # Mock Vertex AI Embeddings
    with patch("backend.services.blackbox_service.InferenceProvider.get_embeddings") as mock_get_embeds:
        mock_embed_model = MagicMock()
        mock_get_embeds.return_value = mock_embed_model
        mock_embed_model.embed_query.return_value = [0.1] * 768
        
        service.upsert_learning_embedding(
            content="Successful ICP engagement",
            learning_type="strategic",
            source_ids=[uuid4()]
        )
        
        mock_embed_model.embed_query.assert_called_once_with("Successful ICP engagement")
        mock_session.table.assert_called_with("blackbox_learnings_industrial")
        mock_query_builder.insert.assert_called_once()

def test_blackbox_service_search_strategic_memory():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    
    service = BlackboxService(vault=mock_vault)
    
    # Mock Vertex AI Embeddings
    with patch("backend.services.blackbox_service.InferenceProvider.get_embeddings") as mock_get_embeds:
        mock_embed_model = MagicMock()
        mock_get_embeds.return_value = mock_embed_model
        mock_embed_model.embed_query.return_value = [0.1] * 768
        
        # Mock RPC response
        mock_rpc = MagicMock()
        mock_session.rpc.return_value = mock_rpc
        mock_rpc.execute.return_value = MagicMock(data=[
            {"id": str(uuid4()), "content": "High conversion on LinkedIn", "similarity": 0.92}
        ])
        
        results = service.search_strategic_memory(query="What worked on social?", limit=3)
        
        assert len(results) == 1
        assert results[0]["content"] == "High conversion on LinkedIn"
        mock_embed_model.embed_query.assert_called_once_with("What worked on social?")
        mock_session.rpc.assert_called_once()
        args, kwargs = mock_session.rpc.call_args
        assert args[0] == "match_blackbox_learnings"
        assert kwargs["params"]["query_embedding"] == [0.1] * 768
        assert kwargs["params"]["match_count"] == 3

def test_blackbox_service_link_learning_to_evidence():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    
    mock_query_builder = MagicMock()
    mock_session.table.return_value = mock_query_builder
    mock_query_builder.update.return_value = mock_query_builder
    mock_query_builder.eq.return_value = mock_query_builder
    mock_query_builder.execute.return_value = MagicMock()
    
    service = BlackboxService(vault=mock_vault)
    
    learning_id = uuid4()
    trace_ids = [uuid4(), uuid4()]
    
    service.link_learning_to_evidence(learning_id, trace_ids)
    
    mock_session.table.assert_called_with("blackbox_learnings_industrial")
    mock_query_builder.update.assert_called_once()
    mock_query_builder.eq.assert_called_once_with("id", str(learning_id))
    
    # Verify the update payload
    update_data = mock_query_builder.update.call_args[0][0]
    assert "source_ids" in update_data
    for tid in trace_ids:
        assert str(tid) in update_data["source_ids"]

def test_vector_search_relevance():
    """Verify that vector search handles similarity scores and limits correctly."""
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    
    service = BlackboxService(vault=mock_vault)
    
    # Mock Vertex AI Embeddings
    with patch("backend.services.blackbox_service.InferenceProvider.get_embeddings") as mock_get_embeds:
        mock_embed_model = MagicMock()
        mock_get_embeds.return_value = mock_embed_model
        mock_embed_model.embed_query.return_value = [0.1] * 768
        
        # Mock RPC response with varying similarity
        mock_rpc = MagicMock()
        mock_session.rpc.return_value = mock_rpc
        mock_rpc.execute.return_value = MagicMock(data=[
            {"id": "1", "content": "Perfect match", "similarity": 0.99},
            {"id": "2", "content": "Close match", "similarity": 0.85},
            {"id": "3", "content": "Marginal match", "similarity": 0.51}
        ])
        
        results = service.search_strategic_memory(query="High relevance search", limit=10)
        
        assert len(results) == 3
        assert results[0]["similarity"] > results[1]["similarity"]
        assert results[0]["content"] == "Perfect match"
        
        # Verify RPC params
        _, kwargs = mock_session.rpc.call_args
        assert kwargs["params"]["match_count"] == 10
        assert kwargs["params"]["match_threshold"] == 0.5


def test_vector_search_relevance():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    
    mock_rpc_builder = MagicMock()
    mock_session.rpc.return_value = mock_rpc_builder
    
    # Mock data with descending similarity
    mock_data = [
        {"content": "Highly relevant", "similarity": 0.95},
        {"content": "Somewhat relevant", "similarity": 0.75},
        {"content": "Barely relevant", "similarity": 0.51}
    ]
    mock_rpc_builder.execute.return_value = MagicMock(data=mock_data)
    
    service = BlackboxService(vault=mock_vault)
    
    with patch("backend.services.blackbox_service.InferenceProvider.get_embeddings") as mock_get_embeds:
        mock_embed_model = MagicMock()
        mock_get_embeds.return_value = mock_embed_model
        mock_embed_model.embed_query.return_value = [0.1] * 768
        
        results = service.search_strategic_memory(query="relevance test", limit=10)
        
        assert len(results) == 3
        assert results[0]["similarity"] > results[1]["similarity"]
        assert results[2]["similarity"] > 0.5