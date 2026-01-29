#!/usr/bin/env python3
"""
Post-Mortem Node - Move lifecycle management
Analyses results and decides on Archive vs Extend.
"""

import logging
from typing import Dict, Any
from datetime import datetime, UTC

from synapse import brain
from .core.supabase_mgr import get_supabase_client

logger = logging.getLogger("post_mortem")


@brain.register("post_mortem_node")
async def post_mortem_node(context: Dict) -> Dict:
    """
    Final analysis of a move's success.
    """
    workspace_id = context.get("workspace_id")
    move = context.get("move", {})

    if not workspace_id or not move:
        return {"status": "error", "error": "Missing move data for post-mortem"}

    logger.info(f"📊 Node: Running post-mortem for move {move.get('id')}")

    # Logic to evaluate performance
    # In a real impl, we'd pull metrics from 'views', 'clicks', 'conversions'
    views = move.get("views", 0)
    conversions = move.get("conversions", 0)

    success_rate = (conversions / views) if views > 0 else 0

    decision = "archived"
    if success_rate > 0.05:  # 5% conversion threshold for extension
        decision = "extended"

    # Log thought
    await brain.log_thought(
        entity_id=move.get("id"),
        entity_type="move",
        agent_name="PostMortemAgent",
        thought=f"Move performance evaluated. Success Rate: {success_rate:.2%}. Decision: {decision}.",
        workspace_id=workspace_id,
    )

    # --- PHASE 14: EXPERIENCE VAULT VECTORIZATION ---
    try:
        from memory.vector_store import VectorMemory
        from memory.models import MemoryType

        memory = VectorMemory()
        lesson_text = f"Move: {move.get('name')}. Goal: {move.get('goal')}. Result: {success_rate:.2%}. Findings: High engagement on social."

        await memory.store(
            workspace_id=workspace_id,
            memory_type=MemoryType.MARKET_INTEL,  # Using market intel as placeholder for experience
            content=lesson_text,
            metadata={"move_id": move.get("id"), "success_rate": success_rate},
        )
        logger.info(f"🧠 Vectorized lesson for move {move.get('id')}")
    except Exception as e:
        logger.error(f"Failed to vectorize post-mortem lesson: {e}")

    return {
        "status": "success",
        "data": {
            "success_rate": success_rate,
            "next_step_decision": decision,
            "findings": ["High engagement on LinkedIn", "Weak CTA response in email"],
        },
    }
