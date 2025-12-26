from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from inference import InferenceProvider
from memory.swarm_learning import SwarmLearning


class StylePreference(BaseModel):
    key: str = Field(
        description="The preference key (e.g. 'emoji_usage', 'sentence_length')"
    )
    value: str = Field(description="The learned rule")
    confidence: float = Field(description="Confidence 0-1")


class MemoryUpdaterAgent:
    def __init__(self, swarm_learning: SwarmLearning | None = None):
        self.llm = InferenceProvider.get_model(
            model_tier="smart"
        ).with_structured_output(StylePreference)
        self.swarm_learning = swarm_learning or SwarmLearning()

    async def learn_from_edit(
        self,
        draft: str,
        final: str,
        workspace_id: Optional[str] = None,
        thread_id: str = "style_preference",
    ) -> Optional[StylePreference]:
        # SOTA Technique: Delta Analysis
        # Compare AI draft vs User's final version to extract style rules.
        if draft == final:
            return None

        system_msg = SystemMessage(
            content="""
            You are the Memory Updater. Compare the AI's draft and the User's final version.
            Identify one clear stylistic preference the user has (e.g. 'prefers no emojis', 'wants shorter sentences').
            Only return if you are highly confident (>0.8).
        """
        )

        comparison = f"DRAFT: {draft}\nFINAL: {final}"
        preference = await self.llm.ainvoke(
            [system_msg, HumanMessage(content=comparison)]
        )

        if (
            preference
            and workspace_id
            and self.swarm_learning
            and preference.confidence >= 0.8
        ):
            await self.swarm_learning.record_learning(
                workspace_id=workspace_id,
                thread_id=thread_id,
                learning=preference.model_dump(),
                metadata={"source": "memory_updater"},
            )

        return preference
