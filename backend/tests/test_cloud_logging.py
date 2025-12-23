import importlib
import sys
from unittest.mock import MagicMock


def test_formatter_adds_severity():
    """Unit test for RaptorFlowJSONFormatter logic."""
    # Temporarily unmock for this test if it's mocked in sys.modules
    # This prevents RaptorFlowJSONFormatter (which inherits from JsonFormatter)
    # from inheriting from a MagicMock during test execution.

    mocked_lib = sys.modules.get("pythonjsonlogger")
    if mocked_lib:
        del sys.modules["pythonjsonlogger"]

    try:
        # Import inside the test to ensure it uses the real lib
        import backend.utils.logger

        importlib.reload(backend.utils.logger)

        formatter = backend.utils.logger.RaptorFlowJSONFormatter()
        log_record = {}
        record = MagicMock()
        record.levelname = "INFO"

        formatter.add_fields(log_record, record, {})

        assert "severity" in log_record
        assert log_record["severity"] == "INFO"
        assert "timestamp" in log_record

    finally:
        # Restore mock if it was there
        if mocked_lib:
            sys.modules["pythonjsonlogger"] = mocked_lib
            import backend.utils.logger
            importlib.reload(backend.utils.logger)