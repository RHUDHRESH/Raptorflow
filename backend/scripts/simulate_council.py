import asyncio
import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch

from graphs.council import get_expert_council_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("raptorflow.simulator")


async def run_simulation():
    """
    Runs a full Expert Council simulation with mock agents and tools.
    """
    logger.info("\U0001f680 Starting Expert Council Simulator...")

    # Mock JSON Response
    mock_json = json.dumps(
        {
            "alignment": 0.92,
            "confidence": 0.88,
            "confidence_score": 92,
            "risk": 0.1,
            "decree": "Simulated Decree: Focus on high-value organic growth.",
            "rationale": "ROI is predicted to be 4.2x higher than current baseline.",
            "impact": 0.9,
            "recommendation": "Execute immediately.",
            "score": 0.95,
            "rejected_paths": [{"path": "Paid Ads", "reason": "High CAC"}],
            "campaign_arc": {
                "title": "Simulator Campaign",
                "objective": "Test RaptorFlow",
                "arc_data": {"phases": ["Start", "Middle", "End"]},
            },
            "moves": [{"title": "Sim Move", "description": "Step 1", "type": "ops"}],
            "tool_requirements": ["brave_search"],
            "muse_prompt": "Create simulator asset",
            "reasoning": "Simulation data looks consistent.",
        }
    )

    mock_agent = AsyncMock()
    mock_agent.side_effect = lambda s: {"messages": [MagicMock(content=mock_json)]}

    with (
        patch("graphs.council.get_council_agents", return_value=[mock_agent] * 12),
        patch(
            "graphs.council.RadarEventsTool",
            return_value=MagicMock(
                run=AsyncMock(
                    return_value={"success": True, "data": {"found_events": []}}
                )
            ),
        ),
        patch(
            "graphs.council.RadarCompetitorsTool",
            return_value=MagicMock(
                run=AsyncMock(
                    return_value={"success": True, "data": {"competitors": []}}
                )
            ),
        ),
        patch(
            "graphs.council.save_reasoning_chain", AsyncMock(return_value="chain_sim")
        ),
        patch("graphs.council.save_rejections", AsyncMock(return_value=None)),
        patch("graphs.council.save_campaign", AsyncMock(return_value="camp_sim")),
        patch("graphs.council.save_move", AsyncMock(return_value="move_sim")),
        patch("graphs.council.update_move_description", AsyncMock(return_value=None)),
        patch(
            "agents.base.get_swarm_memory_coordinator",
            return_value=MagicMock(
                initialize_agent_memory=AsyncMock(), record_agent_memory=AsyncMock()
            ),
        ),
        patch(
            "db.fetch_heuristics",
            AsyncMock(return_value={"never_rules": [], "always_rules": []}),
        ),
        patch("db.fetch_exploits", AsyncMock(return_value=[])),
    ):

        graph = get_expert_council_graph().compile()

        initial_state = {
            "workspace_id": "sim_workspace",
            "brief": {"goals": "simulated test", "target_icp": "developers"},
            "messages": [],
            "status": "idle",
        }

        logger.info("Chamber Initialized. Invoking Graph...")
        final_state = await graph.ainvoke(initial_state, config={"recursion_limit": 50})

        logger.info("\u2705 Simulation Complete.")
        logger.info(
            f"Consensus Alignment: {final_state.get('consensus_metrics', {}).get('alignment')}"
        )
        logger.info(f"FinalDecree: {final_state.get('final_strategic_decree')}")
        logger.info(f"Moves Propagated: {len(final_state.get('move_ids', []))}")


if __name__ == "__main__":
    asyncio.run(run_simulation())
