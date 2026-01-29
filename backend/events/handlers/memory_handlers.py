"""
Memory system event handlers.
Handle events that trigger memory indexing, graph updates, and synchronization.
"""

import logging
from types import Event, EventType, FoundationUpdatedEvent, ICPCreatedEvent
from typing import Any, Dict

from memory.graph import MemoryGraph
from memory.services import MemoryService
from memory.vector_store import VectorStore

logger = logging.getLogger(__name__)


async def on_foundation_updated(event: FoundationUpdatedEvent) -> None:
    """Handle foundation updated event - triggers memory reindexing."""
    try:
        workspace_id = event.workspace_id
        changes = event.changes

        logger.info(
            f"Foundation updated for workspace {workspace_id}, triggering memory sync"
        )

        # Get memory service
        memory_service = MemoryService()

        # Reindex foundation data
        await memory_service.index_foundation_data(workspace_id)

        # Update memory graph with new relationships
        graph = MemoryGraph()
        await graph.update_foundation_nodes(workspace_id, changes)

        # Sync vector store if embeddings are enabled
        vector_store = VectorStore()
        if vector_store.is_enabled():
            await vector_store.sync_foundation_embeddings(workspace_id)

        logger.info(f"Memory sync completed for workspace {workspace_id}")

    except Exception as e:
        logger.error(f"Failed to handle foundation updated event: {e}")


async def on_icp_created(event: ICPCreatedEvent) -> None:
    """Handle ICP created event - adds ICP to memory graph."""
    try:
        workspace_id = event.workspace_id
        icp_id = event.icp_id
        icp_name = event.icp_name

        logger.info(f"ICP created: {icp_name} ({icp_id}) for workspace {workspace_id}")

        # Get memory graph service
        graph = MemoryGraph()

        # Add ICP node to graph
        icp_data = {
            "id": icp_id,
            "name": icp_name,
            "generation_method": event.generation_method,
            "created_at": event.timestamp.isoformat(),
            "workspace_id": workspace_id,
        }

        await graph.add_icp_node(workspace_id, icp_data)

        # Create relationships between ICP and foundation data
        await graph.connect_icp_to_foundation(workspace_id, icp_id)

        # Index in vector store for semantic search
        vector_store = VectorStore()
        if vector_store.is_enabled():
            await vector_store.index_icp(workspace_id, icp_id, icp_data)

        logger.info(f"ICP {icp_id} added to memory systems")

    except Exception as e:
        logger.error(f"Failed to handle ICP created event: {e}")


async def on_icp_updated(event: Event) -> None:
    """Handle ICP updated event - updates memory graph and vector store."""
    try:
        workspace_id = event.workspace_id
        icp_id = event.data.get("icp_id") if event.data else None

        if not icp_id:
            logger.warning("ICP updated event missing icp_id")
            return

        logger.info(f"ICP updated: {icp_id} for workspace {workspace_id}")

        # Update memory graph
        graph = MemoryGraph()
        await graph.update_icp_node(workspace_id, icp_id, event.data)

        # Update vector store embeddings
        vector_store = VectorStore()
        if vector_store.is_enabled():
            await vector_store.update_icp_embeddings(workspace_id, icp_id, event.data)

        logger.info(f"ICP {icp_id} updated in memory systems")

    except Exception as e:
        logger.error(f"Failed to handle ICP updated event: {e}")


async def on_icp_deleted(event: Event) -> None:
    """Handle ICP deleted event - removes from memory systems."""
    try:
        workspace_id = event.workspace_id
        icp_id = event.data.get("icp_id") if event.data else None

        if not icp_id:
            logger.warning("ICP deleted event missing icp_id")
            return

        logger.info(f"ICP deleted: {icp_id} for workspace {workspace_id}")

        # Remove from memory graph
        graph = MemoryGraph()
        await graph.remove_icp_node(workspace_id, icp_id)

        # Remove from vector store
        vector_store = VectorStore()
        if vector_store.is_enabled():
            await vector_store.remove_icp_embeddings(workspace_id, icp_id)

        logger.info(f"ICP {icp_id} removed from memory systems")

    except Exception as e:
        logger.error(f"Failed to handle ICP deleted event: {e}")


# Register all handlers
def register_memory_handlers():
    """Register all memory event handlers."""
    from bus import subscribe_event

    handlers = [
        (EventType.FOUNDATION_UPDATED, on_foundation_updated),
        (EventType.ICP_CREATED, on_icp_created),
        (EventType.ICP_UPDATED, on_icp_updated),
        (EventType.ICP_DELETED, on_icp_deleted),
    ]

    for event_type, handler in handlers:
        subscribe_event(event_type, handler)
        logger.debug(f"Registered memory handler for {event_type.value}")
