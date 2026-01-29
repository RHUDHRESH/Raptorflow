"""
Conflict Resolver Node - Strategic Alignment logic
Prevents contradictory moves within the same campaign agenda.
"""

import logging
from typing import Any, Dict

from synapse import brain

from .agents.skills.registry import get_skills_registry

logger = logging.getLogger("conflict_resolver_node")


@brain.register("conflict_resolver_node")
async def conflict_resolver_node(context: Dict) -> Dict:
    """
    Expert node that scans for overlaps or contradictions in concurrent moves.
    """
    logger.info("🧠 Node: Auditing concurrent moves for alignment.")

    # 1. Get the skill from registry
    skills = get_skills_registry()
    resolver_skill = skills.get_skill("conflict_resolver")

    if not resolver_skill:
        return {"status": "error", "error": "Conflict Resolver skill not found"}

    # 2. Execute skill (which calls the LLM to analyze the move list in context)
    # We pass the moves and the agent reference (Synapse uses brain, nodes use context)
    result = await resolver_skill.execute(context)

    return {"status": "success", "data": result}
