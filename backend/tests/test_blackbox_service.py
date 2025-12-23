import pytest
from unittest.mock import MagicMock
from backend.core.vault import Vault
# This will fail (Red Phase)
try:
    from backend.services.blackbox_service import BlackboxService
except ImportError:
    BlackboxService = None

def test_blackbox_service_instantiation():
    if BlackboxService is None:
        pytest.fail("BlackboxService not found")
    
    mock_vault = MagicMock(spec=Vault)
    service = BlackboxService(vault=mock_vault)
    assert service.vault == mock_vault
    assert hasattr(service, "log_telemetry")
