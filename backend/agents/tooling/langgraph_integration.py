"""
LangGraph Integration Layer

Provides thin wrappers and factory functions that turn RaptorFlow's backend services
(ModelDispatcher, RaptorBus, AuditLog) into LangGraph-compatible tools.

This layer keeps integration minimal and acts as an adapter between our infra
and LangGraph's tool interface.

All tools require a ToolContext to ensure proper workspace scoping, audit logging,
and correlation tracking.
"""

import uuid
from typing import Callable, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import json

# Defensive imports for LangGraph (may not be available in all environments)
try:
    from langchain_core.tools import tool
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    tool = None  # type: ignore

from backend.services.model_dispatcher import model_dispatcher, ModelDispatchRequest
from backend.bus.raptor_bus import get_bus
from backend.services.audit_log import log_tool_call, log_tool_completion
from backend.utils.logging_config import get_logger

from .contracts import ToolContext, ToolOutput


logger = get_logger("langgraph")


# ============================================================================
# TOOL WRAPPER FACTORIES
# ============================================================================

def make_model_dispatch_tool(dispatcher=None):
    """
    Factory that creates a LangGraph tool for LLM inference using ModelDispatcher.

    The tool accepts ToolContext and model parameters, performs the dispatch,
    logs costs/audit, and returns JSON-serializable results.

    Args:
        dispatcher: ModelDispatcher instance (defaults to singleton)

    Returns:
        LangGraph-compatible tool function
    """
    if not LANGGRAPH_AVAILABLE:
        raise RuntimeError("LangGraph not installed. Run: pip install langgraph langchain-core")

    the_dispatcher = dispatcher or model_dispatcher

    @tool
    async def model_dispatch_tool(
        ctx: Dict,  # ToolContext as dict for serialization
        model: str,
        messages: list,
        prompt: Optional[str] = None,
        cache_key: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> ToolOutput:
        """
        Dispatch an LLM inference request through RaptorFlow's infrastructure.

        This tool handles cost logging, budget checks, and audit trails automatically.

        Args:
            ctx: ToolContext dict containing workspace_id, agent_id, etc.
            model: Model alias (fast/standard/heavy) or full model ID
            messages: List of chat messages [{"role": "user", "content": "..."}]
            prompt: Alternative to messages for simple text input
            cache_key: Optional cache key for response caching
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            dict with 'response', 'model', 'tokens_used', 'cost_usd', 'cached'
        """
        # Reconstruct ToolContext from dict
        tool_ctx = ToolContext(**ctx) if isinstance(ctx, dict) else ctx
        bound_logger = logger.bind(
            workspace_id=tool_ctx.workspace_id,
            agent_id=tool_ctx.agent_id,
            agent_run_id=tool_ctx.agent_run_id,
            tool_name="model_dispatch",
        )

        tool_calls = []

        try:
            bound_logger.info("Starting model dispatch")

            # Build ModelDispatchRequest
            # Convert prompt to messages if provided
            if prompt and not messages:
                messages = [{"role": "user", "content": prompt}]

            request = ModelDispatchRequest(
                workspace_id=tool_ctx.workspace_id,
                model=model,
                messages=messages,
                cache_key=cache_key,
                agent_id=tool_ctx.agent_id,
                agent_run_id=tool_ctx.agent_run_id,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Log tool call start
            await log_tool_call(
                workspace_id=tool_ctx.workspace_id,
                tool_name="model_dispatch",
                agent_id=tool_ctx.agent_id,
                parameters={
                    "model": model,
                    "message_count": len(messages),
                    "cache_key": cache_key,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

            # Execute dispatch
            start_time = datetime.utcnow()
            response = await the_dispatcher.dispatch(request)
            end_time = datetime.utcnow()

            execution_ms = int((end_time - start_time).total_seconds() * 1000)

            # Log completion
            await log_tool_completion(
                workspace_id=tool_ctx.workspace_id,
                tool_name="model_dispatch",
                agent_id=tool_ctx.agent_id,
                result_summary=f"Generated {response.total_tokens} tokens with {response.model}",
                success=True,
                execution_duration_ms=execution_ms,
            )

            bound_logger.info(
                "Model dispatch completed",
                model=response.model,
                tokens=response.total_tokens,
                cost=response.estimated_cost_usd,
                cached=response.cached,
            )

            return {
                "response": response.raw_response,
                "model": response.model,
                "prompt_tokens": response.prompt_tokens,
                "completion_tokens": response.completion_tokens,
                "total_tokens": response.total_tokens,
                "estimated_cost_usd": response.estimated_cost_usd,
                "cached": response.cached,
            }

        except Exception as e:
            error_str = str(e)

            # Log failure
            await log_tool_completion(
                workspace_id=tool_ctx.workspace_id,
                tool_name="model_dispatch",
                agent_id=tool_ctx.agent_id,
                result_summary=f"Model dispatch failed: {error_str}",
                success=False,
                error_message=error_str[:500],  # Truncate very long errors
            )

            bound_logger.error("Model dispatch failed", error=error_str)
            raise  # Re-raise for graph error handling

    return model_dispatch_tool


def make_bus_publish_tool():
    """
    Factory that creates a LangGraph tool for publishing events to RaptorBus.

    The tool accepts ToolContext and event payload, publishes to bus with metadata,
    and logs audit trail.

    Returns:
        LangGraph-compatible tool function
    """
    if not LANGGRAPH_AVAILABLE:
        raise RuntimeError("LangGraph not installed. Run: pip install langgraph langchain-core")

    @tool
    async def bus_publish_tool(
        ctx: Dict,  # ToolContext as dict
        event_type: str,
        payload: Dict[str, Any],
    ) -> ToolOutput:
        """
        Publish an event to RaptorBus for inter-agent communication.

        Args:
            ctx: ToolContext dict with workspace scoping
            event_type: Event type (e.g., "agent.task_started", "inference_complete")
            payload: Event payload (JSON-serializable dict)

        Returns:
            dict with 'status' and 'event_id'
        """
        # Reconstruct ToolContext
        tool_ctx = ToolContext(**ctx) if isinstance(ctx, dict) else ctx
        bound_logger = logger.bind(
            workspace_id=tool_ctx.workspace_id,
            agent_id=tool_ctx.agent_id,
            agent_run_id=tool_ctx.agent_run_id,
            tool_name="raptor_bus.publish",
        )

        try:
            bound_logger.info("Publishing to RaptorBus", event_type=event_type)

            # Get bus instance
            bus = await get_bus()

            # Log tool call
            await log_tool_call(
                workspace_id=tool_ctx.workspace_id,
                tool_name="raptor_bus.publish",
                agent_id=tool_ctx.agent_id,
                parameters={
                    "event_type": event_type,
                    "payload_keys": list(payload.keys()),
                },
            )

            # Publish (this will use workspace_id and correlation_id from ToolContext)
            await bus.publish(
                event_type=event_type,
                payload=payload,
                workspace_id=tool_ctx.workspace_id,
                correlation_id=tool_ctx.correlation_id,
            )

            # Log completion
            await log_tool_completion(
                workspace_id=tool_ctx.workspace_id,
                tool_name="raptor_bus.publish",
                agent_id=tool_ctx.agent_id,
                result_summary=f"Published {event_type} event",
                success=True,
            )

            bound_logger.info("Published to RaptorBus", event_type=event_type)

            return {
                "status": "published",
                "event_type": event_type,
                "workspace_id": tool_ctx.workspace_id,
            }

        except Exception as e:
            error_str = str(e)

            await log_tool_completion(
                workspace_id=tool_ctx.workspace_id,
                tool_name="raptor_bus.publish",
                agent_id=tool_ctx.agent_id,
                result_summary=f"Bus publish failed: {error_str}",
                success=False,
                error_message=error_str,
            )

            bound_logger.error("Bus publish failed", event_type=event_type, error=error_str)
            raise

    return bus_publish_tool


# ============================================================================
# AGENT RUN MANAGEMENT
# ============================================================================

async def start_agent_run(
    workspace_id: str,
    agent_id: Optional[str] = None,
    actor_user_id: Optional[str] = None,
    run_name: Optional[str] = None,
) -> str:
    """
    Start an agent run (for LangGraph graph execution).

    Inserts a row into agent_runs table and returns the run_id.

    Args:
        workspace_id: Target workspace
        agent_id: Agent type (optional, for now)
        actor_user_id: Human user initiating (optional)
        run_name: Human-readable run name

    Returns:
        agent_run_id as string
    """
    from backend.services.supabase_client import supabase_client

    run_id = str(uuid.uuid4())

    run_data = {
        "id": run_id,
        "workspace_id": workspace_id,
        "agent_id": agent_id,
        "actor_user_id": actor_user_id,
        "run_name": run_name,
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
    }

    await supabase_client.insert("agent_runs", run_data)

    logger.info(
        "Agent run started",
        workspace_id=workspace_id,
        agent_id=agent_id,
        run_id=run_id,
    )

    return run_id


async def complete_agent_run(
    agent_run_id: str,
    status: str,
    result_summary: Optional[str] = None,
    error_message: Optional[str] = None,
) -> None:
    """
    Complete an agent run (mark as finished/failed).

    Args:
        agent_run_id: The run ID from start_agent_run
        status: "completed", "failed", "cancelled"
        result_summary: Brief description of result
        error_message: Error details if failed
    """
    from backend.services.supabase_client import supabase_client

    update_data = {
        "status": status,
        "completed_at": datetime.utcnow().isoformat(),
    }

    if result_summary:
        update_data["result_summary"] = result_summary[:2000]  # Truncate if too long

    if error_message:
        update_data["error_message"] = error_message[:2000]

    await supabase_client.update(
        "agent_runs",
        update_data,
        filters={"id": agent_run_id}
    )

    logger.info(
        "Agent run completed",
        run_id=agent_run_id,
        status=status,
        result_summary=result_summary,
    )


async def build_tool_context_from_run(agent_run_id: str) -> ToolContext:
    """
    Build a ToolContext from an existing agent run.

    Looks up the run in agent_runs table and extracts workspace/agent metadata.

    Args:
        agent_run_id: Previously started run ID

    Returns:
        ToolContext populated with run metadata

    Raises:
        ValueError: If run not found
    """
    from backend.services.supabase_client import supabase_client

    # Query agent_runs
    result = await supabase_client.select(
        "agent_runs",
        ["workspace_id", "agent_id", "actor_user_id"],
        filters={"id": agent_run_id}
    )

    if not result.data:
        raise ValueError(f"Agent run not found: {agent_run_id}")

    run_data = result.data[0]

    return ToolContext(
        workspace_id=run_data["workspace_id"],
        agent_id=run_data["agent_id"],
        agent_run_id=agent_run_id,
        actor_user_id=run_data["actor_user_id"],
        correlation_id=get_correlation_id(),  # May be None, that's ok
    )


# ============================================================================
# TOOL REGISTRY HELPER
# ============================================================================

def get_default_toolset(dispatcher=None) -> Dict[str, Callable]:
    """
    Get a dict of default LangGraph tools for RaptorFlow graphs.

    Returns a mapping of tool names to tool functions, ready for LangGraph.

    Args:
        dispatcher: Optional custom ModelDispatcher

    Returns:
        dict like {"model_dispatch": <tool>, "bus_publish": <tool>}
    """
    return {
        "model_dispatch": make_model_dispatch_tool(dispatcher),
        "raptor_bus_publish": make_bus_publish_tool(),
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def langgraph_available() -> bool:
    """Check if LangGraph is available in this environment."""
    return LANGGRAPH_AVAILABLE


def require_langgraph():
    """Raise error if LangGraph not available."""
    if not LANGGRAPH_AVAILABLE:
        raise RuntimeError(
            "LangGraph not installed. Install with: pip install langgraph langchain-core"
        )
