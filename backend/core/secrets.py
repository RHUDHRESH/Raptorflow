import logging
import os
from typing import Optional

from google.cloud import secretmanager

logger = logging.getLogger("raptorflow.core.secrets")


def get_secret(name: str, project_id: Optional[str] = None) -> Optional[str]:
    """
    SOTA Secret Retrieval.
    Fetches secrets from GCP Secret Manager with a fallback to local environment variables.
    Ensures industrial-grade security for credentials.
    """
    # 1. Check GCP Secret Manager
    if not project_id:
        project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")

    if project_id:
        try:
            client = secretmanager.SecretManagerServiceClient()
            secret_path = f"projects/{project_id}/secrets/{name}/versions/latest"
            response = client.access_secret_version(request={"name": secret_path})
            val = response.payload.data.decode("UTF-8")
            logger.info(f"Secret {name} successfully fetched from GCP Secret Manager.")
            return val
        except Exception as e:
            logger.debug(
                f"Secret {name} not found in GCP Secret Manager (Project: {project_id}): {e}. Falling back to ENV."
            )
    else:
        logger.debug(
            f"GCP_PROJECT_ID not set. Skipping Secret Manager for {name}. Falling back to ENV."
        )

    # 2. Fallback to Environment Variables
    return os.getenv(name)
