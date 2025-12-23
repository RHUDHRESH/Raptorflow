import os

import yaml


def test_service_yaml_exists():
    """Verify that service.yaml exists in the backend directory."""
    assert os.path.exists("backend/service.yaml")


def test_service_yaml_structure():
    """Verify that service.yaml has the required Cloud Run structure."""
    with open("backend/service.yaml", "r") as f:
        data = yaml.safe_load(f)

    assert data["apiVersion"] == "serving.knative.dev/v1"
    assert data["kind"] == "Service"
    assert "metadata" in data
    assert "spec" in data

    # Check for memory/CPU limits as per Phase 106
    container = data["spec"]["template"]["spec"]["containers"][0]
    resources = container["resources"]["limits"]
    assert "memory" in resources
    assert "cpu" in resources

    # Check for VPC connector as per Phase 106
    annotations = data["spec"]["template"]["metadata"]["annotations"]
    assert "run.googleapis.com/vpc-access-connector" in annotations
