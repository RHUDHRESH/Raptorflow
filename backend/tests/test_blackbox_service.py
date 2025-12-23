import sys
from unittest.mock import MagicMock
import pytest

# Hierarchical mock for google.cloud.bigquery
mock_google = MagicMock()
sys.modules["google"] = mock_google
sys.modules["google.cloud"] = mock_google.cloud
sys.modules["google.cloud.bigquery"] = mock_google.cloud.bigquery

from backend.core.vault import Vault
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
    
    client = service._get_bigquery_client()
    assert client is not None
    mock_google.cloud.bigquery.Client.assert_called_once_with(project="test-project")
