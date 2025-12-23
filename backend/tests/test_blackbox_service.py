import pytest
from unittest.mock import MagicMock
from backend.core.vault import Vault
from backend.services.blackbox_service import BlackboxService

def test_blackbox_service_instantiation():
    mock_vault = MagicMock(spec=Vault)
    service = BlackboxService(vault=mock_vault)
    assert service.vault == mock_vault
    assert hasattr(service, "log_telemetry")
