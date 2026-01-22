"""
Production-ready audit logging for RaptorFlow
Tracks all user actions for security and compliance
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .supabase_mgr import get_supabase_client

logger = logging.getLogger(__name__)


@dataclass
class AuditEvent:
    """Audit event data structure"""

    user_id: Optional[str]
    workspace_id: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data["created_at"] = datetime.now(timezone.utc).isoformat()
        return data


class AuditLogger:
    """Production-ready audit logging system"""

    def __init__(self):
        self.supabase = get_supabase_client()

    async def log_action(
        self,
        user_id: Optional[str],
        workspace_id: Optional[str],
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Dict[str, Any] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Log an audit event

        Args:
            user_id: User ID performing the action
            workspace_id: Workspace ID context
            action: Action performed (create, read, update, delete, login, etc.)
            resource_type: Type of resource (user, workspace, foundation, etc.)
            resource_id: ID of the resource
            details: Additional details about the action
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether the action was successful
            error_message: Error message if action failed

        Returns:
            True if logged successfully, False otherwise
        """
        try:
            event = AuditEvent(
                user_id=user_id,
                workspace_id=workspace_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                error_message=error_message,
            )

            # Store in database
            result = self.supabase.table("audit_logs").insert(event.to_dict()).execute()

            if result.data:
                logger.info(
                    f"Audit event logged: {action} on {resource_type} by user {user_id}"
                )
                return True
            else:
                logger.error("Failed to log audit event: No data returned")
                return False

        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            return False

    async def log_authentication(
        self,
        user_id: str,
        action: str,  # login, logout, failed_login, token_refresh
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Log authentication events

        Args:
            user_id: User ID
            action: Authentication action
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether authentication was successful
            error_message: Error message if failed

        Returns:
            True if logged successfully, False otherwise
        """
        return await self.log_action(
            user_id=user_id,
            workspace_id=None,
            action=action,
            resource_type="authentication",
            resource_id=None,
            details={"auth_action": action},
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
        )

    async def log_workspace_access(
        self,
        user_id: str,
        workspace_id: str,
        action: str,  # access, switch, create, delete
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Log workspace access events

        Args:
            user_id: User ID
            workspace_id: Workspace ID
            action: Workspace action
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether action was successful
            error_message: Error message if failed

        Returns:
            True if logged successfully, False otherwise
        """
        return await self.log_action(
            user_id=user_id,
            workspace_id=workspace_id,
            action=action,
            resource_type="workspace",
            resource_id=workspace_id,
            details={"workspace_action": action},
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
        )

    async def log_data_access(
        self,
        user_id: str,
        workspace_id: str,
        resource_type: str,
        resource_id: Optional[str],
        action: str,  # create, read, update, delete
        details: Dict[str, Any] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Log data access events

        Args:
            user_id: User ID
            workspace_id: Workspace ID
            resource_type: Type of resource accessed
            resource_id: ID of the resource
            action: Data action performed
            details: Additional details
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether action was successful
            error_message: Error message if failed

        Returns:
            True if logged successfully, False otherwise
        """
        return await self.log_action(
            user_id=user_id,
            workspace_id=workspace_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {"data_action": action},
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
        )

    async def get_user_audit_trail(
        self,
        user_id: str,
        workspace_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Dict[str, Any]]:
        """
        Get audit trail for a specific user

        Args:
            user_id: User ID
            workspace_id: Optional workspace filter
            limit: Maximum number of records
            offset: Offset for pagination

        Returns:
            List of audit events
        """
        try:
            query = self.supabase.table("audit_logs").select("*").eq("user_id", user_id)

            if workspace_id:
                query = query.eq("workspace_id", workspace_id)

            result = (
                query.order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return result.data or []

        except Exception as e:
            logger.error(f"Error getting user audit trail: {e}")
            return []

    async def get_workspace_audit_trail(
        self, workspace_id: str, limit: int = 100, offset: int = 0
    ) -> list[Dict[str, Any]]:
        """
        Get audit trail for a specific workspace

        Args:
            workspace_id: Workspace ID
            limit: Maximum number of records
            offset: Offset for pagination

        Returns:
            List of audit events
        """
        try:
            result = (
                self.supabase.table("audit_logs")
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return result.data or []

        except Exception as e:
            logger.error(f"Error getting workspace audit trail: {e}")
            return []


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger singleton"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


# Convenience functions
async def log_action(
    user_id: Optional[str],
    workspace_id: Optional[str],
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Dict[str, Any] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None,
) -> bool:
    """Log an audit action"""
    return await get_audit_logger().log_action(
        user_id,
        workspace_id,
        action,
        resource_type,
        resource_id,
        details,
        ip_address,
        user_agent,
        success,
        error_message,
    )


async def log_authentication(
    user_id: str,
    action: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None,
) -> bool:
    """Log authentication event"""
    return await get_audit_logger().log_authentication(
        user_id, action, ip_address, user_agent, success, error_message
    )
