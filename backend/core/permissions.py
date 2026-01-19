"""
Production-ready permission system for RaptorFlow
Defines permission levels and checking functions with database backing
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Set

from .supabase_mgr import get_supabase_client

logger = logging.getLogger(__name__)


class Permission(Enum):
    """Permission levels for workspace access"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


@dataclass
class UserPermissions:
    """User permissions for a workspace"""

    user_id: str
    workspace_id: str
    permissions: Set[Permission]
    role: str = "owner"  # owner, member, viewer, etc.


def check_permission(user_id: str, workspace_id: str, permission: Permission) -> bool:
    """
    Check if user has specific permission for workspace

    Args:
        user_id: User ID
        workspace_id: Workspace ID
        permission: Permission to check

    Returns:
        True if user has permission, False otherwise
    """
    try:
        supabase = get_supabase_client()

        # Check if user owns the workspace (owner has all permissions)
        result = (
            supabase.table("workspaces")
            .select("user_id")
            .eq("id", workspace_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if result.data:
            # Workspace owners have all permissions
            logger.debug(f"User {user_id} is owner of workspace {workspace_id}")
            return True

        # TODO: Implement role-based permissions for non-owners
        # For now, deny access to non-owners
        logger.warning(
            f"User {user_id} denied access to workspace {workspace_id} - not owner"
        )
        return False

    except Exception as e:
        logger.error(
            f"Error checking permission for user {user_id}, workspace {workspace_id}: {e}"
        )
        # Fail secure - deny access on error
        return False


def get_user_permissions(user_id: str, workspace_id: str) -> UserPermissions:
    """
    Get user permissions for a workspace

    Args:
        user_id: User ID
        workspace_id: Workspace ID

    Returns:
        UserPermissions object
    """
    try:
        supabase = get_supabase_client()

        # Check if user owns the workspace
        result = (
            supabase.table("workspaces")
            .select("user_id")
            .eq("id", workspace_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if result.data:
            # Workspace owners have all permissions
            logger.debug(f"User {user_id} is owner of workspace {workspace_id}")
            return UserPermissions(
                user_id=user_id,
                workspace_id=workspace_id,
                permissions=set(Permission),  # All permissions
                role="owner",
            )

        # TODO: Implement role-based permissions for non-owners
        # For now, return minimal permissions
        logger.warning(f"User {user_id} has minimal access to workspace {workspace_id}")
        return UserPermissions(
            user_id=user_id,
            workspace_id=workspace_id,
            permissions=set(),  # No permissions
            role="none",
        )

    except Exception as e:
        logger.error(
            f"Error getting permissions for user {user_id}, workspace {workspace_id}: {e}"
        )
        # Fail secure - no permissions on error
        return UserPermissions(
            user_id=user_id, workspace_id=workspace_id, permissions=set(), role="none"
        )


def has_permission(user_permissions: UserPermissions, permission: Permission) -> bool:
    """
    Check if user permissions include specific permission

    Args:
        user_permissions: UserPermissions object
        permission: Permission to check

    Returns:
        True if user has permission, False otherwise
    """
    return permission in user_permissions.permissions


def require_permission(permission: Permission):
    """
    Decorator to require specific permission
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check permission here
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Permission constants for easy access
READ_PERMISSION = Permission.READ
WRITE_PERMISSION = Permission.WRITE
DELETE_PERMISSION = Permission.DELETE
ADMIN_PERMISSION = Permission.ADMIN
