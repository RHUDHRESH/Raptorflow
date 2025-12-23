from google.cloud import secretmanager
from backend.core.config import get_settings
from functools import lru_cache

class Vault:
    """
    Interface for GCP Secret Manager.
    """
    def __init__(self):
        self.settings = get_settings()
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = self.settings.GCP_PROJECT_ID

    @lru_cache(maxsize=128)
    def get_secret(self, secret_id: str, version_id: str = "latest") -> str:
        """
        Access the payload for the given secret version if one exists.
        """
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
        
        try:
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            # Fallback to env if secret manager fails or secret not found
            # This is useful for local development
            import os
            val = os.getenv(secret_id)
            if val:
                return val
            raise e

_vault = None

def get_vault() -> Vault:
    global _vault
    if _vault is None:
        _vault = Vault()
    return _vault