"""
Supabase client singleton
Manages database connections with proper configuration
"""

import os
from typing import Optional

from dotenv import load_dotenv

from supabase import Client, create_client

# Load environment variables
load_dotenv()


class SupabaseClient:
    """Singleton Supabase client manager"""

    _instance: Optional["SupabaseClient"] = None
    _client: Optional[Client] = None
    _admin_client: Optional[Client] = None

    def __new__(cls) -> "SupabaseClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._initialize_clients()

    def _initialize_clients(self):
        """Initialize Supabase clients"""
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not self.url or not self.anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

        # Anonymous client (for user operations)
        self._client = create_client(self.url, self.anon_key)

        # Admin client (for system operations)
        if self.service_key:
            self._admin_client = create_client(self.url, self.service_key)

    @property
    def client(self) -> Client:
        """Get the anonymous client"""
        if self._client is None:
            raise RuntimeError("Supabase client not initialized")
        return self._client

    @property
    def admin(self) -> Client:
        """Get the admin client (service role)"""
        if self._admin_client is None:
            raise RuntimeError(
                "Supabase admin client not available - set SUPABASE_SERVICE_ROLE_KEY"
            )
        return self._admin_client

    def get_client(self, use_admin: bool = False) -> Client:
        """Get client with option for admin access"""
        if use_admin:
            return self.admin
        return self.client

    def get_admin_client(self) -> Client:
        """Get the admin client (service role)"""
        return self.admin

    def health_check(self) -> bool:
        """Check if Supabase is accessible"""
        try:
            result = self.client.table("users").select("count", count="exact").execute()
            return hasattr(result, "data")
        except Exception:
            return False


# Global instance
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> Client:
    """Get Supabase client (singleton pattern)"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client.client


def get_supabase_admin() -> Client:
    """Get Supabase admin client"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client.admin
