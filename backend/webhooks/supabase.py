"""
Supabase webhook handlers for Raptorflow.

Handles Supabase authentication and database events
with proper event processing and error handling.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from handler import WebhookHandler, get_webhook_handler
from infrastructure.cloud_monitoring import get_cloud_monitoring
from infrastructure.logging import get_cloud_logging

from .models import WebhookEvent, WebhookResponse

logger = logging.getLogger(__name__)


@dataclass
class SupabaseAuthEvent:
    """Supabase authentication event data."""

    user_id: str
    email: str
    event_type: str
    timestamp: datetime
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class SupabaseDatabaseEvent:
    """Supabase database event data."""

    table: str
    record: Dict[str, Any]
    old_record: Optional[Dict[str, Any]]
    event_type: str
    timestamp: datetime
    schema: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "table": self.table,
            "record": self.record,
            "old_record": self.old_record,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "schema": self.schema,
        }


class SupabaseWebhookHandler:
    """Supabase webhook event handler."""

    def __init__(self):
        self.logger = logging.getLogger("supabase_webhook_handler")
        self.logging = get_cloud_logging()
        self.monitoring = get_cloud_monitoring()

        # Register handlers with main webhook handler
        self._register_handlers()

    def _register_handlers(self):
        """Register Supabase event handlers."""
        webhook_handler = get_webhook_handler()

        # Authentication events
        webhook_handler.register_handler("supabase.auth.signup", self.handle_signup)
        webhook_handler.register_handler("supabase.auth.login", self.handle_login)
        webhook_handler.register_handler("supabase.auth.logout", self.handle_logout)
        webhook_handler.register_handler(
            "supabase.auth.password_recovery", self.handle_password_recovery
        )
        webhook_handler.register_handler(
            "supabase.auth.user_updated", self.handle_user_updated
        )
        webhook_handler.register_handler(
            "supabase.auth.user_deleted", self.handle_user_deleted
        )

        # Database events
        webhook_handler.register_handler("supabase.database.insert", self.handle_insert)
        webhook_handler.register_handler("supabase.database.update", self.handle_update)
        webhook_handler.register_handler("supabase.database.delete", self.handle_delete)

        # Storage events
        webhook_handler.register_handler(
            "supabase.storage.created", self.handle_storage_created
        )
        webhook_handler.register_handler(
            "supabase.storage.updated", self.handle_storage_updated
        )
        webhook_handler.register_handler(
            "supabase.storage.deleted", self.handle_storage_deleted
        )

    async def handle_auth_event(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle Supabase authentication event."""
        try:
            # Parse auth event
            auth_event = self._parse_auth_event(event.data)

            # Log event
            await self.logging.log_structured(
                "INFO",
                f"Supabase auth event: {auth_event.event_type}",
                {
                    "user_id": auth_event.user_id,
                    "email": auth_event.email,
                    "event_type": auth_event.event_type,
                    "timestamp": auth_event.timestamp.isoformat(),
                },
            )

            # Process event based on type
            if auth_event.event_type == "signup":
                return await self.handle_signup(event)
            elif auth_event.event_type == "login":
                return await self.handle_login(event)
            elif auth_event.event_type == "logout":
                return await self.handle_logout(event)
            elif auth_event.event_type == "password_recovery":
                return await self.handle_password_recovery(event)
            elif auth_event.event_type == "user_updated":
                return await self.handle_user_updated(event)
            elif auth_event.event_type == "user_deleted":
                return await self.handle_user_deleted(event)
            else:
                self.logger.warning(f"Unknown auth event type: {auth_event.event_type}")
                return {"status": "unknown_event", "event_type": auth_event.event_type}

        except Exception as e:
            self.logger.error(f"Failed to handle Supabase auth event: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_database_event(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle Supabase database event."""
        try:
            # Parse database event
            db_event = self._parse_database_event(event.data)

            # Log event
            await self.logging.log_structured(
                "INFO",
                f"Supabase database event: {db_event.event_type}",
                {
                    "table": db_event.table,
                    "schema": db_event.schema,
                    "event_type": db_event.event_type,
                    "timestamp": db_event.timestamp.isoformat(),
                },
            )

            # Process event based on type
            if db_event.event_type == "INSERT":
                return await self.handle_insert(event)
            elif db_event.event_type == "UPDATE":
                return await self.handle_update(event)
            elif db_event.event_type == "DELETE":
                return await self.handle_delete(event)
            else:
                self.logger.warning(
                    f"Unknown database event type: {db_event.event_type}"
                )
                return {"status": "unknown_event", "event_type": db_event.event_type}

        except Exception as e:
            self.logger.error(f"Failed to handle Supabase database event: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_signup(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle user signup event."""
        try:
            auth_event = self._parse_auth_event(event.data)

            # Create user in local system
            from core.user import get_user_service

            user_service = get_user_service()

            user_data = {
                "id": auth_event.user_id,
                "email": auth_event.email,
                "created_at": auth_event.timestamp,
                "metadata": auth_event.metadata,
            }

            await user_service.create_user_from_supabase(user_data)

            # Send welcome notification
            from notifications.notification_service import get_notification_service

            notification_service = get_notification_service()

            await notification_service.send_welcome_email(auth_event.user_id)

            # Record metrics
            await self.monitoring.record_metric(
                "supabase_signup_completed", 1, {"source": "supabase_webhook"}
            )

            return {
                "status": "success",
                "user_id": auth_event.user_id,
                "email": auth_event.email,
                "action": "user_created",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle signup: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_login(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle user login event."""
        try:
            auth_event = self._parse_auth_event(event.data)

            # Update user login tracking
            from core.user import get_user_service

            user_service = get_user_service()

            await user_service.update_user_login(
                auth_event.user_id, auth_event.timestamp
            )

            # Create session
            from redis_core.session import get_session_service

            session_service = get_session_service()

            session_data = {
                "user_id": auth_event.user_id,
                "email": auth_event.email,
                "login_time": auth_event.timestamp,
                "source": "supabase",
            }

            session_id = await session_service.create_session(
                auth_event.user_id, session_data
            )

            # Record metrics
            await self.monitoring.record_metric(
                "supabase_login_completed", 1, {"source": "supabase_webhook"}
            )

            return {
                "status": "success",
                "user_id": auth_event.user_id,
                "session_id": session_id,
                "action": "login_completed",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle login: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_logout(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle user logout event."""
        try:
            auth_event = self._parse_auth_event(event.data)

            # Update user logout tracking
            from core.user import get_user_service

            user_service = get_user_service()

            await user_service.update_user_logout(
                auth_event.user_id, auth_event.timestamp
            )

            # Invalidate sessions
            from redis_core.session import get_session_service

            session_service = get_session_service()

            await session_service.invalidate_user_sessions(auth_event.user_id)

            # Record metrics
            await self.monitoring.record_metric(
                "supabase_logout_completed", 1, {"source": "supabase_webhook"}
            )

            return {
                "status": "success",
                "user_id": auth_event.user_id,
                "action": "logout_completed",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle logout: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_password_recovery(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle password recovery event."""
        try:
            auth_event = self._parse_auth_event(event.data)

            # Send password recovery email
            from notifications.notification_service import get_notification_service

            notification_service = get_notification_service()

            await notification_service.send_password_recovery_email(
                auth_event.user_id,
                auth_event.email,
                auth_event.metadata.get("recovery_token"),
            )

            # Record metrics
            await self.monitoring.record_metric(
                "supabase_password_recovery_initiated",
                1,
                {"source": "supabase_webhook"},
            )

            return {
                "status": "success",
                "user_id": auth_event.user_id,
                "email": auth_event.email,
                "action": "password_recovery_sent",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle password recovery: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_user_updated(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle user updated event."""
        try:
            auth_event = self._parse_auth_event(event.data)

            # Update user in local system
            from core.user import get_user_service

            user_service = get_user_service()

            update_data = {
                "email": auth_event.email,
                "updated_at": auth_event.timestamp,
                "metadata": auth_event.metadata,
            }

            await user_service.update_user_from_supabase(
                auth_event.user_id, update_data
            )

            # Record metrics
            await self.monitoring.record_metric(
                "supabase_user_updated", 1, {"source": "supabase_webhook"}
            )

            return {
                "status": "success",
                "user_id": auth_event.user_id,
                "action": "user_updated",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle user updated: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_user_deleted(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle user deleted event."""
        try:
            auth_event = self._parse_auth_event(event.data)

            # Delete user from local system
            from core.user import get_user_service

            user_service = get_user_service()

            await user_service.delete_user_from_supabase(auth_event.user_id)

            # Clean up user data
            await self._cleanup_user_data(auth_event.user_id)

            # Record metrics
            await self.monitoring.record_metric(
                "supabase_user_deleted", 1, {"source": "supabase_webhook"}
            )

            return {
                "status": "success",
                "user_id": auth_event.user_id,
                "action": "user_deleted",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle user deleted: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_insert(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle database insert event."""
        try:
            db_event = self._parse_database_event(event.data)

            # Handle table-specific inserts
            if db_event.table == "workspaces":
                return await self._handle_workspace_insert(db_event)
            elif db_event.table == "projects":
                return await self._handle_project_insert(db_event)
            elif db_event.table == "agents":
                return await self._handle_agent_insert(db_event)
            else:
                # Generic insert handling
                return await self._handle_generic_insert(db_event)

        except Exception as e:
            self.logger.error(f"Failed to handle insert: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_update(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle database update event."""
        try:
            db_event = self._parse_database_event(event.data)

            # Handle table-specific updates
            if db_event.table == "workspaces":
                return await self._handle_workspace_update(db_event)
            elif db_event.table == "projects":
                return await self._handle_project_update(db_event)
            elif db_event.table == "agents":
                return await self._handle_agent_update(db_event)
            else:
                # Generic update handling
                return await self._handle_generic_update(db_event)

        except Exception as e:
            self.logger.error(f"Failed to handle update: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_delete(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle database delete event."""
        try:
            db_event = self._parse_database_event(event.data)

            # Handle table-specific deletes
            if db_event.table == "workspaces":
                return await self._handle_workspace_delete(db_event)
            elif db_event.table == "projects":
                return await self._handle_project_delete(db_event)
            elif db_event.table == "agents":
                return await self._handle_agent_delete(db_event)
            else:
                # Generic delete handling
                return await self._handle_generic_delete(db_event)

        except Exception as e:
            self.logger.error(f"Failed to handle delete: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_storage_created(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle storage file created event."""
        try:
            storage_data = event.data

            # Process file upload
            from infrastructure.storage import get_cloud_storage

            storage_service = get_cloud_storage()

            file_path = storage_data.get("path")
            file_size = storage_data.get("size", 0)
            mime_type = storage_data.get("mime_type")

            # Update file metadata
            await storage_service.update_file_metadata(
                file_path,
                {
                    "size": file_size,
                    "mime_type": mime_type,
                    "created_at": datetime.utcnow(),
                    "source": "supabase_storage",
                },
            )

            # Record metrics
            await self.monitoring.record_metric(
                "supabase_storage_file_created",
                1,
                {"source": "supabase_webhook", "mime_type": mime_type},
            )

            return {
                "status": "success",
                "file_path": file_path,
                "action": "file_created",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle storage created: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_storage_updated(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle storage file updated event."""
        try:
            storage_data = event.data

            file_path = storage_data.get("path")
            file_size = storage_data.get("size", 0)

            # Update file metadata
            from infrastructure.storage import get_cloud_storage

            storage_service = get_cloud_storage()

            await storage_service.update_file_metadata(
                file_path,
                {
                    "size": file_size,
                    "updated_at": datetime.utcnow(),
                    "source": "supabase_storage",
                },
            )

            return {
                "status": "success",
                "file_path": file_path,
                "action": "file_updated",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle storage updated: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_storage_deleted(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle storage file deleted event."""
        try:
            storage_data = event.data

            file_path = storage_data.get("path")

            # Clean up local references
            from infrastructure.storage import get_cloud_storage

            storage_service = get_cloud_storage()

            await storage_service.cleanup_file_references(file_path)

            return {
                "status": "success",
                "file_path": file_path,
                "action": "file_deleted",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle storage deleted: {e}")
            return {"status": "error", "error": str(e)}

    def _parse_auth_event(self, data: Dict[str, Any]) -> SupabaseAuthEvent:
        """Parse Supabase authentication event."""
        user_data = data.get("user", {})

        return SupabaseAuthEvent(
            user_id=user_data.get("id"),
            email=user_data.get("email"),
            event_type=data.get("type", "unknown"),
            timestamp=datetime.utcnow(),
            metadata={
                "raw_data": data,
                "user_metadata": user_data.get("user_metadata", {}),
                "app_metadata": user_data.get("app_metadata", {}),
            },
        )

    def _parse_database_event(self, data: Dict[str, Any]) -> SupabaseDatabaseEvent:
        """Parse Supabase database event."""
        return SupabaseDatabaseEvent(
            table=data.get("table", ""),
            record=data.get("record", {}),
            old_record=data.get("old_record"),
            event_type=data.get("type", "unknown"),
            timestamp=datetime.utcnow(),
            schema=data.get("schema", "public"),
        )

    async def _cleanup_user_data(self, user_id: str):
        """Clean up user data after deletion."""
        try:
            # Invalidate all sessions
            from redis_core.session import get_session_service

            session_service = get_session_service()
            await session_service.invalidate_user_sessions(user_id)

            # Clean up user cache
            from redis_core.cache import get_cache_service

            cache_service = get_cache_service()
            await cache_service.clear_user_cache(user_id)

            # Clean up user-specific data
            # Add more cleanup as needed

        except Exception as e:
            self.logger.error(f"Failed to cleanup user data for {user_id}: {e}")

    async def _handle_workspace_insert(
        self, db_event: SupabaseDatabaseEvent
    ) -> Dict[str, Any]:
        """Handle workspace insert event."""
        try:
            workspace_data = db_event.record

            from core.workspace import get_workspace_service

            workspace_service = get_workspace_service()

            await workspace_service.sync_workspace_from_supabase(workspace_data)

            return {
                "status": "success",
                "table": db_event.table,
                "workspace_id": workspace_data.get("id"),
                "action": "workspace_synced",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle workspace insert: {e}")
            return {"status": "error", "error": str(e)}

    async def _handle_project_insert(
        self, db_event: SupabaseDatabaseEvent
    ) -> Dict[str, Any]:
        """Handle project insert event."""
        try:
            project_data = db_event.record

            from core.project import get_project_service

            project_service = get_project_service()

            await project_service.sync_project_from_supabase(project_data)

            return {
                "status": "success",
                "table": db_event.table,
                "project_id": project_data.get("id"),
                "action": "project_synced",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle project insert: {e}")
            return {"status": "error", "error": str(e)}

    async def _handle_agent_insert(
        self, db_event: SupabaseDatabaseEvent
    ) -> Dict[str, Any]:
        """Handle agent insert event."""
        try:
            agent_data = db_event.record

            from agents.core.registry import get_agent_registry

            agent_registry = get_agent_registry()

            await agent_registry.sync_agent_from_supabase(agent_data)

            return {
                "status": "success",
                "table": db_event.table,
                "agent_id": agent_data.get("id"),
                "action": "agent_synced",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle agent insert: {e}")
            return {"status": "error", "error": str(e)}

    async def _handle_generic_insert(
        self, db_event: SupabaseDatabaseEvent
    ) -> Dict[str, Any]:
        """Handle generic insert event."""
        return {
            "status": "success",
            "table": db_event.table,
            "action": "generic_insert_handled",
        }

    async def _handle_workspace_update(
        self, db_event: SupabaseDatabaseEvent
    ) -> Dict[str, Any]:
        """Handle workspace update event."""
        try:
            workspace_data = db_event.record

            from core.workspace import get_workspace_service

            workspace_service = get_workspace_service()

            await workspace_service.update_workspace_from_supabase(
                workspace_data.get("id"), workspace_data
            )

            return {
                "status": "success",
                "table": db_event.table,
                "workspace_id": workspace_data.get("id"),
                "action": "workspace_updated",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle workspace update: {e}")
            return {"status": "error", "error": str(e)}

    async def _handle_project_update(
        self, db_event: SupabaseDatabaseEvent
    ) -> Dict[str, Any]:
        """Handle project update event."""
        try:
            project_data = db_event.record

            from core.project import get_project_service

            project_service = get_project_service()

            await project_service.update_project_from_supabase(
                project_data.get("id"), project_data
            )

            return {
                "status": "success",
                "table": db_event.table,
                "project_id": project_data.get("id"),
                "action": "project_updated",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle project update: {e}")
            return {"status": "error", "error": str(e)}

    async def _handle_agent_update(
        self, db_event: SupabaseDatabaseEvent
    ) -> Dict[str, Any]:
        """Handle agent update event."""
        try:
            agent_data = db_event.record

            from agents.core.registry import get_agent_registry

            agent_registry = get_agent_registry()

            await agent_registry.update_agent_from_supabase(
                agent_data.get("id"), agent_data
            )

            return {
                "status": "success",
                "table": db_event.table,
                "agent_id": agent_data.get("id"),
                "action": "agent_updated",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle agent update: {e}")
            return {"status": "error", "error": str(e)}

    async def _handle_generic_update(
        self, db_event: SupabaseDatabaseEvent
    ) -> Dict[str, Any]:
        """Handle generic update event."""
        return {
            "status": "success",
            "table": db_event.table,
            "action": "generic_update_handled",
        }

    async def _handle_workspace_delete(
        self, db_event: SupabaseDatabaseEvent
    ) -> Dict[str, Any]:
        """Handle workspace delete event."""
        try:
            workspace_id = (
                db_event.old_record.get("id") if db_event.old_record else None
            )

            if workspace_id:
                from core.workspace import get_workspace_service

                workspace_service = get_workspace_service()

                await workspace_service.delete_workspace_from_supabase(workspace_id)

            return {
                "status": "success",
                "table": db_event.table,
                "workspace_id": workspace_id,
                "action": "workspace_deleted",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle workspace delete: {e}")
            return {"status": "error", "error": str(e)}

    async def _handle_project_delete(
        self, db_event: SupabaseDatabaseEvent
    ) -> Dict[str, Any]:
        """Handle project delete event."""
        try:
            project_id = db_event.old_record.get("id") if db_event.old_record else None

            if project_id:
                from core.project import get_project_service

                project_service = get_project_service()

                await project_service.delete_project_from_supabase(project_id)

            return {
                "status": "success",
                "table": db_event.table,
                "project_id": project_id,
                "action": "project_deleted",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle project delete: {e}")
            return {"status": "error", "error": str(e)}

    async def _handle_agent_delete(
        self, db_event: SupabaseDatabaseEvent
    ) -> Dict[str, Any]:
        """Handle agent delete event."""
        try:
            agent_id = db_event.old_record.get("id") if db_event.old_record else None

            if agent_id:
                from agents.core.registry import get_agent_registry

                agent_registry = get_agent_registry()

                await agent_registry.delete_agent_from_supabase(agent_id)

            return {
                "status": "success",
                "table": db_event.table,
                "agent_id": agent_id,
                "action": "agent_deleted",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle agent delete: {e}")
            return {"status": "error", "error": str(e)}

    async def _handle_generic_delete(
        self, db_event: SupabaseDatabaseEvent
    ) -> Dict[str, Any]:
        """Handle generic delete event."""
        return {
            "status": "success",
            "table": db_event.table,
            "action": "generic_delete_handled",
        }


# Global Supabase webhook handler instance
_supabase_webhook_handler: Optional[SupabaseWebhookHandler] = None


def get_supabase_webhook_handler() -> SupabaseWebhookHandler:
    """Get the global Supabase webhook handler instance."""
    global _supabase_webhook_handler
    if _supabase_webhook_handler is None:
        _supabase_webhook_handler = SupabaseWebhookHandler()
    return _supabase_webhook_handler


# Export all components
__all__ = [
    "SupabaseWebhookHandler",
    "SupabaseAuthEvent",
    "SupabaseDatabaseEvent",
    "get_supabase_webhook_handler",
]
