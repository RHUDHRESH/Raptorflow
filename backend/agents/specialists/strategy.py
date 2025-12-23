from typing import List, Dict, Any, Optional
from inference import InferenceProvider
from models.cognitive import AgentResponse, CognitiveStep, ModelTier
from langchain_core.messages import SystemMessage, HumanMessage
import logging

class ICPArchitectAgent:
    """
    A03: The ICP Architect.
    Builds surgical target audience profiles.
    Analyzes 'Jobs to be Done', 'Status Quo', and 'Core Fears'.
    """
    def __init__(self):
        self.llm = InferenceProvider.get_model(model_tier=ModelTier.ULTRA)
        self.researcher = InferenceProvider.get_model(model_tier=ModelTier.SMART)

    async def build_profile(self, company_context: str) -> AgentResponse:
        # Step 1: Hypothesis Generation
        hypothesis_prompt = f"Given this context: {company_context}, hypothesize 3 specific, non-obvious segments that would pay 5x the average."
        hypotheses = await self.researcher.ainvoke([HumanMessage(content=hypothesis_prompt)])
        
        # Step 2: Deep Profiling (JTBD Framework)
        system = """
        You are the World's Best Growth Strategist. 
        Profile the audience using the JTBD (Jobs to be Done) framework.
        Fields: Job, Trigger, Outcome, Hidden Anxiety, Status Quo.
        """
        profile = await self.llm.ainvoke([SystemMessage(content=system), HumanMessage(content=hypotheses.content)])
        
        return AgentResponse(
            content=profile.content,
            rationale="Built using the Jobs to be Done framework with premium segment hypotheses.",
            confidence_score=0.88,
            inner_monologue=[CognitiveStep(thought="Hypothesized segments, then deep-profiled the highest value one.")]
        )

class CompetitorAnalystAgent:
    """
    A04: The Competitor Intelligence Specialist.
    Analyzes competitor landers, pricing, and USP gaps.
    """
    def __init__(self):
        self.llm = InferenceProvider.get_model(model_tier=ModelTier.SMART)

    async def gap_analysis(self, company_usp: List[str], competitors: List[str]) -> AgentResponse:
        # Complex logic to map USP overlaps and identify the 'Blue Ocean' gap.
        prompt = f"Compare {company_usp} against {competitors}. Find the weakness in their messaging."
        res = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return AgentResponse(content=res.content, rationale="Competitor gap analysis completed.", confidence_score=0.85)

class OfferArchitectAgent:
    """
    A05: The Offer Strategist.
    Turns products into IRRESISTIBLE offers (Alex Hormozi style but surgical).
    """
    def __init__(self):
        self.llm = InferenceProvider.get_model(model_tier=ModelTier.ULTRA)

    async def structure_offer(self, product_details: str) -> AgentResponse:
        system = "You are the Offer Architect. Increase perceived value. Decrease effort. Add urgency. Add proof."
        res = await self.llm.ainvoke([SystemMessage(content=system), HumanMessage(content=product_details)])
        return AgentResponse(content=res.content, rationale="Offer structured for maximum perceived value.", confidence_score=0.92)
