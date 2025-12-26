from typing import List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from core.config import get_settings
from inference import InferenceProvider
from memory.swarm_learning import SwarmLearningMemory


class RouterOutput(BaseModel):
    asset_type: str = Field(
        description="The family of asset (email, social, meme, strategy)"
    )
    confidence: float = Field(description="Confidence score 0.0 - 1.0")
    extracted_goal: str = Field(description="What the user wants to achieve")
    entities: List[str] = Field(
        description="Extracted @mentions like cohorts or campaigns"
    )
    ambiguity_reasons: Optional[List[str]] = Field(
        description="Reasons for low confidence"
    )


class IntentRouterAgent:
    def __init__(self):
        # Use the 'fast' tier for routing
        self.llm = InferenceProvider.get_model(
            model_tier="fast", temperature=0.0
        ).with_structured_output(RouterOutput)
        self.memory = SwarmLearningMemory()
        self.settings = get_settings()

    async def route(self, prompt: str, workspace_id: Optional[str] = None) -> RouterOutput:
        feedback_context = await self._get_feedback_context(prompt, workspace_id)
        system_msg = SystemMessage(
            content="""
            You are the Intent Router for RaptorFlow.
            Classify user prompts into asset families: email, social, meme, or strategy.
            Extract @mentions which represent campaigns, cohorts, or competitors.
            Assign confidence based on how much detail is provided.
            If the prompt is vague (e.g. 'write an email'), confidence must be < 0.7.
            Use relevant feedback from similar requests to bias routing decisions.
        """
        )
        if feedback_context:
            system_msg = SystemMessage(
                content=f"""{system_msg.content}

Relevant feedback:
{feedback_context}
"""
            )

        return await self.llm.ainvoke([system_msg, HumanMessage(content=prompt)])

    async def _get_feedback_context(
        self, prompt: str, workspace_id: Optional[str]
    ) -> str:
        resolved_workspace_id = workspace_id or self.settings.DEFAULT_TENANT_ID
        if not resolved_workspace_id:
            return ""

        feedback = await self.memory.recall_feedback(
            workspace_id=resolved_workspace_id, query=prompt, limit=3
        )
        if not feedback:
            return ""

        return "\n".join(self._format_feedback_entry(entry) for entry in feedback)

    @staticmethod
    def _format_feedback_entry(entry: dict) -> str:
        metadata = entry.get("metadata", {}) or {}
        signal = metadata.get("signal", "neutral")
        tool_hint = metadata.get("tool_hint") or "n/a"
        agent_hint = metadata.get("agent_hint") or "n/a"
        context = metadata.get("context") or "n/a"
        content = entry.get("content", "")
        return (
            f"- [{signal}] tool={tool_hint} agent={agent_hint} "
            f"context={context} feedback={content}"
        )
