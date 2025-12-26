import logging
from typing import Any, Dict, List

from agents.supervisor import HierarchicalSupervisor
from agents.swarm_decomposer import SwarmTaskDecomposer
from models.swarm import SwarmState

logger = logging.getLogger("raptorflow.agents.swarm_controller")


class SwarmController:
    """
    Swarm Controller that decomposes missions before routing to specialists.
    """

    def __init__(
        self,
        llm: Any,
        team_members: List[str],
        system_prompt: str,
        decomposer: SwarmTaskDecomposer | None = None,
    ):
        self.decomposer = decomposer or SwarmTaskDecomposer(llm)
        self.supervisor = HierarchicalSupervisor(llm, team_members, system_prompt)

    async def route(self, state: SwarmState) -> Dict[str, Any]:
        """
        Ensures decomposition runs before routing to specialists.
        """
        if not state.get("subtask_specs"):
            logger.info("SwarmController running decomposition before routing.")
            decomposition = await self.decomposer(state)
            state = {**state, **decomposition}

        return await self.supervisor(state)

    async def execute(self, state: SwarmState, nodes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the swarm loop with decomposition enforced up front.
        """
        if not state.get("subtask_specs"):
            logger.info("SwarmController running decomposition before execution loop.")
            decomposition = await self.decomposer(state)
            state = {**state, **decomposition}

        return await self.supervisor.execute_loop(state, nodes)
