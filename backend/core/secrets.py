import os
import logging
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
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        
    if project_id:
        try:
            client = secretmanager.SecretManagerServiceClient()
            secret_path = f"projects/{project_id}/secrets/{name}/versions/latest"
            response = client.access_secret_version(request={"name": secret_path})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.debug(f"Secret {name} not found in GCP Secret Manager: {e}. Falling back to ENV.")
            
    # 2. Fallback to Environment Variables
    return os.getenv(name)
