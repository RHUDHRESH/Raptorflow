import logging
from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

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
""",
                ),
                ("human", "{intent}"),
            ]
        )

    async def pick_best_tool(self, intent: str) -> Dict[str, Any]:
        """
        Analyzes the intent and selects the optimal skill from the registry.
        """
        logger.info(f"SkillSelector analyzing intent: {intent}")

        # In a real build, we'd fetch descriptions for each skill.
        # For now, we list the registered names.
        skills = self.registry.list_skills()
        skill_descriptions = "\n".join([f"- {s}" for s in skills])

        chain = self.prompt.partial(
            skill_descriptions=skill_descriptions
        ) | self.llm.with_structured_output(SkillSelection)

        try:
            response = await chain.ainvoke({"intent": intent})
            return {"skill_name": response.skill_name, "reasoning": response.reasoning}
        except Exception as e:
            logger.error(f"Skill selection failed: {e}")
            return {"skill_name": "none", "reasoning": f"Error: {str(e)}"}
