from unittest.mock import MagicMock, patch
from uuid import uuid4

from models.blackbox import BlackboxOutcome
from services.outcome_ingestion_service import OutcomeIngestionService


def test_outcome_ingestion_service_webhook():
    mock_vault = MagicMock()
    mock_session = MagicMock()
    mock_vault.get_session.return_value = mock_session

    mock_query = MagicMock()
    mock_session.table.return_value = mock_query
    mock_query.insert.return_value = mock_query
    mock_query.execute.return_value = MagicMock()

    service = OutcomeIngestionService(vault=mock_vault)

    payload = {
        "tenant_id": str(uuid4()),
        "source": "stripe",
        "conversion_value": 299.0,
        "confidence": 1.0,
    }

    outcome = service.ingest_webhook_payload(payload)

    assert outcome.source == "stripe"
    assert outcome.value == 299.0
    mock_session.table.assert_called_with("blackbox_outcomes_industrial")
    mock_query.insert.assert_called_once()
