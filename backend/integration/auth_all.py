"""
Authentication integration across all modules.
Injects auth context into agent state and verifies workspace access.
"""

import logging
from typing import Any, Dict, Optional

from backend.agents.state import AgentState
from backend.core.auth import get_current_user, get_workspace_id

logger = logging.getLogger(__name__)


async def inject_auth_context(
    state: AgentState, user: Dict[str, Any], workspace_id: str
) -> AgentState:
    """
    Inject authentication context into agent state.

    Args:
        state: Agent state
        user: User data from auth
        workspace_id: Workspace ID

    Returns:
        Updated agent state with auth context
    """
    try:
        # Add auth context to state
        state.update(
            {
                "user_id": user.get("id"),
                "user_email": user.get("email"),
                "user_subscription": user.get("subscription_tier", "free"),
                "workspace_id": workspace_id,
                "authenticated": True,
                "auth_timestamp": user.get("created_at"),
                "permissions": _get_user_permissions(user),
            }
        )

        logger.info(
            f"Injected auth context for user {user.get('id')} in workspace {workspace_id}"
        )

        return state

    except Exception as e:
        logger.error(f"Error injecting auth context: {e}")
        state["authenticated"] = False
        state["auth_error"] = str(e)
        return state


def _get_user_permissions(user: Dict[str, Any]) -> Dict[str, bool]:
    """
    Get user permissions based on subscription tier.

    Args:
        user: User data

    Returns:
        Permission dictionary
    """
    subscription = user.get("subscription_tier", "free")

    permissions = {
        "read": True,  # All users can read
        "write": subscription in ["starter", "pro", "enterprise"],
        "delete": subscription in ["pro", "enterprise"],
        "admin": subscription == "enterprise",
        "ai_features": subscription in ["starter", "pro", "enterprise"],
        "advanced_analytics": subscription in ["pro", "enterprise"],
        "api_access": subscription in ["pro", "enterprise"],
        "bulk_operations": subscription == "enterprise",
    }

    return permissions


async def verify_workspace_access(
    workspace_id: str, user: Dict[str, Any], db_client
) -> bool:
    """
    Verify user has access to workspace.

    Args:
        workspace_id: Workspace ID to check
        user: User data
        db_client: Database client

    Returns:
        Access permission status
    """
    try:
        # Check if workspace exists and user is member
        result = (
            db_client.table("workspaces").select("*").eq("id", workspace_id).execute()
        )

        if not result.data:
            logger.warning(f"Workspace {workspace_id} not found")
            return False

        workspace = result.data[0]

        # Check if user owns the workspace
        if workspace["user_id"] == user.get("id"):
            logger.info(f"User {user.get('id')} is owner of workspace {workspace_id}")
            return True

        # TODO: Check for team members when team functionality is added
        logger.warning(
            f"User {user.get('id')} is not member of workspace {workspace_id}"
        )
        return False

    except Exception as e:
        logger.error(f"Error verifying workspace access: {e}")
        return False


async def check_subscription_limits(
    user: Dict[str, Any], action: str, current_count: int = 0
) -> Dict[str, Any]:
    """
    Check if user's subscription allows the action.

    Args:
        user: User data
        action: Action being performed
        current_count: Current count of items

    Returns:
        Limit check result
    """
    try:
        subscription = user.get("subscription_tier", "free")

        # Define limits per subscription tier
        limits = {
            "free": {
                "icps": 3,
                "moves": 5,
                "campaigns": 2,
                "ai_requests": 100,
                "storage_mb": 100,
            },
            "starter": {
                "icps": 10,
                "moves": 20,
                "campaigns": 10,
                "ai_requests": 1000,
                "storage_mb": 1024,
            },
            "pro": {
                "icps": 50,
                "moves": 100,
                "campaigns": 50,
                "ai_requests": 10000,
                "storage_mb": 10240,
            },
            "enterprise": {
                "icps": -1,  # Unlimited
                "moves": -1,
                "campaigns": -1,
                "ai_requests": -1,
                "storage_mb": -1,
            },
        }

        tier_limits = limits.get(subscription, limits["free"])
        limit = tier_limits.get(action, 0)

        # Check if unlimited
        if limit == -1:
            return {
                "allowed": True,
                "limit": "unlimited",
                "current": current_count,
                "remaining": "unlimited",
            }

        # Check if under limit
        allowed = current_count < limit
        remaining = max(0, limit - current_count)

        return {
            "allowed": allowed,
            "limit": limit,
            "current": current_count,
            "remaining": remaining,
            "subscription": subscription,
        }

    except Exception as e:
        logger.error(f"Error checking subscription limits: {e}")
        return {"allowed": False, "error": str(e)}


class AuthContextManager:
    """
    Manages authentication context across the system.
    """

    def __init__(self, db_client):
        self.db_client = db_client
        self.active_sessions = {}

    async def create_auth_context(
        self, request, workspace_id: str = None
    ) -> Dict[str, Any]:
        """
        Create authentication context from request.

        Args:
            request: FastAPI request
            workspace_id: Optional workspace ID

        Returns:
            Authentication context
        """
        try:
            # Get current user
            user = await get_current_user(request)

            if not user:
                return {"authenticated": False, "error": "User not authenticated"}

            # Get workspace ID
            if not workspace_id:
                workspace_id = await get_workspace_id(
                    user, request.headers.get("workspace-id")
                )

            # Verify workspace access
            has_access = await verify_workspace_access(
                workspace_id, user, self.db_client
            )

            if not has_access:
                return {"authenticated": False, "error": "Workspace access denied"}

            # Get subscription limits
            # This would typically come from a billing service
            subscription_info = {
                "tier": user.get("subscription_tier", "free"),
                "limits": await check_subscription_limits(user, "icps", 0),
            }

            context = {
                "authenticated": True,
                "user": user,
                "workspace_id": workspace_id,
                "subscription": subscription_info,
                "permissions": _get_user_permissions(user),
                "timestamp": time.time(),
            }

            # Store in active sessions
            session_id = f"{user.get('id')}_{workspace_id}"
            self.active_sessions[session_id] = context

            return context

        except Exception as e:
            logger.error(f"Error creating auth context: {e}")
            return {"authenticated": False, "error": str(e)}

    async def get_auth_context(
        self, user_id: str, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get existing authentication context.

        Args:
            user_id: User ID
            workspace_id: Workspace ID

        Returns:
            Authentication context or None
        """
        session_id = f"{user_id}_{workspace_id}"
        return self.active_sessions.get(session_id)

    async def invalidate_auth_context(self, user_id: str, workspace_id: str):
        """
        Invalidate authentication context.

        Args:
            user_id: User ID
            workspace_id: Workspace ID
        """
        session_id = f"{user_id}_{workspace_id}"
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Invalidated auth context for {user_id} in {workspace_id}")

    async def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """
        Clean up expired authentication sessions.

        Args:
            max_age_hours: Maximum age in hours
        """
        current_time = time.time()
        expired_sessions = []

        for session_id, context in self.active_sessions.items():
            age_hours = (current_time - context["timestamp"]) / 3600
            if age_hours > max_age_hours:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.active_sessions[session_id]

        logger.info(f"Cleaned up {len(expired_sessions)} expired auth sessions")
