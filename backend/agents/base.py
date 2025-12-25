import logging
from abc import ABC
from typing import Any, AsyncIterator, Dict, List, Optional, Type

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from backend.inference import InferenceProvider
from backend.memory.peer_review import PeerReviewMemory
from backend.models.cognitive import AgentMessage, CognitiveIntelligenceState

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
    ):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model_tier = model_tier
        self.tools = tools or []
        self.output_schema = output_schema

        self.llm = InferenceProvider.get_model(model_tier=self.model_tier)

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
        self,
        content: str,
        state: CognitiveIntelligenceState,
        use_peer_critiques: bool = False,
    ) -> str:
        """
        SOTA Self-Correction Loop.
        Critiques own output and refines it based on industrial standards.
        """
        logger.info(f"Agent {self.name} performing self-correction...")

        peer_critiques = []
        if use_peer_critiques:
            peer_critiques = state.get("peer_critiques", []) or []
            tenant_id = state.get("tenant_id")
            if not peer_critiques and tenant_id:
                memory = PeerReviewMemory(tenant_id, state.get("workspace_id"))
                peer_critiques = await memory.get_recent_critiques()

        peer_section = ""
        if use_peer_critiques:
            formatted = "\n".join(
                [
                    f"- {item.get('reviewer', 'Peer')}: {item.get('critique', '')}"
                    for item in peer_critiques
                ]
            )
            peer_section = (
                "\n# PEER CRITIQUES:\n"
                + (formatted if formatted else "None available.")
            )

        # 1. Generate Critique
        critique_prompt = f"""
        # ROLE: Ruthless Editorial Skeptic
        # TASK: Critique the following content for {self.role} quality.
        # CONTENT: {content}
        {peer_section}
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
        Node execution logic with token tracking.
        """
        logger.info(f"Agent {self.name} ({self.role}) executing...")

        messages = self._format_messages(state.get("messages", []))

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

        return {
            "messages": [AgentMessage(role=self.role, content=content)],
            "last_agent": self.name,
            "token_usage": {
                f"{self.name}_input": input_tokens,
                f"{self.name}_output": output_tokens,
            },
        }
