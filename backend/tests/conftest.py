import sys
from unittest.mock import MagicMock

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

# Mock pythonjsonlogger
sys.modules["pythonjsonlogger"] = MagicMock()
