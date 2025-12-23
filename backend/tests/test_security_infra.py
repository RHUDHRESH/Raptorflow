import os


def test_cloud_armor_script_exists():
    """Verify that the Cloud Armor setup script exists."""
    assert os.path.exists("backend/scripts/setup_cloud_armor.py")


def test_deployment_md_security_updates():
    """Verify that DEPLOYMENT.md contains Cloud Armor and IAM pruning info."""
    with open("backend/DEPLOYMENT.md", "r") as f:
        content = f.read()

    assert "Cloud Armor" in content
    assert "IAM Role Pruning" in content
