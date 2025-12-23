import sys
from unittest.mock import MagicMock

# Temporarily unmock for this test if it's mocked
if "pythonjsonlogger" in sys.modules:
    real_pythonjsonlogger = sys.modules.pop("pythonjsonlogger")
else:
    real_pythonjsonlogger = None

try:
    # We might not be able to import it if it's not installed in this env
    # but conftest mocks it, suggesting it might be missing or we just want to avoid it.
    # Let's assume it's installed since it's in pyproject.toml
    from pythonjsonlogger import jsonlogger
    from backend.utils.logger import RaptorFlowJSONFormatter
    
    def test_formatter_adds_severity():
        """Unit test for RaptorFlowJSONFormatter logic."""
        formatter = RaptorFlowJSONFormatter()
        log_record = {}
        record = MagicMock()
        record.levelname = "INFO"
        
        formatter.add_fields(log_record, record, {})
        
        assert "severity" in log_record
        assert log_record["severity"] == "INFO"
        assert "timestamp" in log_record

finally:
    # Restore mock
    if real_pythonjsonlogger:
        sys.modules["pythonjsonlogger"] = real_pythonjsonlogger
