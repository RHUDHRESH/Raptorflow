import sys
import time
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from datetime import datetime

# Hierarchical mock for google.cloud dependencies WITHOUT breaking google.cloud namespace
if "google" not in sys.modules:
    sys.modules["google"] = MagicMock()
if "google.cloud" not in sys.modules:
    sys.modules["google.cloud"] = MagicMock()

# Note: BigQuery and SecretManager mocks are expected to be in sys.modules via conftest.py
# or the previous lines if they were missing.

from backend.core.vault import Vault
from backend.models.blackbox import BlackboxTelemetry
from backend.services.blackbox_service import BlackboxService, trace_agent


def test_blackbox_service_instantiation():
    mock_vault = MagicMock(spec=Vault)
    service = BlackboxService(vault=mock_vault)
    assert service.vault == mock_vault
    assert hasattr(service, "log_telemetry")


def test_blackbox_service_bigquery_client_initialization():
    mock_vault = MagicMock(spec=Vault)
    mock_vault.project_id = "test-project"
    service = BlackboxService(vault=mock_vault)

    # Importing here to use the mock from sys.modules
    from google.cloud import bigquery

    client = service._get_bigquery_client()
    assert client is not None
    bigquery.Client.assert_called_once_with(project="test-project")


def test_blackbox_service_log_telemetry_supabase():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session

    # Chain: session.table().insert().execute()
    mock_query_builder = MagicMock()
    mock_session.table.return_value = mock_query_builder
    mock_query_builder.insert.return_value = mock_query_builder
    mock_query_builder.execute.return_value = MagicMock()  # Sync execute

    service = BlackboxService(vault=mock_vault)

    telemetry = BlackboxTelemetry(
        move_id=uuid4(),
        agent_id="test-agent",
        trace={"steps": ["thought"]},
        tokens=10,
        latency=0.1,
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
        latency=0.1,
    )

    with patch("google.cloud.bigquery.Client") as mock_client_init:
        mock_bq_client = mock_client_init.return_value
        mock_bq_client.insert_rows_json.return_value = []  # No errors

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
        latency=1.5,
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
        latency=0.1,
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
    with patch(
        "backend.services.blackbox_service.InferenceProvider.get_embeddings"
    ) as mock_get_embeds:
        mock_embed_model = MagicMock()
        mock_get_embeds.return_value = mock_embed_model
        mock_embed_model.embed_query.return_value = [0.1] * 768

        service.upsert_learning_embedding(
            content="Successful ICP engagement",
            learning_type="strategic",
            source_ids=[uuid4()],
        )

        mock_embed_model.embed_query.assert_called_once_with(
            "Successful ICP engagement"
        )
        mock_session.table.assert_called_with("blackbox_learnings_industrial")
        mock_query_builder.insert.assert_called_once()


def test_blackbox_service_search_strategic_memory():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session

    service = BlackboxService(vault=mock_vault)

    # Mock Vertex AI Embeddings
    with patch(
        "backend.services.blackbox_service.InferenceProvider.get_embeddings"
    ) as mock_get_embeds:
        mock_embed_model = MagicMock()
        mock_get_embeds.return_value = mock_embed_model
        mock_embed_model.embed_query.return_value = [0.1] * 768

        # Mock RPC response
        mock_rpc = MagicMock()
        mock_session.rpc.return_value = mock_rpc
        mock_rpc.execute.return_value = MagicMock(
            data=[
                {
                    "id": str(uuid4()),
                    "content": "High conversion on LinkedIn",
                    "similarity": 0.92,
                }
            ]
        )

        results = service.search_strategic_memory(
            query="What worked on social?", limit=3
        )

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
    with patch(
        "backend.services.blackbox_service.InferenceProvider.get_embeddings"
    ) as mock_get_embeds:
        mock_embed_model = MagicMock()
        mock_get_embeds.return_value = mock_embed_model
        mock_embed_model.embed_query.return_value = [0.1] * 768

        # Mock RPC response with varying similarity
        mock_rpc = MagicMock()
        mock_session.rpc.return_value = mock_rpc
        mock_rpc.execute.return_value = MagicMock(
            data=[
                {"id": "1", "content": "Perfect match", "similarity": 0.99},
                {"id": "2", "content": "Close match", "similarity": 0.85},
                {"id": "3", "content": "Marginal match", "similarity": 0.51},
            ]
        )

        results = service.search_strategic_memory(
            query="High relevance search", limit=10
        )

        assert len(results) == 3
        assert results[0]["similarity"] > results[1]["similarity"]
        assert results[2]["similarity"] > 0.5


def test_blackbox_service_categorize_learning():
    mock_vault = MagicMock()
    service = BlackboxService(vault=mock_vault)

    # Mock LLM response
    with patch(
        "backend.services.blackbox_service.InferenceProvider.get_model"
    ) as mock_get_model:
        mock_llm = MagicMock()
        mock_get_model.return_value = mock_llm

        # Simulate LLM returning a category
        mock_response = MagicMock()
        mock_response.content = "strategic"
        mock_llm.invoke.return_value = mock_response

        category = service.categorize_learning(
            content="We should focus on LinkedIn for high-ticket SaaS founders."
        )

        assert category == "strategic"
        mock_llm.invoke.assert_called_once()
        # Verify prompt contains the content
        call_args = mock_llm.invoke.call_args[0][0]
        assert "We should focus on LinkedIn" in str(call_args)


def test_blackbox_service_get_memory_context_for_planner():
    mock_vault = MagicMock()
    service = BlackboxService(vault=mock_vault)

    # Mock search_strategic_memory
    with patch.object(service, "search_strategic_memory") as mock_search:
        mock_search.return_value = [
            {"content": "LinkedIn works well for SaaS", "learning_type": "strategic"},
            {"content": "Short copy is better", "learning_type": "tactical"},
        ]

        # This will fail until implemented
        try:
            context = service.get_memory_context_for_planner(move_type="linkedin_post")
            assert "LinkedIn works well for SaaS" in context
            assert "Short copy is better" in context
            mock_search.assert_called_once_with(query="linkedin_post", limit=5)
        except AttributeError:
            pytest.fail("get_memory_context_for_planner not implemented")

def test_blackbox_service_compute_roi():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    
    service = BlackboxService(vault=mock_vault)
    
    campaign_id = uuid4()
    move_id = str(uuid4())
    
    # 1. Mock moves fetching
    mock_moves_query = MagicMock()
    mock_moves_query.execute.return_value = MagicMock(data=[{"id": move_id}])
    
    # 2. Mock token cost fetching (via calculate_move_cost)
    # We need to mock the table call inside calculate_move_cost
    mock_tokens_res = MagicMock()
    mock_tokens_res.data = [{"tokens": 10000}]
    
    # 3. Mock outcomes fetching
    mock_outcomes_res = MagicMock()
    mock_outcomes_res.data = [{"value": 1.20}]

    def table_side_effect(name):
        mock_query = MagicMock()
        if name == "moves":
            # Chained: table("moves").select().eq().order().execute()
            mock_query.select.return_value = mock_query
            mock_query.eq.return_value = mock_query
            mock_query.order.return_value = mock_query
            mock_query.execute.return_value = MagicMock(data=[{"id": move_id}])
            return mock_query
        if name == "blackbox_telemetry_industrial":
            # calculate_move_cost uses: table().select().eq().execute()
            mock_query.select.return_value = mock_query
            mock_query.eq.return_value = mock_query
            mock_query.execute.return_value = mock_tokens_res
            return mock_query
        if name == "blackbox_outcomes_industrial":
            # compute_roi uses: table().select().execute()
            mock_query.select.return_value = mock_query
            mock_query.execute.return_value = mock_outcomes_res
            return mock_query
        return MagicMock()

    mock_session.table.side_effect = table_side_effect
    
    result = service.compute_roi(campaign_id)
    
    # Cost = (10000 / 1000) * 0.02 = 0.20
    # Value = 1.20
    # ROI = (1.20 - 0.20) / 0.20 = 5.0 (500%)
    
    assert result["roi"] == 5.0
    assert result["total_cost"] == 0.20
    assert result["total_value"] == 1.20

def test_attribution_models_definition():
    from backend.services.blackbox_service import AttributionModel
    assert AttributionModel.FIRST_TOUCH == "first_touch"
    assert AttributionModel.LAST_TOUCH == "last_touch"
    assert AttributionModel.LINEAR == "linear"

def test_blackbox_service_momentum_score():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    
    service = BlackboxService(vault=mock_vault)
    
    # Mock data
    def table_side_effect(name):
        mock_query = MagicMock()
        if name == "blackbox_telemetry_industrial":
            mock_query.select.return_value.execute.return_value = MagicMock(data=[{"tokens": 1000}, {"tokens": 4000}]) # 5000 total
            return mock_query
        if name == "blackbox_outcomes_industrial":
            mock_query.select.return_value.execute.return_value = MagicMock(data=[{"value": 50.0}])
            return mock_query
        return MagicMock()
        
    mock_session.table.side_effect = table_side_effect
    
    # (50.0 / 5000) * 1000 = 10.0
    score = service.calculate_momentum_score()
    assert score == 10.0

def test_blackbox_service_attribution_confidence():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    
    service = BlackboxService(vault=mock_vault)
    
    # 1. Zero traces
    with patch.object(service, "get_telemetry_by_move", return_value=[]):
        assert service.calculate_attribution_confidence("m1") == 0.0
        
    # 2. Ten traces (should be ~0.62 with the formula)
    # 0.3 + 0.65*(1/2) = 0.3 + 0.325 = 0.625 -> min(round(0.625, 2)) = 0.62 or 0.63 depending on round()
    with patch.object(service, "get_telemetry_by_move", return_value=[{"id": i} for i in range(10)]):
        conf = service.calculate_attribution_confidence("m1")
        assert conf == 0.63 or conf == 0.62 # Rounding behavior
