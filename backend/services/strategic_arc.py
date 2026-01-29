"""
Strategic Arc Logic Service: Handles move dependencies, synchronization, and expansion.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from db.moves import MoveRepository

from .core.supabase_mgr import get_supabase_client

logger = logging.getLogger(__name__)


class StrategicArcService:
    """Service for managing the hierarchical and sequential logic of campaign arcs."""

    def __init__(self):
        self.supabase = get_supabase_client()
        self.move_repo = MoveRepository()

    async def resolve_dependencies(
        self, workspace_id: str, move_id: str
    ) -> Dict[str, Any]:
        """
        Check if a move is blocked by dependencies.
        Sequential move locking logic.
        """
        try:
            # Query the move and its dependencies
            move_res = (
                await self.supabase.table("moves")
                .select("dependencies")
                .eq("id", move_id)
                .eq("workspace_id", workspace_id)
                .single()
                .execute()
            )

            if not move_res.data:
                return {"blocked": False, "reason": "Move not found"}

            dependencies = move_res.data.get("dependencies", [])
            if not dependencies:
                return {"blocked": False, "reason": "No dependencies"}

            # Check status of all dependency moves
            blocked_by = []
            for dep_id in dependencies:
                dep_res = (
                    await self.supabase.table("moves")
                    .select("status")
                    .eq("id", dep_id)
                    .single()
                    .execute()
                )
                if dep_res.data and dep_res.data.get("status") != "completed":
                    blocked_by.append(dep_id)

            if blocked_by:
                return {
                    "blocked": True,
                    "blocked_by": blocked_by,
                    "reason": "Dependencies not completed",
                }

            return {"blocked": False, "reason": "All dependencies satisfied"}
        except Exception as e:
            logger.error(f"Dependency resolution failed: {e}")
            return {"blocked": True, "error": str(e)}

    async def synchronize_moves(self, campaign_id: str) -> List[Dict[str, Any]]:
        """
        Move Synchronization (StrategicIndex).
        Ensures concurrent moves in a campaign are aligned.
        """
        try:
            # Fetch all moves for this campaign
            moves_res = (
                await self.supabase.table("moves")
                .select("*")
                .eq("campaign_id", campaign_id)
                .execute()
            )
            moves = moves_res.data or []

            # Implementation of 'Breathing Arcs' logic:
            # If one move is delayed, shift subsequent dependent moves.
            # (Stub for Phase 7 implementation)

            return moves
        except Exception as e:
            logger.error(f"Move synchronization failed: {e}")
            return []

    async def align_agendas(self, arc_id: str):
        """
        Ensures concurrent moves within the same agenda don't overlap or conflict.
        """
        logger.info(f"ArcResolver: Aligning agendas for arc {arc_id}")

        try:
            # 1. Fetch all active moves in this arc
            moves = (
                self.client.table("moves")
                .select("id, name, goal, metadata")
                .eq("arc_id", arc_id)
                .eq("status", "active")
                .execute()
            )
            active_moves = moves.data or []

            if len(active_moves) < 2:
                return

            # 2. Call the Conflict Resolver skill via Synapse
            # This ensures the agents check each other's work
            await brain.run_node(
                "conflict_resolver_node", {"arc_id": arc_id, "moves": active_moves}
            )

        except Exception as e:
            logger.error(f"Agenda alignment failed: {e}")

    async def expand_arc(self, move_id: str, workspace_id: str):
        """
        Dynamically extends an arc if a move was highly successful.
        """
        logger.info(f"ArcResolver: Expanding arc based on move {move_id} success.")

        try:
            # 1. Fetch the successful move
            move = (
                self.client.table("moves")
                .select("*")
                .eq("id", move_id)
                .single()
                .execute()
            )
            if not move.data or not move.data.get("arc_id"):
                return

            # 2. Call Strategist to generate 'Phase 2'
            # This adds new moves to the arc automatically
            await brain.run_node(
                "strategy_node",
                {
                    "workspace_id": workspace_id,
                    "arc_id": move.data["arc_id"],
                    "parent_move_id": move_id,
                    "goal": f"Scale success of {move.data['name']}",
                    "mode": "EXPANSION",
                },
            )

        except Exception as e:
            logger.error(f"Arc expansion failed: {e}")
