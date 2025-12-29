from typing import List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from inference import InferenceProvider


class Brief(BaseModel):
    goal: str = Field(description="The primary objective of the asset")
    audience: str = Field(description="Who this is specifically for")
    offer: Optional[str] = Field(description="The product or service being promoted")
    tone: str = Field(
        description="The desired brand voice (e.g., surgical, authoritative)"
    )
    constraints: List[str] = Field(description="Technical or brand constraints")
    cta: str = Field(description="The primary call to action")


class BriefBuilderAgent:
    def __init__(self):
        # Use 'fast' tier for structuring
        self.llm = InferenceProvider.get_model(
            model_tier="fast", temperature=0.2
        ).with_structured_output(Brief)

    async def build(self, prompt: str, router_context: dict) -> Brief:
        system_msg = SystemMessage(
            content=f"""
            You are the Brief Builder for RaptorFlow.
            Turn the user's prompt into a surgical marketing brief.
            Context from Router: {router_context}

            Focus on clarity and effectiveness. If details are missing, make high-probability
            assumptions based on 'Founder Marketing' best practices but keep them professional.
        """
        )

        return await self.llm.ainvoke([system_msg, HumanMessage(content=prompt)])


def get_swarm_brief_builder():
    """Factory for Swarm-compatible Brief Builder."""
    from swarm import Agent

    from agents.handoffs import handoff_to_supervisor

    return Agent(
        name="Brief Builder",
        instructions="""
        You are the Brief Builder. Your mission is to take raw user input and
        turn it into a structured marketing brief (Goal, Audience, Offer, Tone, CTA).

        Once you have gathered all necessary components, hand off to the Supervisor.
        """,
        functions=[handoff_to_supervisor],
    )
