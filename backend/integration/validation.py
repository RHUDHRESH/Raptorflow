"""
Cross-module validation functions.
Validates workspace consistency and agent state integrity.
"""

import logging
from typing import Any, Dict, List, Optional

from backend.agents.state import AgentState

logger = logging.getLogger(__name__)


async def validate_workspace_consistency(
    workspace_id: str, db_client, memory_controller
) -> Dict[str, Any]:
    """
    Validate workspace consistency across all modules.

    Args:
        workspace_id: Workspace ID to validate
        db_client: Database client
        memory_controller: Memory controller

    Returns:
        Validation results
    """
    try:
        logger.info(f"Validating workspace consistency for {workspace_id}")

        results = {
            "database": await _validate_database_consistency(workspace_id, db_client),
            "memory": await _validate_memory_consistency(
                workspace_id, memory_controller
            ),
            "cross_module": await _validate_cross_module_consistency(
                workspace_id, db_client, memory_controller
            ),
        }

        # Overall status
        results["overall"] = {
            "valid": all(result.get("valid", False) for result in results.values()),
            "errors": [
                result.get("error")
                for result in results.values()
                if result.get("error")
            ],
            "warnings": [
                result.get("warning")
                for result in results.values()
                if result.get("warning")
            ],
        }

        logger.info(
            f"Workspace validation completed: {'VALID' if results['overall']['valid'] else 'INVALID'}"
        )

        return results

    except Exception as e:
        logger.error(f"Error validating workspace consistency: {e}")
        return {
            "overall": {"valid": False, "error": str(e)},
            "database": {"valid": False, "error": str(e)},
            "memory": {"valid": False, "error": str(e)},
            "cross_module": {"valid": False, "error": str(e)},
        }


async def _validate_database_consistency(
    workspace_id: str, db_client
) -> Dict[str, Any]:
    """Validate database consistency."""
    try:
        errors = []
        warnings = []

        # Check workspace exists
        workspace_result = (
            db_client.table("workspaces").select("*").eq("id", workspace_id).execute()
        )
        if not workspace_result.data:
            return {"valid": False, "error": "Workspace not found in database"}

        workspace = workspace_result.data[0]

        # Check foundation exists
        foundation_result = (
            db_client.table("foundations")
            .select("*")
            .eq("workspace_id", workspace_id)
            .execute()
        )
        if not foundation_result.data:
            warnings.append("No foundation data found")

        # Check ICPs
        icp_result = (
            db_client.table("icp_profiles")
            .select("*")
            .eq("workspace_id", workspace_id)
            .execute()
        )
        if not icp_result.data:
            warnings.append("No ICP profiles found")

        # Check for orphaned records
        orphaned_moves = await _check_orphaned_moves(workspace_id, db_client)
        if orphaned_moves > 0:
            warnings.append(f"Found {orphaned_moves} orphaned move records")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "summary": {
                "workspace": workspace,
                "foundation_exists": bool(foundation_result.data),
                "icp_count": len(icp_result.data),
                "orphaned_moves": orphaned_moves,
            },
        }

    except Exception as e:
        return {"valid": False, "error": str(e)}


async def _validate_memory_consistency(
    workspace_id: str, memory_controller
) -> Dict[str, Any]:
    """Validate memory system consistency."""
    try:
        errors = []
        warnings = []

        # Check vector memory
        vector_results = await memory_controller.search(
            workspace_id=workspace_id,
            query="test",
            memory_types=["foundation", "icp", "conversation"],
            limit=1,
        )

        if not vector_results:
            warnings.append("No vector memory found")

        # Check graph memory
        try:
            graph_entities = await memory_controller.graph_memory.get_entities(
                workspace_id=workspace_id, entity_type=None
            )
            if not graph_entities:
                warnings.append("No graph entities found")
        except Exception as e:
            warnings.append(f"Graph memory error: {e}")

        # Check working memory
        try:
            working_memory = await memory_controller.working_memory.get_session_count(
                workspace_id
            )
            if working_memory == 0:
                warnings.append("No active working memory sessions")
        except Exception as e:
            warnings.append(f"Working memory error: {e}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "summary": {
                "vector_results": len(vector_results),
                "graph_entities": (
                    len(graph_entities) if "graph_entities" in locals() else 0
                ),
                "working_sessions": (
                    working_memory if "working_memory" in locals() else 0
                ),
            },
        }

    except Exception as e:
        return {"valid": False, "error": str(e)}


async def _validate_cross_module_consistency(
    workspace_id: str, db_client, memory_controller
) -> Dict[str, Any]:
    """Validate consistency between database and memory."""
    try:
        errors = []
        warnings = []

        # Check database ICPs vs memory ICPs
        db_icps = (
            db_client.table("icp_profiles")
            .select("*")
            .eq("workspace_id", workspace_id)
            .execute()
        )
        db_icp_count = len(db_icps.data) if db_icps.data else 0

        memory_icps = await memory_controller.search(
            workspace_id=workspace_id, query="icp", memory_types=["icp"], limit=100
        )
        memory_icp_count = len(memory_icps)

        if abs(db_icp_count - memory_icp_count) > 5:  # Allow some tolerance
            warnings.append(
                f"ICP count mismatch: DB={db_icp_count}, Memory={memory_icp_count}"
            )

        # Check foundation consistency
        db_foundation = (
            db_client.table("foundations")
            .select("*")
            .eq("workspace_id", workspace_id)
            .execute()
        )
        if db_foundation.data:
            foundation_id = db_foundation.data[0]["id"]

            memory_foundation = await memory_controller.search(
                workspace_id=workspace_id,
                query=foundation_id,
                memory_types=["foundation"],
                limit=10,
            )

            if not memory_foundation:
                warnings.append("Foundation not found in memory")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "summary": {
                "db_icp_count": db_icp_count,
                "memory_icp_count": memory_icp_count,
                "foundation_synced": bool(memory_foundation),
            },
        }

    except Exception as e:
        return {"valid": False, "error": str(e)}


async def _check_orphaned_moves(workspace_id: str, db_client) -> int:
    """Check for orphaned move records."""
    try:
        # Get all moves
        moves_result = (
            db_client.table("moves")
            .select("id", "campaign_id")
            .eq("workspace_id", workspace_id)
            .execute()
        )

        if not moves_result.data:
            return 0

        orphaned_count = 0
        for move in moves_result.data:
            if move["campaign_id"] and move["campaign_id"] != "":
                # Check if campaign exists
                campaign_result = (
                    db_client.table("campaigns")
                    .select("id")
                    .eq("id", move["campaign_id"])
                    .eq("workspace_id", workspace_id)
                    .execute()
                )
                if not campaign_result.data:
                    orphaned_count += 1

        return orphaned_count

    except Exception:
        return 0


async def validate_agent_state(state: AgentState) -> Dict[str, Any]:
    """
    Validate agent state integrity.

    Args:
        state: Agent state to validate

    Returns:
        Validation results
    """
    try:
        errors = []
        warnings = []

        # Check required fields
        required_fields = ["workspace_id", "user_id", "session_id"]
        for field in required_fields:
            if field not in state or not state[field]:
                errors.append(f"Missing required field: {field}")

        # Check data types
        if "tokens_used" in state and not isinstance(
            state["tokens_used"], (int, float)
        ):
            errors.append("tokens_used must be numeric")

        if "cost_usd" in state and not isinstance(state["cost_usd"], (int, float)):
            errors.append("cost_usd must be numeric")

        # Check message format
        if "messages" in state:
            if not isinstance(state["messages"], list):
                errors.append("messages must be a list")
            else:
                for i, message in enumerate(state["messages"]):
                    if not isinstance(message, dict):
                        errors.append(f"Message {i} must be a dict")
                    elif "role" not in message or "content" not in message:
                        errors.append(f"Message {i} missing required fields")

        # Check routing path
        if "routing_path" in state and state["routing_path"]:
            if not isinstance(state["routing_path"], list):
                errors.append("routing_path must be a list")

        # Check memory context
        if "memory_context" in state and state["memory_context"]:
            if not isinstance(state["memory_context"], list):
                errors.append("memory_context must be a list")

        # Warnings for optional but recommended fields
        recommended_fields = ["current_agent", "goal", "context"]
        for field in recommended_fields:
            if field not in state:
                warnings.append(f"Missing recommended field: {field}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "summary": {
                "has_required_fields": all(field in state for field in required_fields),
                "has_recommended_fields": all(
                    field in state for field in recommended_fields
                ),
                "messages_count": len(state.get("messages", [])),
                "has_routing_path": "routing_path" in state,
                "has_memory_context": "memory_context" in state,
            },
        }

    except Exception as e:
        return {"valid": False, "error": str(e)}


class ValidationService:
    """
    Service for performing system validations.
    """

    def __init__(self, db_client, memory_controller):
        self.db_client = db_client
        self.memory_controller = memory_controller
        self.validation_cache = {}

    async def validate_workspace(
        self, workspace_id: str, use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Validate workspace with optional caching.

        Args:
            workspace_id: Workspace ID
            use_cache: Whether to use cached results

        Returns:
            Validation results
        """
        if use_cache and workspace_id in self.validation_cache:
            cache_entry = self.validation_cache[workspace_id]
            if time.time() - cache_entry["timestamp"] < 300:  # 5 minute cache
                return cache_entry["results"]

        results = await validate_workspace_consistency(
            workspace_id, self.db_client, self.memory_controller
        )

        # Cache results
        if use_cache:
            self.validation_cache[workspace_id] = {
                "results": results,
                "timestamp": time.time(),
            }

        return results

    async def validate_agent(self, state: AgentState) -> Dict[str, Any]:
        """
        Validate agent state.

        Args:
            state: Agent state

        Returns:
            Validation results
        """
        return await validate_agent_state(state)

    async def run_health_check(self, workspace_id: str = None) -> Dict[str, Any]:
        """
        Run comprehensive health check.

        Args:
            workspace_id: Optional workspace ID to check

        Returns:
            Health check results
        """
        try:
            if workspace_id:
                return await self.validate_workspace(workspace_id, use_cache=False)
            else:
                # Check all workspaces (would need to get list first)
                return {"error": "Workspace ID required for specific validation"}

        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {"valid": False, "error": str(e)}

    async def clear_cache(self, workspace_id: str = None):
        """
        Clear validation cache.

        Args:
            workspace_id: Optional workspace ID to clear
        """
        if workspace_id and workspace_id in self.validation_cache:
            del self.validation_cache[workspace_id]
        else:
            self.validation_cache.clear()

        logger.info(f"Cleared validation cache for {workspace_id or 'all workspaces'}")
