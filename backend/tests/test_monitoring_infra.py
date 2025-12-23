import os


def test_monitoring_script_exists():
    """Verify that the Monitoring setup script exists."""
    assert os.path.exists("backend/scripts/setup_monitoring.py")
