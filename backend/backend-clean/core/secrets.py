import logging
import os
from typing import Optional

# Import secretmanager only if available
try:
    from google.api_core.exceptions import NotFound
    from google.cloud import secretmanager

    SECRET_MANAGER_AVAILABLE = True
except ImportError:
    SECRET_MANAGER_AVAILABLE = False
    NotFound = Exception
    secretmanager = None

logger = logging.getLogger("raptorflow.core.secrets")


def get_secret(name: str, project_id: Optional[str] = None) -> Optional[str]:
    """
    Retrieve a secret from GCP Secret Manager or environment variables.
    Falls back to environment variable if Secret Manager is not available.
    """
    # First try environment variable
    env_value = os.environ.get(name)
    if env_value:
        return env_value

    # Try GCP Secret Manager
    if SECRET_MANAGER_AVAILABLE and secretmanager:
        try:
            if project_id is None:
                project_id = os.environ.get("GCP_PROJECT_ID", "raptorflow-481505")

            client = secretmanager.SecretManagerServiceClient()
            secret_path = f"projects/{project_id}/secrets/{name}/versions/latest"

            response = client.access_secret_version(request={"name": secret_path})
            secret_value = response.payload.data.decode("UTF-8")
            logger.info(f"Secret {name} successfully fetched from GCP Secret Manager.")
            return secret_value
        except NotFound:
            logger.warning(f"Secret {name} not found in GCP Secret Manager.")
            return None
        except Exception as e:
            logger.error(f"Error accessing GCP Secret Manager for {name}: {e}")
            return None

    return None
