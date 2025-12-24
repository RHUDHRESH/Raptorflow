from typing import List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from backend.inference import InferenceProvider


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

    async def route(self, prompt: str) -> RouterOutput:
        system_msg = SystemMessage(
            content="""
            You are the Intent Router for RaptorFlow.
            Classify user prompts into asset families: email, social, meme, or strategy.
            Extract @mentions which represent campaigns, cohorts, or competitors.
            Assign confidence based on how much detail is provided.
            If the prompt is vague (e.g. 'write an email'), confidence must be < 0.7.
        """
        )

        return await self.llm.ainvoke([system_msg, HumanMessage(content=prompt)])
