import asyncio
import logging
from typing import Any, Dict, List

from agents.specialists.brand_philosopher import BrandPhilosopherAgent
from agents.specialists.community_catalyst import CommunityCatalystAgent
from agents.specialists.data_quant import DataQuantAgent
from agents.specialists.direct_response import DirectResponseAgent
from agents.specialists.media_buyer import MediaBuyerAgent
from agents.specialists.partnership import PartnershipAgent
from agents.specialists.pr_specialist import PRSpecialistAgent
from agents.specialists.product_lead import ProductLeadAgent
from agents.specialists.psychologist import PsychologistAgent
from agents.specialists.retention import RetentionAgent
from agents.specialists.seo_moat import SEOMoatAgent
from agents.specialists.viral_alchemist import ViralAlchemistAgent
from models.council import CouncilBlackboardState, CouncilThought

logger = logging.getLogger("raptorflow.graphs.council")


def get_council_agents() -> List[Any]:
    """Returns instances of all 12 Council Expert agents."""
    return [
        DirectResponseAgent(),
        ViralAlchemistAgent(),
        BrandPhilosopherAgent(),
        DataQuantAgent(),
        CommunityCatalystAgent(),
        MediaBuyerAgent(),
        SEOMoatAgent(),
        PRSpecialistAgent(),
        PsychologistAgent(),
        ProductLeadAgent(),
        PartnershipAgent(),
        RetentionAgent(),
    ]


async def council_debate_node(state: CouncilBlackboardState) -> Dict[str, Any]:
    """
    Council Debate Node: Parallel 'Thought' generation.
    Triggers all 12 experts to contribute their unique perspective to the blackboard.
    """
    logger.info("Council Chamber: Initiating parallel debate...")

    agents = get_council_agents()

    # Run all agents in parallel
    tasks = [agent(state) for agent in agents]
    results = await asyncio.gather(*tasks)

    new_thoughts = []
    for i, res in enumerate(results):
        agent = agents[i]
        # Extract the last message content as the 'thought'
        thought_content = (
            res["messages"][-1].content
            if res.get("messages")
            else "No thought generated."
        )

        thought = CouncilThought(
            agent_id=agent.name,
            content=thought_content,
            confidence=0.9,  # Default confidence, can be refined based on agent output
            tool_observations={},  # Can be extracted if agent used tools
        )
        new_thoughts.append(thought)

    return {"parallel_thoughts": new_thoughts, "last_agent": "Council_Chamber"}
