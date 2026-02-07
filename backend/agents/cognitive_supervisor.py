import logging
from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

from inference import InferenceProvider
from models.cognitive import AgentMessage, CognitiveIntelligenceState, CognitiveStatus

logger = logging.getLogger("raptorflow.agents.cognitive_supervisor")


class SupervisorDecision(BaseModel):
    """SOTA Decision schema for the Cognitive Supervisor."""

    next_action: str = Field(
        description="The next status or node to transition to: 'planning', 'researching', 'execution', or 'complete'."
    )
    rationale: str = Field(description="Reasoning for the delegation decision.")
    crew_instructions: str = Field(
        description="Specific surgical instructions for the chosen crew."
    )


class CognitiveSupervisor:
    """
    Industrial-grade Supervisor Agent.
    Coordinates the Cognitive Intelligence Engine's specialized crews.
    """

    def __init__(self, llm: Optional[Any] = None):
        self.llm = llm or InferenceProvider.get_model(model_tier="driver")
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                You are the Cognitive Intelligence Supervisor for RaptorFlow.
                Your mission is to orchestrate a high-performance marketing engine.

                CREWS AVAILABLE:
                1. Planning: Strategic synthesis, ICP profiling, goal setting.
                2. Researching: Web scraping (Firecrawl/Jina), trend analysis, competitor mapping.
                3. Execution: Asset generation (Copy, Image, Layout), Move orchestration.

                CRITERIA:
                - If the prompt is new, start with Planning.
                - If the plan exists but lacks data, move to Researching.
                - If data is validated, move to Execution.
                - If quality is low (<0.7), loop back to Researching.
                - If all steps are high-quality, mark as Complete.
            """,
                ),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "user",
                    "Current Status: {status}. Quality Score: {quality_score}. Decide the next strategic move.",
                ),
            ]
        )
        self._chain = None

    @property
    def chain(self):
        if self._chain is None:
            self._chain = self.prompt | self.llm.with_structured_output(
                SupervisorDecision
            )
        return self._chain

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes the supervisor reasoning loop."""
        logger.info("Supervisor evaluating engine state...")

        # Convert AgentMessages to LangChain messages for the prompt
        lc_messages = []
        for m in state.get("messages", []):
            if m.role == "human":
                lc_messages.append(HumanMessage(content=m.content))
            else:
                lc_messages.append(AIMessage(content=f"[{m.role}]: {m.content}"))

        decision = await self.chain.ainvoke(
            {
                "messages": lc_messages,
                "status": state.get("status"),
                "quality_score": state.get("quality_score", 0.0),
            }
        )

        logger.info(
            f"Supervisor Decision: {decision.next_action}. Rationale: {decision.rationale}"
        )

        status_map = {
            "planning": CognitiveStatus.PLANNING,
            "researching": CognitiveStatus.RESEARCHING,
            "execution": CognitiveStatus.EXECUTING,
            "complete": CognitiveStatus.COMPLETE,
        }

        target_action = decision.next_action.lower()
        new_status = status_map.get(target_action, state["status"])

        return {
            "status": new_status,
            "next_node": target_action,
            "messages": [
                AgentMessage(
                    role="supervisor",
                    content=f"DELEGATE: {target_action}. {decision.crew_instructions}",
                )
            ],
        }
