import logging
from typing import Any, Callable, Dict, List, Optional

from swarm import Agent as OpenAI_Swarm_Agent

from agents.base import BaseCognitiveAgent
from core.agent_monitor import get_agent_health_monitor
from core.thought_cache import get_thought_cache
from core.token_governor import get_token_governor
from models.cognitive import AgentMessage, CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.swarm")


class SwarmAgent(BaseCognitiveAgent):
    """
    Industrial wrapper for OpenAI Swarm Agents.
    Inherits SOTA features (DNA, tokens, cache) while providing Swarm compatibility.
    """

    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        model_tier: str = "driver",
        functions: Optional[List[Callable]] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            role=role,
            system_prompt=system_prompt,
            model_tier=model_tier,
            **kwargs,
        )

        # Swarm library expects a standard Agent object
        self.functions = functions or []
        self._swarm_agent = None

    def get_swarm_agent(self, workspace_id: Optional[str] = None) -> OpenAI_Swarm_Agent:
        """
        Dynamically produces an OpenAI Swarm Agent object with injected DNA.
        """
        # Note: We can't easily await in this sync property if we want to follow Swarm's pattern
        # But we can pre-fetch DNA or use a factory pattern.
        # For now, we'll use the base system prompt and let the orchestrator handle injection.

        return OpenAI_Swarm_Agent(
            name=self.name, instructions=self.system_prompt, functions=self.functions
        )

    async def execute_swarm_node(
        self, swarm_client: Any, state: CognitiveIntelligenceState
    ) -> Dict[str, Any]:
        """
        Executes this agent within a swarm context, handling all reliability layers.
        """
        workspace_id = state.get("workspace_id")

        # 1. Token Check
        governor = get_token_governor()
        if not await governor.check_budget(workspace_id):
            return {"error": "Budget Exceeded"}

        # 2. Cache Check
        cache = get_thought_cache()
        msg_dicts = [
            {"role": m.role, "content": m.content} for m in state.get("messages", [])
        ]
        cached = await cache.get(self.role, msg_dicts)
        if cached:
            return cached

        # 3. DNA Injection
        heuristics = await self._get_heuristics_prompt(workspace_id)
        exploits = await self._get_exploits_prompt(workspace_id)

        full_instructions = self.system_prompt
        if heuristics:
            full_instructions += f"\n\n# HEURISTICS:\n{heuristics}"
        if exploits:
            full_instructions += f"\n\n# PAST WINS:\n{exploits}"

        agent = OpenAI_Swarm_Agent(
            name=self.name, instructions=full_instructions, functions=self.functions
        )

        # 4. Run Swarm
        # Swarm's run is typically sync but we'll wrap it or use its async counterpart if available
        # Note: Official openai/swarm is currently sync-first
        response = swarm_client.run(
            agent=agent,
            messages=msg_dicts,
            context_variables=state.get("context_variables", {}),
        )

        content = response.messages[-1]["content"]

        # 5. Health Audit
        monitor = get_agent_health_monitor()
        await monitor.audit_response(self.name, content, {})

        # 6. Record usage
        # (Simplified for now, real implementation would extract tokens from response)
        await governor.record_usage(workspace_id, 1000)

        return {
            "messages": [AgentMessage(role=self.role, content=content)],
            "context_variables": response.context_variables,
        }
