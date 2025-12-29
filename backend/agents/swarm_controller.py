import logging
from typing import Any, Dict, List

from swarm import Swarm

from agents.supervisor import get_swarm_supervisor
from db.swarm_context import load_swarm_context, save_swarm_context
from models.cognitive import AgentMessage

logger = logging.getLogger("raptorflow.agents.swarm_controller")


class SwarmOrchestrator:
    """
    SOTA Swarm Orchestrator using OpenAI Swarm.
    Manages the lifecycle of dynamic agent teams.
    """

    def __init__(self):
        self.client = Swarm()
        self.root_agent = get_swarm_supervisor()

    async def run_mission(
        self, prompt: str, workspace_id: str, context: dict = None
    ) -> Dict[str, Any]:
        """
        Runs a full swarm mission starting from the Supervisor.
        """
        logger.info(
            f"SwarmOrchestrator initiating mission for workspace: {workspace_id}"
        )

        # Load existing context from DB
        db_context = await load_swarm_context(workspace_id)

        # Initial context
        context_vars = {**db_context, **(context or {})}
        context_vars["workspace_id"] = workspace_id

        # Swarm library's run is sync, but we treat it as blocking here
        response = self.client.run(
            agent=self.root_agent,
            messages=[{"role": "user", "content": prompt}],
            context_variables=context_vars,
            debug=True,
        )

        # Persist updated context
        await save_swarm_context(workspace_id, response.context_variables)

        return {
            "messages": [
                AgentMessage(role=m["role"], content=m["content"])
                for m in response.messages
            ],
            "context_variables": response.context_variables,
            "last_agent": response.agent.name if response.agent else "Unknown",
        }


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
