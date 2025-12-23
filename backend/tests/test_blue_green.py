import yaml


def test_workflow_has_blue_green_logic():
    """Verify that backend-ci-cd.yml has blue-green deployment logic."""
    with open(".github/workflows/backend-ci-cd.yml", "r") as f:
        workflow = yaml.safe_load(f)

    steps = workflow["jobs"]["test-and-deploy"]["steps"]

    # Check if there is a 'no-traffic' or 'traffic' related step
    # or just look for the deployment command with specific flags
    found_traffic_mgmt = False
    for step in steps:
        if "deploy-cloudrun" in step.get("uses", ""):
            if step.get("with", {}).get("no_traffic") == True:
                found_traffic_mgmt = True
        if "gcloud run services update-traffic" in step.get("run", ""):
            found_traffic_mgmt = True

    assert found_traffic_mgmt
