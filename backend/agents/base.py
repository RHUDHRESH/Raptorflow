import logging
from typing import List, Dict, Any, Optional, Type, Union
from abc import ABC, abstractmethod
from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from backend.inference import InferenceProvider
from backend.models.cognitive import CognitiveIntelligenceState, AgentMessage

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
        output_schema: Optional[Type[BaseModel]] = None
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
            self.llm_with_structured = self.llm.with_structured_output(self.output_schema)
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

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """
        Node execution logic.
        Can be overridden for complex logic or tool execution flows.
        """
        logger.info(f"Agent {self.name} ({self.role}) executing...")

        messages = self._format_messages(state.get("messages", []))

        # If output schema is set, use structured output
        if self.output_schema:
            response = await self.llm_with_structured.ainvoke(messages)
            content = str(response.model_dump()) if hasattr(response, "model_dump") else str(response)
        else:
            response = await self.llm_with_tools.ainvoke(messages)
            content = response.content

        return {
            "messages": [AgentMessage(role=self.role, content=content)],
            "last_agent": self.name
        }
