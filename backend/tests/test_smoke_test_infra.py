import os

def test_smoke_test_script_exists():
    """Verify that the Smoke Test script exists."""
    assert os.path.exists("backend/scripts/smoke_test_prod.py")
