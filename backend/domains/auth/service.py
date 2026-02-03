"""
Auth Domain - Service
Authentication service using Supabase Auth API
"""

import logging
import os
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

from domains.auth.models import Profile, Workspace, WorkspaceMember

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication and authorization service using Supabase Auth"""

    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY", "")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self._client: Optional[Client] = None

    def _get_client(self) -> Client:
        """Get Supabase client with service role for admin operations"""
        if not self._client:
            if not self.url or not self.service_role_key:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
            self._client = create_client(self.url, self.service_role_key)
        return self._client

    def _get_anon_client(self) -> Client:
        """Get Supabase client with anon key for auth operations"""
        if not self.url or not self.anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        return create_client(self.url, self.anon_key)

    async def get_profile(self, user_id: str) -> Optional[Profile]:
        """Get profile by user ID"""
        try:
            client = self._get_client()
            result = client.table("profiles").select("*").eq("id", user_id).single().execute()
            if result.data:
                return Profile(**result.data)
            return None
        except Exception as e:
            logger.error(f"Failed to get profile: {e}")
            return None

    async def sign_up(self, email: str, password: str, user_metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Sign up new user with Supabase Auth"""
        try:
            client = self._get_anon_client()
            result = client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": user_metadata or {}}
            })
            if result.user:
                return {"success": True, "user": result.user, "session": result.session}
            return {"success": False, "error": "Signup failed"}
        except Exception as e:
            logger.error(f"Signup failed: {e}")
            return {"success": False, "error": str(e)}

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in user with Supabase Auth"""
        try:
            client = self._get_anon_client()
            result = client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if result.user and result.session:
                return {
                    "success": True,
                    "user": result.user,
                    "session": {
                        "access_token": result.session.access_token,
                        "refresh_token": result.session.refresh_token,
                        "expires_at": result.session.expires_at
                    }
                }
            return {"success": False, "error": "Invalid credentials"}
        except Exception as e:
            logger.error(f"Sign in failed: {e}")
            return {"success": False, "error": str(e)}

    async def list_user_workspaces(self, user_id: str) -> List[Workspace]:
        """Get all workspaces for a user"""
        try:
            client = self._get_client()
            workspaces = []
            owned = client.table("workspaces").select("*").eq("owner_id", user_id).execute()
            if owned.data:
                workspaces.extend([Workspace(**w) for w in owned.data])
            return workspaces
        except Exception as e:
            logger.error(f"Failed to list workspaces: {e}")
            return []


_auth_service: Optional[AuthService] = None

def get_auth_service() -> AuthService:
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
