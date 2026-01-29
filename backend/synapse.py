#!/usr/bin/env python3
"""
Synapse 2.0: The Cognitive Spine
Refactored for Absolute Infinity with Supabase persistence.
Coordinates specialized agents and skills across the strategic graph.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, UTC

from core.supabase_mgr import get_supabase_client
from core.auth import get_auth_context

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Synapse")


class Synapse:
    """
    The Brain that connects all nodes.
    Now backed by Supabase JSONB for industrial persistence and auditability.
    """

    def __init__(self):
        self.nodes: Dict[str, Callable] = {}
        self.client = get_supabase_client()
        logger.info("🧠 Synapse 2.0 initialized with Supabase persistence")

    def register(self, name: str):
        """Decorator to register a node function"""

        def decorator(func):
            self.nodes[name] = func
            logger.info(f"🔌 Node Registered: {name}")
            return func

        return decorator

    async def save_state(self, flow_id: str, context: Dict, workspace_id: str):
        """Saves current context to Supabase campaign_arcs current_pulse"""
        try:
            # We use campaign_arcs as the primary pulse storage
            # Fallback to a generic session state if arc_id isn't provided
            payload = {
                "id": flow_id,
                "workspace_id": workspace_id,
                "state": context,
                "updated_at": datetime.now(UTC).isoformat(),
            }

            # Using upsert logic for the pulse
            self.client.table("campaign_arcs").upsert(
                {
                    "id": flow_id,
                    "workspace_id": workspace_id,
                    "current_pulse": context,
                    "updated_at": datetime.now(UTC).isoformat(),
                }
            ).execute()

        except Exception as e:
            logger.error(f"❌ Synapse: Failed to save state to Supabase: {e}")

    async def load_state(self, flow_id: str) -> Dict:
        """Loads context from Supabase"""
        try:
            result = (
                self.client.table("campaign_arcs")
                .select("current_pulse")
                .eq("id", flow_id)
                .single()
                .execute()
            )
            return result.data.get("current_pulse", {}) if result.data else {}
        except Exception as e:
            logger.error(f"❌ Synapse: Failed to load state: {e}")
            return {}

    async def log_thought(
        self,
        entity_id: str,
        entity_type: str,
        agent_name: str,
        thought: str,
        workspace_id: str,
        tokens: int = 0,
    ):
        """Log agent reasoning to the persistent audit trail"""
        try:
            self.client.table("agent_thought_logs").insert(
                {
                    "workspace_id": workspace_id,
                    "entity_id": entity_id,
                    "entity_type": entity_type,
                    "agent_name": agent_name,
                    "thought_process": thought,
                    "tokens_used": tokens,
                    "created_at": datetime.now(UTC).isoformat(),
                }
            ).execute()
        except Exception as e:
            logger.error(f"❌ Synapse: Failed to log thought: {e}")

    async def run_node(self, node_name: str, context: Dict, flow_id: str = "temp"):
        """Executes a single node with telemetry and state sync"""
        if node_name not in self.nodes:
            raise ValueError(f"❌ Node '{node_name}' not found")

        workspace_id = context.get("workspace_id")
        if not workspace_id:
            logger.warning(
                "⚠️ Synapse: No workspace_id in context. Persistence may fail."
            )

        logger.info(f"⚡ Synapse: Firing node '{node_name}'")
        start_time = datetime.now(UTC)

        try:
            # Execute the node
            node_func = self.nodes[node_name]
            result = await node_func(context)

            # Update context with result
            if isinstance(result, dict):
                if "data" in result:
                    context.update(result["data"])

                # Metadata updates
                for key in ["status", "next_step", "error"]:
                    if key in result:
                        context[key] = result[key]

            # Log successful execution to telemetry
            execution_time = (datetime.now(UTC) - start_time).total_seconds()
            context["last_node_execution_ms"] = int(execution_time * 1000)

            # Save state if flow_id is valid
            if flow_id != "temp" and workspace_id:
                await self.save_state(flow_id, context, workspace_id)

            return context

        except Exception as e:
            logger.error(f"🔥 Error in node '{node_name}': {e}")
            context["error"] = str(e)
            return context

    async def run_sequence(
        self, node_list: List[str], context: Dict, flow_id: str = "temp"
    ):
        """Executes a list of nodes in order (For Moves)"""
        logger.info(f"🚀 Starting Sequence: {node_list}")
        for node in node_list:
            context = await self.run_node(node, context, flow_id)
            if "error" in context:
                logger.error(f"🛑 Sequence halted at '{node}' due to error.")
                break
        return context

    async def run_move(self, move_name: str, context: Dict, flow_id: str = "temp"):
        """Executes a strategic move sequence based on definitions"""
        logger.info(f"♟️ Executing Move: {move_name}")

        # 1. Fetch move sequence definition (In Phase 6 this moves to a 'move_definitions' table)
        # For now, we maintain the registry but it will be dynamic.
        move_sequences = {
            "market_research": ["research_node", "strategy_node"],
            "content_creation": ["content_creator", "seo_skill"],
            "competitive_analysis": [
                "research_node",
                "strategy_node",
                "content_creator",
            ],
            "product_launch": [
                "research_node",
                "strategy_node",
                "content_creator",
                "seo_skill",
            ],
        }

        if move_name not in move_sequences:
            raise ValueError(f"❌ Move '{move_name}' not defined in Synapse registry")

        sequence = move_sequences[move_name]
        return await self.run_sequence(sequence, context, flow_id)


# Global Brain Instance
brain = Synapse()
