import os
from typing import Optional
from supabase import create_client, Client
from google.cloud import secretmanager


class Vault:
    """
    The Vault is the secure gateway for RaptorFlow, managing
    connections to Supabase and GCP Secret Manager.
    """

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.client: Optional[Client] = None
        self._secret_client = None
        self.project_id = os.getenv("GCP_PROJECT_ID")

    def _get_secret_client(self):
        if not self._secret_client:
            self._secret_client = secretmanager.SecretManagerServiceClient()
        return self._secret_client

    async def initialize(self):
        """Initializes the Supabase client."""
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set.")
        # create_client in supabase-py is synchronous but works with async code
        self.client = create_client(self.supabase_url, self.supabase_key)

    async def get_session(self) -> Client:
        """Returns the active Supabase client session."""
        if not self.client:
            await self.initialize()
        return self.client

    async def get_secret(self, secret_id: str, version_id: str = "latest") -> str:
        """Retrieves a secret from GCP Secret Manager."""
        try:
            name = (
                f"projects/{self.project_id}/secrets/{secret_id}/"
                f"versions/{version_id}"
            )
            sc = self._get_secret_client()
            response = sc.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve secret {secret_id}: {str(e)}")

    async def health_check(self) -> dict:
        """Verifies connectivity to core services."""
        status = {"supabase": "healthy", "gcp_secrets": "healthy"}

        try:
            # Check Supabase
            client = await self.get_session()
            await client.table("foundation_brand_kit").select(
                "id", count="exact"
            ).limit(1).execute()
        except Exception as e:
            status["supabase"] = f"unhealthy: {str(e)}"

        try:
            # Check GCP Secrets
            sc = self._get_secret_client()
            sc.list_secrets(request={"parent": f"projects/{self.project_id}"})
        except Exception as e:
            status["gcp_secrets"] = f"unhealthy: {str(e)}"

        return status
