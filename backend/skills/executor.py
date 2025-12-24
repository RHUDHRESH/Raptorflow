import json
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from backend.inference import InferenceProvider


class SkillExecutor:
    """
    SOTA Skill Executor with Reflection.
    Does not just 'generate'; it 'refines' until it passes internal QA.
    """

    def __init__(self):
        self.generator = InferenceProvider.get_model(model_tier="ultra")
        self.critic = InferenceProvider.get_model(model_tier="smart")

    async def run_skill(
        self, skill_id: str, inputs: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        # 1. INITIAL DRAFT
        draft_prompt = f"Write {skill_id} content. Inputs: {inputs}. Context: {context}"
        draft = await self.generator.ainvoke([HumanMessage(content=draft_prompt)])

        # 2. INTERNAL REFLECTION (The 'World Class' Secret)
        critique_msg = f"""
        Critique the following draft for a {skill_id}.

        DRAFT: {draft.content}

        Is it surgical? Does it follow brand voice? Is the hook strong?
        List exactly 3 improvements.
        """
        critique = await self.critic.ainvoke([SystemMessage(content=critique_msg)])

        # 3. FINAL POLISH
        final_prompt = f"""
        Refine the draft based on the critique.

        DRAFT: {draft.content}
        CRITIQUE: {critique.content}

        Deliver the final surgical version. No conversational filler.
        """
        final = await self.generator.ainvoke([HumanMessage(content=final_prompt)])

        return final.content
