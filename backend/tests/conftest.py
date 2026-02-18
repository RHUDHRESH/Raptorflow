"""
Pytest configuration for RaptorFlow tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

vendor_path = Path(__file__).parent.parent / "vendor"
if str(vendor_path) not in sys.path:
    sys.path.insert(0, str(vendor_path))
