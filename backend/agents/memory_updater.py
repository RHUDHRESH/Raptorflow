from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from backend.inference import InferenceProvider


class StylePreference(BaseModel):
    key: str = Field(
        description="The preference key (e.g. 'emoji_usage', 'sentence_length')"
    )
    value: str = Field(description="The learned rule")
    confidence: float = Field(description="Confidence 0-1")


class MemoryUpdaterAgent:
    def __init__(self):
        self.llm = InferenceProvider.get_model(
            model_tier="smart"
        ).with_structured_output(StylePreference)

    async def learn_from_edit(
        self, draft: str, final: str
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
        return await self.llm.ainvoke([system_msg, HumanMessage(content=comparison)])
