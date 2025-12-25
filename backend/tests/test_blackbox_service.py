import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

# Hierarchical mock for google.cloud dependencies WITHOUT breaking google.cloud namespace
if "google" not in sys.modules:
    sys.modules["google"] = MagicMock()
if "google.cloud" not in sys.modules:
    sys.modules["google.cloud"] = MagicMock()

from backend.core.vault import Vault
from backend.models.blackbox import BlackboxTelemetry
from backend.services.blackbox_service import BlackboxService


def test_blackbox_service_instantiation():
    mock_vault = MagicMock(spec=Vault)
    service = BlackboxService(vault=mock_vault)
    assert service.vault == mock_vault
    assert hasattr(service, "log_telemetry")


def test_blackbox_service_bigquery_client_initialization():
    mock_vault = MagicMock(spec=Vault)
    mock_vault.project_id = "test-project"
    service = BlackboxService(vault=mock_vault)

    from google.cloud import bigquery

    client = service._get_bigquery_client()
    assert client is not None
    bigquery.Client.assert_called_once_with(project="test-project")


def test_blackbox_service_log_telemetry_supabase():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session

    mock_query_builder = MagicMock()
    mock_session.table.return_value = mock_query_builder
    mock_query_builder.insert.return_value = mock_query_builder
    mock_query_builder.execute.return_value = MagicMock()

    service = BlackboxService(vault=mock_vault)
    telemetry = BlackboxTelemetry(
        tenant_id=uuid4(), move_id=uuid4(), agent_id="test", tokens=10
    )
    service.log_telemetry(telemetry)

    mock_session.table.assert_called_once_with("blackbox_telemetry_industrial")
    mock_query_builder.insert.assert_called_once()


def test_blackbox_service_compute_roi():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    service = BlackboxService(vault=mock_vault)

    campaign_id = uuid4()
    move_id = str(uuid4())
    tenant_id = uuid4()

    def table_side_effect(name):
        mock_query = MagicMock()
        if name == "moves":
            mock_query.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
                data=[{"id": move_id}]
            )
            return mock_query
        if name == "blackbox_telemetry_industrial":
            (
                mock_query.select.return_value.eq.return_value.eq.return_value.execute.return_value
            ) = MagicMock(data=[{"tokens": 10000}])
            return mock_query
        if name == "blackbox_outcomes_industrial":
            (
                mock_query.select.return_value.eq.return_value.eq.return_value.execute.return_value
            ) = MagicMock(data=[{"value": 1.20}])
            return mock_query
        return MagicMock()

    mock_session.table.side_effect = table_side_effect
    result = service.compute_roi(campaign_id, tenant_id)
    assert result["roi"] == 5.0


def test_blackbox_service_momentum_score():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    service = BlackboxService(vault=mock_vault)

    def table_side_effect(name):
        mock_query = MagicMock()
        if name == "blackbox_telemetry_industrial":
            mock_query.select.return_value.execute.return_value = MagicMock(
                data=[{"tokens": 5000}]
            )
            return mock_query
        if name == "blackbox_outcomes_industrial":
            mock_query.select.return_value.execute.return_value = MagicMock(
                data=[{"value": 50.0}]
            )
            return mock_query
        return MagicMock()

    mock_session.table.side_effect = table_side_effect
    assert service.calculate_momentum_score() == 10.0


def test_blackbox_service_attribution_confidence():
    mock_vault = MagicMock()
    service = BlackboxService(vault=mock_vault)
    with patch.object(
        service, "get_telemetry_by_move", return_value=[{"id": i} for i in range(10)]
    ):
        conf = service.calculate_attribution_confidence("m1", uuid4())
        assert conf == 0.63 or conf == 0.62


def test_blackbox_service_trigger_learning_cycle():
    mock_vault = MagicMock()
    service = BlackboxService(vault=mock_vault)
    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(
        return_value={"findings": ["Finding 1"], "confidence": 0.85}
    )

    with patch(
        "backend.graphs.blackbox_analysis.create_blackbox_graph",
        return_value=mock_graph,
    ):
            with patch.object(service, "upsert_learning_embedding") as mock_upsert:
                with patch.object(service, "categorize_learning", return_value="strategic"):
                    move_id = str(uuid4())
                    result = asyncio.run(
                        service.trigger_learning_cycle(move_id, uuid4())
                    )
                    assert result["findings_count"] == 1
                    mock_upsert.assert_called_once()


def test_blackbox_service_generate_pivot_recommendation():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    service = BlackboxService(vault=mock_vault)

    with patch.object(service, "get_telemetry_by_move", return_value=[{"trace": "t1"}]):
        (
            mock_session.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value
        ) = MagicMock(data=[{"value": 100}])
        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(return_value={"pivots": "New Strategy"})
        with patch(
            "backend.agents.blackbox_specialist.LearningAgent", return_value=mock_agent
        ):
            result = asyncio.run(
                service.generate_pivot_recommendation(str(uuid4()), uuid4())
            )
            assert result["pivot_recommendation"] == "New Strategy"


def test_blackbox_service_apply_learning_to_foundation():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    service = BlackboxService(vault=mock_vault)

    mock_session.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{"content": "Insight"}]
    )
    with patch(
        "backend.services.foundation_service.FoundationService.update_brand_kit",
        new_callable=AsyncMock,
    ):
        result = asyncio.run(service.apply_learning_to_foundation(uuid4(), uuid4()))
        assert result["status"] == "foundation_updated"


def test_blackbox_service_get_evidence_package():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    service = BlackboxService(vault=mock_vault)

    learning_id = uuid4()
    trace_id = str(uuid4())

    # 1. Mock learning fetch (source_ids)
    mock_learn_res = MagicMock()
    mock_learn_res.data = [{"source_ids": [trace_id]}]

    # 2. Mock telemetry fetch
    mock_tele_res = MagicMock()
    mock_tele_res.data = [{"id": trace_id, "agent_id": "a1"}]

    def table_side_effect(name):
        mock_query = MagicMock()
        if name == "blackbox_learnings_industrial":
            mock_query.select.return_value.eq.return_value.execute.return_value = (
                mock_learn_res
            )
            return mock_query
        if name == "blackbox_telemetry_industrial":
            mock_query.select.return_value.in_.return_value.execute.return_value = (
                mock_tele_res
            )
            return mock_query
        return MagicMock()

    mock_session.table.side_effect = table_side_effect

    evidence = service.get_evidence_package(learning_id)
    assert len(evidence) == 1
    assert evidence[0]["id"] == trace_id


def test_learning_flywheel_output():
    """Integration test for the entire learning flywheel data flow."""
    mock_vault = MagicMock()
    service = BlackboxService(vault=mock_vault)

    # Mocking create_blackbox_graph to return a simple flow
    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(
        return_value={
            "findings": ["Insight A", "Insight B"],
            "confidence": 0.9,
            "status": ["validated"],
        }
    )

    with patch(
        "backend.graphs.blackbox_analysis.create_blackbox_graph",
        return_value=mock_graph,
    ):
        with patch.object(service, "upsert_learning_embedding") as mock_upsert:
            with patch.object(service, "categorize_learning", return_value="strategic"):
                move_id = str(uuid4())
                asyncio.run(service.trigger_learning_cycle(move_id, uuid4()))

                # Should have upserted both findings
                assert mock_upsert.call_count == 2


def test_blackbox_service_get_learning_feed():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    service = BlackboxService(vault=mock_vault)

    mock_query_builder = MagicMock()
    mock_session.table.return_value = mock_query_builder
    mock_query_builder.select.return_value = mock_query_builder
    mock_query_builder.order.return_value = mock_query_builder
    mock_query_builder.limit.return_value = mock_query_builder

    mock_response = MagicMock()
    mock_response.data = [{"id": "l1", "content": "Insight 1"}]
    mock_query_builder.execute.return_value = mock_response

    feed = service.get_learning_feed(limit=5)

    assert len(feed) == 1
    assert feed[0]["id"] == "l1"
    mock_session.table.assert_called_with("blackbox_learnings_industrial")
    mock_query_builder.limit.assert_called_once_with(5)


def test_blackbox_service_validate_insight():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session
    service = BlackboxService(vault=mock_vault)

    mock_query_builder = MagicMock()
    mock_session.table.return_value = mock_query_builder
    mock_query_builder.update.return_value = mock_query_builder
    mock_query_builder.eq.return_value = mock_query_builder
    mock_query_builder.execute.return_value = MagicMock()

    learning_id = uuid4()
    service.validate_insight(learning_id, status="approved")

    mock_session.table.assert_called_with("blackbox_learnings_industrial")
    mock_query_builder.update.assert_called_once_with({"status": "approved"})
    mock_query_builder.eq.assert_called_once_with("id", str(learning_id))
