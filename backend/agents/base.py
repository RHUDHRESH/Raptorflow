import logging
from abc import ABC
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional, Type

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from agents.tool_integration import get_agent_tools
from db import fetch_heuristics
from inference import InferenceProvider
from memory.swarm_coordinator import get_swarm_memory_coordinator
from models.capabilities import CapabilityProfile
from models.cognitive import AgentMessage, CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.base")


class BaseCognitiveAgent(ABC):
    """
    Industrial-grade Base Agent Class.
    Handles tool calling, unified logging, and state management.
    """

    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        model_tier: str = "driver",
        tools: Optional[List[BaseTool]] = None,
        output_schema: Optional[Type[BaseModel]] = None,
        capability_profile: Optional[CapabilityProfile] = None,
        auto_assign_tools: bool = True,
    ):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model_tier = model_tier
        self.capability_profile = capability_profile

        # Auto-assign tools based on role if no tools provided
        if auto_assign_tools and not tools:
            self.tools = self._filter_tools(get_agent_tools(role))
        else:
            self.tools = self._filter_tools(tools or [])

        self.output_schema = output_schema

        self.llm = InferenceProvider.get_model(model_tier=self.model_tier)
        self.memory_coordinator = None  # Will be initialized during execution

        if self.tools:
            self.llm_with_tools = self.llm.bind_tools(self.tools)
        else:
            self.llm_with_tools = self.llm

        if self.output_schema:
            self.llm_with_structured = self.llm.with_structured_output(
                self.output_schema
            )
        else:
            self.llm_with_structured = self.llm

    def _filter_tools(self, tools: List[BaseTool]) -> List[BaseTool]:
        if not self.capability_profile:
            return tools
        return [
            tool
            for tool in tools
            if self.capability_profile.allows_tool(getattr(tool, "name", ""))
        ]

    async def _get_heuristics_prompt(self, workspace_id: Optional[str]) -> str:
        """Fetches heuristics from DB and formats them for the prompt."""
        if not workspace_id:
            return ""
        try:
            heuristics = await fetch_heuristics(workspace_id, self.role)
            lines = []
            if heuristics.get("never_rules"):
                lines.append("# NEVER RULES:")
                lines.extend([f"- {r}" for r in heuristics["never_rules"]])
            if heuristics.get("always_rules"):
                lines.append("# ALWAYS RULES:")
                lines.extend([f"- {r}" for r in heuristics["always_rules"]])
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Failed to fetch heuristics for {self.role}: {e}")
            return ""

    def _format_messages(self, state_messages: List[AgentMessage]) -> List[BaseMessage]:
        """Converts internal AgentMessage to LangChain messages."""
        lc_messages = [SystemMessage(content=self.system_prompt)]
        for m in state_messages:
            if m.role == "human":
                lc_messages.append(HumanMessage(content=m.content))
            elif m.role == self.role:
                lc_messages.append(AIMessage(content=m.content))
            else:
                lc_messages.append(AIMessage(content=f"[{m.role}]: {m.content}"))
        return lc_messages

    async def self_correct(
        self, content: str, state: CognitiveIntelligenceState
    ) -> str:
        """
        SOTA Self-Correction Loop.
        Critiques own output and refines it based on industrial standards.
        """
        logger.info(f"Agent {self.name} performing self-correction...")

        # 1. Generate Critique
        critique_prompt = f"""
        # ROLE: Ruthless Editorial Skeptic
        # TASK: Critique the following content for {self.role} quality.
        # CONTENT: {content}
        # CRITERIA: Factual density, brand alignment, logic gaps.
        """
        critique_res = await self.llm.ainvoke([SystemMessage(content=critique_prompt)])
        critique = critique_res.content

        # 2. Refine based on critique
        refine_prompt = f"""
        # TASK: Refine the content based on this critique: {critique}
        # ORIGINAL CONTENT: {content}
        # OUTPUT: Return the final polished content only.
        """
        refine_res = await self.llm.ainvoke([SystemMessage(content=refine_prompt)])

        return refine_res.content

    async def astream(self, state: CognitiveIntelligenceState) -> AsyncIterator[Any]:
        """
        Streaming node execution logic.
        Yields content chunks for real-time UI updates.
        """
        logger.info(f"Agent {self.name} ({self.role}) streaming...")
        messages = self._format_messages(state.get("messages", []))

        async for chunk in self.llm_with_tools.astream(messages):
            yield chunk

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """
        Node execution logic with token tracking and memory integration.
        """
        logger.info(f"Agent {self.name} ({self.role}) executing...")

        # Initialize memory coordinator if needed
        workspace_id = state.get("workspace_id")
        if workspace_id and not self.memory_coordinator:
            self.memory_coordinator = get_swarm_memory_coordinator(workspace_id)

            # Register agent with memory system
            await self.memory_coordinator.initialize_agent_memory(
                agent_id=self.name, agent_type=self.role
            )

        # Fetch and inject heuristics
        heuristics_prompt = await self._get_heuristics_prompt(workspace_id)

        messages = self._format_messages(state.get("messages", []))

        # Inject heuristics into system message if found
        if heuristics_prompt and messages:
            if isinstance(messages[0], SystemMessage):
                messages[
                    0
                ].content += f"\n\n# ADDITIONAL HEURISTICS:\n{heuristics_prompt}"

        # If output schema is set, use structured output
        if self.output_schema:
            response = await self.llm_with_structured.ainvoke(messages)
            content = (
                str(response.model_dump())
                if hasattr(response, "model_dump")
                else str(response)
            )
            # Metadata for structured output might be nested differently
            metadata = (
                getattr(response, "response_metadata", {})
                if hasattr(response, "response_metadata")
                else {}
            )
        else:
            response = await self.llm_with_tools.ainvoke(messages)
            content = response.content
            metadata = getattr(response, "response_metadata", {})

        # Extract Token Usage (Vertex AI pattern)
        token_usage = metadata.get("token_usage", {})
        input_tokens = token_usage.get("prompt_token_count", 0)
        output_tokens = token_usage.get("candidates_token_count", 0)

        logger.info(f"Agent {self.name} tokens: {input_tokens} in, {output_tokens} out")

        # Record agent execution in memory system
        if self.memory_coordinator:
            await self.memory_coordinator.record_agent_memory(
                agent_id=self.name,
                content={
                    "task": state.get("instructions", ""),
                    "result": content,
                    "tokens_used": {"input": input_tokens, "output": output_tokens},
                    "model_tier": self.model_tier,
                },
                importance=0.6,  # Medium importance for agent outputs
                metadata={
                    "agent_type": self.role,
                    "workspace_id": workspace_id,
                    "execution_timestamp": str(datetime.now()),
                },
            )

        return {
            "messages": [AgentMessage(role=self.role, content=content)],
            "last_agent": self.name,
            "token_usage": {
                f"{self.name}_input": input_tokens,
                f"{self.name}_output": output_tokens,
            },
        }
