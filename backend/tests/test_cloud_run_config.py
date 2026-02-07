import pytest

from scripts.deploy_cloud_run import deploy_to_cloud_run


def test_deploy_command_contains_required_vars():
    """Verify that the deployment command includes essential GCP and secret configs."""
    cmd = deploy_to_cloud_run()

    assert "gcloud run deploy raptorflow-spine" in cmd
    assert "--region europe-west1" in cmd
    assert "INFERENCE_PROVIDER=google" in cmd
    assert "SUPABASE_URL=SUPABASE_URL:latest" in cmd
    assert "UPSTASH_REDIS_REST_URL=UPSTASH_REDIS_REST_URL:latest" in cmd
