"""
Audit Log Service

Canonical service for writing structured audit events to the audit_logs table.
Provides helpers for system events and future LangGraph tool-call logging.
"""

import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from backend.services.supabase_client import supabase_client
from backend.utils.logging_config import get_logger, get_correlation_id

logger = get_logger("audit")

# ============================================================================
# EVENT TYPE CONSTANTS
# ============================================================================

# System events
EVENT_USER_LOGIN = "user.login"
EVENT_USER_LOGOUT = "user.logout"
EVENT_WORKSPACE_CREATED = "workspace.created"
EVENT_WORKSPACE_DELETED = "workspace.deleted"
EVENT_AGENT_SEEDED = "agent.seeded"
EVENT_PERMISSION_GRANTED = "permission.granted"
EVENT_PERMISSION_REVOKED = "permission.revoked"

# Tool-related events (future LangGraph integration)
EVENT_TOOL_CALLED = "tool.called"
EVENT_TOOL_COMPLETED = "tool.completed"
EVENT_TOOL_FAILED = "tool.failed"


@dataclass
class AuditEvent:
    """Internal representation of an audit event."""
    workspace_id: str
    event_type: str
    actor_user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AuditLogService:
    """
    Canonical audit logging service.

    Features:
    - Structured event writing to audit_logs table
    - Automatic correlation ID inclusion
    - Helper functions for common event types
    - Future-ready for LangGraph tool-call logging
    """

    def __init__(self):
        self.supabase = supabase_client

    async def log_event(
        self,
        workspace_id: str,
        event_type: str,
        actor_user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a structured audit event to the audit_logs table.

        Args:
            workspace_id: Target workspace
            event_type: Type of event (e.g., "user.login", "tool.called")
            actor_user_id: User who triggered the event (optional)
            metadata: Additional JSON-serializable metadata
        """
        try:
            # Get correlation ID from context
            correlation_id = get_correlation_id()

            # Prepare metadata with correlation ID
            event_metadata = metadata or {}
            if correlation_id:
                event_metadata["correlation_id"] = correlation_id

            # Prepare DB record
            audit_data = {
                "workspace_id": workspace_id,
                "actor_user_id": actor_user_id,
                "event_type": event_type,
                "metadata": json.dumps(event_metadata),
            }

            # Insert into audit_logs table
            result = await self.supabase.insert("audit_logs", audit_data)

            # Log the event (redundant logging for observability)
            logger.info(
                "Audit event logged",
                workspace_id=workspace_id,
                event_type=event_type,
                actor_user_id=actor_user_id,
                metadata_keys=list(event_metadata.keys()) if event_metadata else [],
            )

        except Exception as e:
            logger.error(
                "Failed to log audit event",
                workspace_id=workspace_id,
                event_type=event_type,
                error=str(e),
            )
            # Don't crash business logic for audit logging failures

    # ============================================================================
    # SYSTEM EVENT HELPERS
    # ============================================================================

    async def log_user_login(self, workspace_id: str, user_id: str, login_method: str = "web") -> None:
        """Log a user login event."""
        await self.log_event(
            workspace_id=workspace_id,
            event_type=EVENT_USER_LOGIN,
            actor_user_id=user_id,
            metadata={"login_method": login_method},
        )

    async def log_user_logout(self, workspace_id: str, user_id: str, logout_type: str = "normal") -> None:
        """Log a user logout event."""
        await self.log_event(
            workspace_id=workspace_id,
            event_type=EVENT_USER_LOGOUT,
            actor_user_id=user_id,
            metadata={"logout_type": logout_type},
        )

    async def log_workspace_created(self, workspace_id: str, creator_user_id: str, workspace_name: str) -> None:
        """Log workspace creation."""
        await self.log_event(
            workspace_id=workspace_id,
            event_type=EVENT_WORKSPACE_CREATED,
            actor_user_id=creator_user_id,
            metadata={"workspace_name": workspace_name},
        )

    async def log_workspace_deleted(self, workspace_id: str, deleter_user_id: str, workspace_name: str) -> None:
        """Log workspace deletion."""
        await self.log_event(
            workspace_id=workspace_id,
            event_type=EVENT_WORKSPACE_DELETED,
            actor_user_id=deleter_user_id,
            metadata={"workspace_name": workspace_name},
        )

    async def log_agents_seeded(self, workspace_id: str, seeder_user_id: str, agent_count: int) -> None:
        """Log agent seeding event."""
        await self.log_event(
            workspace_id=workspace_id,
            event_type=EVENT_AGENT_SEEDED,
            actor_user_id=seeder_user_id,
            metadata={"agents_created": agent_count},
        )

    async def log_permission_change(
        self,
        workspace_id: str,
        target_user_id: str,
        changer_user_id: str,
        permission: str,
        action: str,  # "granted" or "revoked"
        old_role: Optional[str] = None,
        new_role: Optional[str] = None,
    ) -> None:
        """Log permission changes."""
        event_type = EVENT_PERMISSION_GRANTED if action == "granted" else EVENT_PERMISSION_REVOKED

        await self.log_event(
            workspace_id=workspace_id,
            event_type=event_type,
            actor_user_id=changer_user_id,
            metadata={
                "target_user_id": target_user_id,
                "permission": permission,
                "old_role": old_role,
                "new_role": new_role,
            },
        )

    # ============================================================================
    # TOOL-CALL LOGGING (FOR FUTURE LANGGRAPH INTEGRATION)
    # ============================================================================

    async def log_tool_call(
        self,
        workspace_id: str,
        tool_name: str,
        agent_id: str,
        parameters: Dict[str, Any],
        call_duration_ms: Optional[float] = None,
    ) -> None:
        """
        Log a tool call initiation (for future LangGraph tools).

        Args:
            workspace_id: Target workspace
            tool_name: Name of the tool being called
            agent_id: Agent initiating the call
            parameters: Tool parameters (sanitized for logging)
            call_duration_ms: Expected/estimated duration if known
        """
        await self.log_event(
            workspace_id=workspace_id,
            event_type=EVENT_TOOL_CALLED,
            metadata={
                "tool_name": tool_name,
                "agent_id": agent_id,
                "parameters": parameters,  # Sanitize in production
                "call_duration_ms": call_duration_ms,
            },
        )

    async def log_tool_completion(
        self,
        workspace_id: str,
        tool_name: str,
        agent_id: str,
        result_summary: str,
        success: bool = True,
        execution_duration_ms: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Log a tool call completion (for future LangGraph tools).

        Args:
            workspace_id: Target workspace
            tool_name: Name of the completed tool
            agent_id: Agent that called the tool
            result_summary: Brief description of result
            success: Whether the tool call succeeded
            execution_duration_ms: Actual execution time
            error_message: Error details if failed
        """
        await self.log_event(
            workspace_id=workspace_id,
            event_type=EVENT_TOOL_COMPLETED if success else EVENT_TOOL_FAILED,
            metadata={
                "tool_name": tool_name,
                "agent_id": agent_id,
                "result_summary": result_summary,
                "execution_duration_ms": execution_duration_ms,
                "error_message": error_message,  # Sanitized error details
            },
        )


# Global service instance
audit_log = AuditLogService()

# ============================================================================
# CONVENIENCE FUNCTIONS FOR EASY IMPORT
# ============================================================================

# Core event logging
log_event = audit_log.log_event

# System events
log_user_login = audit_log.log_user_login
log_user_logout = audit_log.log_user_logout
log_workspace_created = audit_log.log_workspace_created
log_workspace_deleted = audit_log.log_workspace_deleted
log_agents_seeded = audit_log.log_agents_seeded
log_permission_change = audit_log.log_permission_change

# Tool events (future LangGraph ready)
log_tool_call = audit_log.log_tool_call
log_tool_completion = audit_log.log_tool_completion
