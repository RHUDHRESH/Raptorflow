import logging
import os
from typing import Optional

from google.api_core.exceptions import NotFound
from google.cloud import secretmanager

logger = logging.getLogger("raptorflow.core.secrets")


def get_secret(name: str, project_id: Optional[str] = None) -> Optional[str]:
    """
    SOTA Secret Retrieval.
    Fetches secrets from GCP Secret Manager with a fallback to local environment variables.
    Ensures industrial-grade security for credentials.
    """
    # 1. Prefer environment variables to avoid blocking on unavailable Secret Manager access.
    env_val = os.getenv(name)
    if env_val:
        logger.debug(f"Using environment variable for {name}.")
        return env_val

    if os.getenv("DISABLE_GCP_SECRET_MANAGER", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }:
        logger.debug(
            f"Secret Manager disabled via DISABLE_GCP_SECRET_MANAGER. "
            f"Skipping Secret Manager for {name}."
        )
        return None

    # 2. Check GCP Secret Manager
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
        except PermissionError as e:
            logger.warning(f"Permission denied accessing secret {name}: {e}")
        except NotFound:
            logger.debug(f"Secret {name} not found in GCP Secret Manager.")
        except Exception as e:
            logger.warning(f"Error accessing GCP Secret Manager for {name}: {e}")
    else:
        logger.debug(
            f"GCP_PROJECT_ID not set. Skipping Secret Manager for {name}. Falling back to ENV."
        )

    # 3. Fallback to Environment Variables (in case it was set after first check)
    env_val = os.getenv(name)
    if env_val:
        logger.debug(f"Using environment variable for {name}.")
    else:
        logger.debug(f"Secret {name} not found in environment variables.")

    return env_val
