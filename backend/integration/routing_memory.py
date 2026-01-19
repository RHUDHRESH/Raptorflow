"""
Integration between routing and memory systems.
Retrieves relevant memory before routing and injects context into routing decisions.
"""

import logging
from typing import Any, Dict, Optional

from backend.agents.routing.models import RoutingDecision
from backend.agents.routing.pipeline import RoutingPipeline
from backend.memory.controller import MemoryController

logger = logging.getLogger(__name__)


async def route_with_memory_context(
    request: str,
    workspace_id: str,
    memory_controller: MemoryController,
    routing_pipeline: RoutingPipeline,
) -> RoutingDecision:
    """
    Route request with memory context injection.

    Args:
        request: User request string
        workspace_id: Workspace ID
        memory_controller: Memory controller instance
        routing_pipeline: Routing pipeline instance

    Returns:
        Routing decision with memory context
    """
    try:
        # Retrieve relevant memory context
        memory_context = await memory_controller.search(
            workspace_id=workspace_id,
            query=request,
            memory_types=["foundation", "icp", "conversation"],
            limit=10,
        )

        # Format memory context for routing
        context_string = _format_memory_context(memory_context)

        # Enhance request with context
        enhanced_request = f"""
        User Request: {request}

        Relevant Context:
        {context_string}
        """

        # Route with enhanced request
        routing_decision = await routing_pipeline.route(
            request=enhanced_request, workspace_id=workspace_id, fast_mode=False
        )

        # Add memory context to routing decision
        routing_decision.memory_context = memory_context
        routing_decision.context_used = len(memory_context) > 0

        logger.info(f"Routed request with {len(memory_context)} memory items")

        return routing_decision

    except Exception as e:
        logger.error(f"Error in routing with memory context: {e}")
        # Fallback to routing without memory
        return await routing_pipeline.route(
            request=request, workspace_id=workspace_id, fast_mode=True
        )


def _format_memory_context(memory_items: list) -> str:
    """
    Format memory items into context string.

    Args:
        memory_items: List of memory items

    Returns:
        Formatted context string
    """
    if not memory_items:
        return "No relevant context found."

    context_parts = []

    for item in memory_items[:5]:  # Limit to top 5 items
        if item.memory_type == "foundation":
            context_parts.append(f"Foundation: {item.content[:200]}...")
        elif item.memory_type == "icp":
            context_parts.append(f"ICP: {item.content[:200]}...")
        elif item.memory_type == "conversation":
            context_parts.append(f"Previous: {item.content[:200]}...")
        else:
            context_parts.append(f"Context: {item.content[:200]}...")

    return "\n".join(context_parts)


async def get_memory_for_routing(
    workspace_id: str, query: str, memory_controller: MemoryController
) -> Dict[str, Any]:
    """
    Get memory context specifically for routing decisions.

    Args:
        workspace_id: Workspace ID
        query: Query string
        memory_controller: Memory controller

    Returns:
        Memory context dictionary
    """
    try:
        # Search for relevant memory
        memory_results = await memory_controller.search(
            workspace_id=workspace_id,
            query=query,
            memory_types=["foundation", "icp", "moves", "campaigns"],
            limit=5,
        )

        # Organize by type
        organized_context = {
            "foundation": [],
            "icps": [],
            "moves": [],
            "campaigns": [],
            "other": [],
        }

        for item in memory_results:
            if item.memory_type in organized_context:
                organized_context[item.memory_type].append(
                    {
                        "content": item.content,
                        "score": item.score,
                        "metadata": item.metadata,
                    }
                )
            else:
                organized_context["other"].append(
                    {
                        "content": item.content,
                        "score": item.score,
                        "metadata": item.metadata,
                    }
                )

        return organized_context

    except Exception as e:
        logger.error(f"Error getting memory for routing: {e}")
        return {}


async def update_routing_memory(
    workspace_id: str,
    routing_decision: RoutingDecision,
    memory_controller: MemoryController,
):
    """
    Store routing decision in memory for future reference.

    Args:
        workspace_id: Workspace ID
        routing_decision: Routing decision made
        memory_controller: Memory controller
    """
    try:
        # Store routing decision as episodic memory
        routing_content = f"""
        Routing Decision:
        - Target Agent: {routing_decision.target_agent}
        - Confidence: {routing_decision.confidence}
        - Routing Path: {routing_decision.routing_path}
        - Memory Used: {routing_decision.context_used}
        """

        await memory_controller.store(
            workspace_id=workspace_id,
            memory_type="conversation",
            content=routing_content,
            metadata={
                "type": "routing_decision",
                "target_agent": routing_decision.target_agent,
                "confidence": routing_decision.confidence,
                "timestamp": routing_decision.timestamp,
            },
        )

        logger.info(
            f"Stored routing decision for agent {routing_decision.target_agent}"
        )

    except Exception as e:
        logger.error(f"Error updating routing memory: {e}")


class MemoryAwareRouter:
    """
    Router that automatically incorporates memory context.
    """

    def __init__(
        self, memory_controller: MemoryController, routing_pipeline: RoutingPipeline
    ):
        self.memory_controller = memory_controller
        self.routing_pipeline = routing_pipeline

    async def route(self, request: str, workspace_id: str, **kwargs) -> RoutingDecision:
        """
        Route request with memory awareness.

        Args:
            request: User request
            workspace_id: Workspace ID
            **kwargs: Additional routing parameters

        Returns:
        Enhanced routing decision
        """
        return await route_with_memory_context(
            request=request,
            workspace_id=workspace_id,
            memory_controller=self.memory_controller,
            routing_pipeline=self.routing_pipeline,
        )
