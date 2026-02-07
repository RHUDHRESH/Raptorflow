import os
import subprocess

from core.config import get_settings


def deploy_to_cloud_run():
    """
    Deploy the RaptorFlow Agent Spine to Google Cloud Run.
    Configures environment variables and secret manager integration.
    """
    settings = get_settings()
    project_id = settings.GCP_PROJECT_ID
    region = settings.GCP_REGION
    service_name = "raptorflow-spine"

    print(f"Deploying {service_name} to {region} in project {project_id}...")

    # Construct gcloud command
    # Using --source . for automated build via Cloud Build
    command = [
        "gcloud",
        "run",
        "deploy",
        service_name,
        "--source",
        ".",
        "--region",
        region,
        "--project",
        project_id,
        "--allow-unauthenticated",  # Adjust based on auth requirements
        "--set-env-vars",
        f"GCP_PROJECT_ID={project_id},GCP_REGION={region},INFERENCE_PROVIDER=google",
        "--update-secrets",
        "SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_SERVICE_ROLE_KEY=SUPABASE_SERVICE_ROLE_KEY:latest,UPSTASH_REDIS_REST_URL=UPSTASH_REDIS_REST_URL:latest,UPSTASH_REDIS_REST_TOKEN=UPSTASH_REDIS_REST_TOKEN:latest",
    ]

    try:
        # We don't execute it here to avoid accidental spend, but provide the command
        cmd_str = " ".join(command)
        print(f"Deployment command generated:\n\n{cmd_str}\n")
        return cmd_str
    except Exception as e:
        print(f"Error preparing deployment: {e}")
        return None


if __name__ == "__main__":
    deploy_to_cloud_run()
