import logging
from typing import Any, Dict, Optional

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from backend.core.config import get_settings
from backend.memory.swarm_learning import SwarmLearningMemory
from backend.skills.matrix_skills import SkillRegistry

logger = logging.getLogger("raptorflow.matrix.agents")


class SkillSelection(BaseModel):
    """Structured output for skill selection."""

    skill_name: str = Field(
        description="The name of the skill to execute, or 'none' if no match."
    )
    reasoning: str = Field(
        description="Brief explanation for why this skill was chosen."
    )


class SkillSelectorAgent:
    """
    SOTA Agent for selecting the best deterministic skill for a given intent.
    Uses few-shot prompting and structured output for reliability.
    """

    def __init__(self, llm: Any, registry: SkillRegistry):
        self.llm = llm
        self.registry = registry
        self.memory = SwarmLearningMemory()
        self.settings = get_settings()

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are the Matrix Skill Selector.
Your job is to map a user's intent or a system situation to the most appropriate deterministic skill.

Available Skills:
{skill_descriptions}

Rules:
1. Only select from the available skills list.
2. If no skill is a clear match, return 'none'.
3. Prioritize 'emergency_halt' for any mention of stopping, killing, or system failure.

Feedback to bias selection:
{feedback_context}
""",
                ),
                ("human", "{intent}"),
            ]
        )

    async def pick_best_tool(
        self, intent: str, workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes the intent and selects the optimal skill from the registry.
        """
        logger.info(f"SkillSelector analyzing intent: {intent}")

        # In a real build, we'd fetch descriptions for each skill.
        # For now, we list the registered names.
        skills = self.registry.list_skills()
        skill_descriptions = "\n".join([f"- {s}" for s in skills])
        feedback_context = await self._get_feedback_context(intent, workspace_id)

        chain = self.prompt.partial(
            skill_descriptions=skill_descriptions,
            feedback_context=feedback_context or "None",
        ) | self.llm.with_structured_output(SkillSelection)

        try:
            response = await chain.ainvoke({"intent": intent})
            return {"skill_name": response.skill_name, "reasoning": response.reasoning}
        except Exception as e:
            logger.error(f"Skill selection failed: {e}")
            return {"skill_name": "none", "reasoning": f"Error: {str(e)}"}

    async def _get_feedback_context(
        self, intent: str, workspace_id: Optional[str]
    ) -> str:
        resolved_workspace_id = workspace_id or self.settings.DEFAULT_TENANT_ID
        if not resolved_workspace_id:
            return ""

        feedback = await self.memory.recall_feedback(
            workspace_id=resolved_workspace_id, query=intent, limit=3
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
