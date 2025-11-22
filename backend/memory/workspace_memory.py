"""
Workspace Memory - Shared Workspace Context Storage

This module implements workspace-level memory using Supabase for persistent storage.
Workspace memory stores shared context like ICPs, brand voice, preferences, and
workspace-wide settings that should be accessible across sessions and agents.

Purpose:
--------
- Store shared workspace context (ICPs, brand voice, preferences)
- Enable consistent context access across all agents and sessions
- Support workspace-wide learning and customization
- Maintain persistent workspace configuration
- Provide structured storage with JSONB support

Schema:
-------
Table: workspace_memory
Columns:
- id: UUID (primary key)
- workspace_id: UUID (foreign key to workspaces table)
- memory_key: str (unique identifier within workspace)
- memory_type: str (e.g., "icp", "brand_voice", "preference", "custom")
- value: JSONB (flexible storage for any structure)
- metadata: JSONB (additional metadata like tags, timestamps, versions)
- created_at: timestamp
- updated_at: timestamp
- embedding: vector (for future semantic search support)

Indexes:
- (workspace_id, memory_key) - unique
- workspace_id - for filtering
- memory_type - for type-based queries

Storage Backend: Supabase (PostgreSQL)
- Persistent storage across sessions
- JSONB support for flexible schemas
- Full-text search capabilities
- Vector support for semantic search (pgvector extension)
- Transaction support for consistency

Dependencies:
-------------
- supabase: For database client
- services.supabase_client: For shared Supabase connection
- datetime: For timestamp management
- uuid: For ID generation

Usage Example:
--------------
from memory.workspace_memory import WorkspaceMemory
from uuid import UUID

# Initialize workspace memory
ws_memory = WorkspaceMemory()

# Store brand voice
await ws_memory.remember(
    key="brand_voice",
    value={
        "tone": "professional yet friendly",
        "values": ["innovation", "transparency", "customer-first"],
        "avoid": ["jargon", "overpromising"]
    },
    workspace_id=UUID("..."),
    metadata={"category": "brand", "version": "1.0"}
)

# Retrieve brand voice
brand_voice = await ws_memory.recall(
    key="brand_voice",
    workspace_id=UUID("...")
)

# Search for ICPs
icps = await ws_memory.search(
    query="enterprise",
    workspace_id=UUID("..."),
    filters={"memory_type": "icp"}
)
"""

import json
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
import structlog

from memory.base import BaseMemory, MemoryError
from services.supabase_client import supabase_client

logger = structlog.get_logger()


class WorkspaceMemory(BaseMemory):
    """
    Supabase-based workspace memory for shared context storage.

    This class manages workspace-level information that should persist
    across sessions and be accessible to all agents within the workspace.
    Uses Supabase for reliable, structured storage with JSONB support.

    Attributes:
        supabase: Supabase client instance
        table_name: Name of the memory table
    """

    def __init__(self, table_name: str = "workspace_memory"):
        """
        Initialize workspace memory with Supabase client.

        Args:
            table_name: Name of the Supabase table (default: "workspace_memory")
        """
        super().__init__(memory_type="workspace")
        self.supabase = supabase_client
        self.table_name = table_name

    async def remember(
        self,
        key: str,
        value: Any,
        workspace_id: UUID,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> None:
        """
        Store or update workspace memory.

        Uses upsert to handle both insert and update cases. If a memory item
        with the same key exists, it will be updated; otherwise, it will be created.

        Args:
            key: Unique identifier within the workspace (e.g., "brand_voice", "icp_enterprise")
            value: Data to store (dict, list, string, etc.)
            workspace_id: Workspace UUID
            metadata: Optional metadata (tags, category, version, etc.)
            ttl: Not used for workspace memory (persistent storage)

        Raises:
            MemoryError: If storage operation fails
        """
        self._validate_workspace_id(workspace_id)

        try:
            # Prepare memory record
            memory_record = {
                "workspace_id": str(workspace_id),
                "memory_key": key,
                "value": value if isinstance(value, dict) else {"data": value},
                "metadata": metadata or {},
                "updated_at": datetime.utcnow().isoformat()
            }

            # Infer memory type from metadata or key
            if metadata and "memory_type" in metadata:
                memory_record["memory_type"] = metadata["memory_type"]
            else:
                # Infer from key prefix
                if key.startswith("icp_"):
                    memory_record["memory_type"] = "icp"
                elif key.startswith("brand_"):
                    memory_record["memory_type"] = "brand_voice"
                elif key.startswith("pref_"):
                    memory_record["memory_type"] = "preference"
                else:
                    memory_record["memory_type"] = "custom"

            # Check if exists
            existing = await self._get_by_key(key, workspace_id)

            if existing:
                # Update existing record
                result = await self.supabase.update(
                    table=self.table_name,
                    filters={"id": existing["id"]},
                    updates=memory_record
                )
            else:
                # Insert new record
                memory_record["id"] = str(uuid4())
                memory_record["created_at"] = datetime.utcnow().isoformat()
                result = await self.supabase.insert(
                    table=self.table_name,
                    data=memory_record
                )

            self.logger.debug(
                "Stored workspace memory",
                key=key,
                workspace_id=str(workspace_id),
                operation="update" if existing else "insert"
            )

        except Exception as e:
            self.logger.error(
                "Failed to store workspace memory",
                key=key,
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to store workspace memory: {str(e)}",
                memory_type=self.memory_type,
                operation="remember"
            )

    async def recall(
        self,
        key: str,
        workspace_id: UUID,
        default: Any = None
    ) -> Any:
        """
        Retrieve workspace memory by key.

        Args:
            key: Memory identifier within the workspace
            workspace_id: Workspace UUID
            default: Default value if not found

        Returns:
            The stored value, or default if not found

        Raises:
            MemoryError: If retrieval operation fails
        """
        self._validate_workspace_id(workspace_id)

        try:
            record = await self._get_by_key(key, workspace_id)

            if not record:
                self.logger.debug(
                    "No workspace memory found, returning default",
                    key=key,
                    workspace_id=str(workspace_id)
                )
                return default

            # Extract value from record
            value = record.get("value", default)

            self.logger.debug(
                "Recalled workspace memory",
                key=key,
                workspace_id=str(workspace_id)
            )

            return value

        except Exception as e:
            self.logger.error(
                "Failed to recall workspace memory",
                key=key,
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to recall workspace memory: {str(e)}",
                memory_type=self.memory_type,
                operation="recall"
            )

    async def search(
        self,
        query: str,
        workspace_id: UUID,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search workspace memory using text matching.

        Searches across memory keys and JSONB values for matching content.
        For semantic search, use SemanticMemory instead.

        Args:
            query: Search query string
            workspace_id: Workspace UUID
            top_k: Maximum results to return
            filters: Optional filters (memory_type, created_after, etc.)

        Returns:
            List of matching memory records

        Raises:
            MemoryError: If search operation fails
        """
        self._validate_workspace_id(workspace_id)

        try:
            # Build base query
            query_filters = {"workspace_id": str(workspace_id)}

            # Add type filter if specified
            if filters and "memory_type" in filters:
                query_filters["memory_type"] = filters["memory_type"]

            # Fetch all matching records (Supabase filtering)
            records = await self.supabase.fetch_all(
                table=self.table_name,
                filters=query_filters
            )

            # Filter by query string (simple text search)
            results = []
            query_lower = query.lower()

            for record in records:
                # Check if query matches key
                if query_lower in record.get("memory_key", "").lower():
                    results.append(record)
                    continue

                # Check if query matches value content
                value = record.get("value", {})
                value_str = json.dumps(value).lower()
                if query_lower in value_str:
                    results.append(record)

                if len(results) >= top_k:
                    break

            # Apply date filters if specified
            if filters:
                if "created_after" in filters:
                    created_after = filters["created_after"]
                    results = [
                        r for r in results
                        if r.get("created_at", "") >= created_after
                    ]
                if "updated_after" in filters:
                    updated_after = filters["updated_after"]
                    results = [
                        r for r in results
                        if r.get("updated_at", "") >= updated_after
                    ]

            self.logger.debug(
                "Workspace memory search completed",
                query=query,
                workspace_id=str(workspace_id),
                results_count=len(results)
            )

            return results[:top_k]

        except Exception as e:
            self.logger.error(
                "Failed to search workspace memory",
                query=query,
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to search workspace memory: {str(e)}",
                memory_type=self.memory_type,
                operation="search"
            )

    async def forget(
        self,
        key: str,
        workspace_id: UUID
    ) -> bool:
        """
        Delete workspace memory by key.

        Args:
            key: Memory identifier to delete
            workspace_id: Workspace UUID

        Returns:
            True if deletion was successful

        Raises:
            MemoryError: If deletion operation fails
        """
        self._validate_workspace_id(workspace_id)

        try:
            # Get record to find ID
            record = await self._get_by_key(key, workspace_id)

            if not record:
                self.logger.debug(
                    "No workspace memory to delete",
                    key=key,
                    workspace_id=str(workspace_id)
                )
                return False

            # Delete record
            success = await self.supabase.delete(
                table=self.table_name,
                filters={"id": record["id"]}
            )

            self.logger.debug(
                "Workspace memory deleted",
                key=key,
                workspace_id=str(workspace_id),
                success=success
            )

            return success

        except Exception as e:
            self.logger.error(
                "Failed to delete workspace memory",
                key=key,
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to delete workspace memory: {str(e)}",
                memory_type=self.memory_type,
                operation="forget"
            )

    async def learn_from_feedback(
        self,
        key: str,
        feedback: Dict[str, Any],
        workspace_id: UUID
    ) -> None:
        """
        Update workspace memory based on feedback.

        For workspace memory, this can be used to refine ICPs, adjust
        brand voice, or update preferences based on performance data.

        Args:
            key: Memory identifier to update
            feedback: Feedback data to incorporate
            workspace_id: Workspace UUID

        Raises:
            MemoryError: If update operation fails
        """
        self._validate_workspace_id(workspace_id)

        try:
            # Get existing record
            record = await self._get_by_key(key, workspace_id)

            if not record:
                self.logger.warning(
                    "Cannot learn from feedback: memory not found",
                    key=key,
                    workspace_id=str(workspace_id)
                )
                return

            # Update based on feedback
            value = record.get("value", {})
            metadata = record.get("metadata", {})

            # Add feedback to history
            if "feedback_history" not in metadata:
                metadata["feedback_history"] = []

            feedback_item = feedback.copy()
            feedback_item["timestamp"] = datetime.utcnow().isoformat()
            metadata["feedback_history"].append(feedback_item)

            # Keep only recent feedback (last 20 items)
            if len(metadata["feedback_history"]) > 20:
                metadata["feedback_history"] = metadata["feedback_history"][-20:]

            # Update record
            await self.supabase.update(
                table=self.table_name,
                filters={"id": record["id"]},
                updates={
                    "metadata": metadata,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )

            self.logger.info(
                "Workspace memory learned from feedback",
                key=key,
                workspace_id=str(workspace_id)
            )

        except Exception as e:
            self.logger.error(
                "Failed to learn from feedback",
                key=key,
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to learn from feedback: {str(e)}",
                memory_type=self.memory_type,
                operation="learn_from_feedback"
            )

    async def clear(self, workspace_id: UUID) -> bool:
        """
        Clear all workspace memory for a workspace.

        Args:
            workspace_id: Workspace UUID

        Returns:
            True if successful

        Raises:
            MemoryError: If clear operation fails
        """
        self._validate_workspace_id(workspace_id)

        try:
            success = await self.supabase.delete(
                table=self.table_name,
                filters={"workspace_id": str(workspace_id)}
            )

            self.logger.info(
                "Cleared all workspace memory",
                workspace_id=str(workspace_id),
                success=success
            )

            return success

        except Exception as e:
            self.logger.error(
                "Failed to clear workspace memory",
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to clear workspace memory: {str(e)}",
                memory_type=self.memory_type,
                operation="clear"
            )

    async def list_all(
        self,
        workspace_id: UUID,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all memory items for a workspace.

        Args:
            workspace_id: Workspace UUID
            memory_type: Optional filter by memory type

        Returns:
            List of all memory records

        Raises:
            MemoryError: If list operation fails
        """
        self._validate_workspace_id(workspace_id)

        try:
            filters = {"workspace_id": str(workspace_id)}
            if memory_type:
                filters["memory_type"] = memory_type

            records = await self.supabase.fetch_all(
                table=self.table_name,
                filters=filters
            )

            self.logger.debug(
                "Listed workspace memory items",
                workspace_id=str(workspace_id),
                memory_type=memory_type,
                count=len(records)
            )

            return records

        except Exception as e:
            self.logger.error(
                "Failed to list workspace memory",
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to list workspace memory: {str(e)}",
                memory_type=self.memory_type,
                operation="list_all"
            )

    async def _get_by_key(self, key: str, workspace_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Helper method to get a memory record by key.

        Args:
            key: Memory key
            workspace_id: Workspace UUID

        Returns:
            Memory record or None if not found
        """
        try:
            record = await self.supabase.fetch_one(
                table=self.table_name,
                filters={
                    "workspace_id": str(workspace_id),
                    "memory_key": key
                }
            )
            return record
        except Exception:
            return None
