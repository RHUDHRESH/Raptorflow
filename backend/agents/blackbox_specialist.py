from abc import ABC, abstractmethod
from typing import Any, Dict
from backend.inference import InferenceProvider

class BlackboxSpecialist(ABC):
    """
    Base class for all Blackbox specialist agents.
    Provides shared access to inference and common utilities.
    """
    
    def __init__(self, agent_id: str, model_tier: str = "driver"):
        self.agent_id = agent_id
        self.llm = InferenceProvider.get_model(model_tier=model_tier)
        
    @abstractmethod
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the specialist's core logic.
        """
        pass
        
    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Allows the specialist to be used as a LangGraph node.
        """
        return await self.run(state)

class ROIAnalystAgent(BlackboxSpecialist):
    """
    Specialist focused on business outcome attribution and ROI calculation.
    """

    def __init__(self, model_tier: str = "reasoning"):
        super().__init__(agent_id="roi_analyst", model_tier=model_tier)

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        outcomes = state.get("outcomes", [])
        move_id = state.get("move_id", "unknown")

        prompt = (
            "You are the RaptorFlow ROI Analyst. Analyze these outcomes for move {move_id}:\n"
            "{outcomes}\n\n"
            "Provide a concise attribution report including ROI estimate."
        ).format(move_id=move_id, outcomes=outcomes)

        response = await self.llm.ainvoke(prompt)
        return {
            "attribution_report": response.content,
            "status": ["attributed"],
        }

class StrategicDriftAgent(BlackboxSpecialist):
    """
    Specialist focused on detecting deviation from brand foundation and strategy.
    """

    def __init__(self, model_tier: str = "reasoning"):
        super().__init__(agent_id="strategic_drift", model_tier=model_tier)

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        findings = state.get("findings", [])
        move_id = state.get("move_id", "unknown")

        prompt = (
            "You are the RaptorFlow Strategic Drift Agent. Analyze these findings for move {move_id}:\n"
            "{findings}\n\n"
            "Compare them against typical 'Brand Foundation' constraints. "
            "Identify any 'Strategic Drift' or misalignment."
        ).format(move_id=move_id, findings=findings)

        response = await self.llm.ainvoke(prompt)
        return {
            "drift_analysis": response.content,
            "status": ["analyzed"],
        }

class CompetitorIntelligenceAgent(BlackboxSpecialist):
    """
    Specialist focused on extracting insights from competitor scrape telemetry.
    """

    def __init__(self, model_tier: str = "reasoning"):
        super().__init__(agent_id="competitor_intelligence", model_tier=model_tier)

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        telemetry = state.get("telemetry_data", [])
        move_id = state.get("move_id", "unknown")

        # Filter for scrape actions
        scrapes = [t for t in telemetry if "scrape" in str(t).lower()]

        prompt = (
            "You are the RaptorFlow Competitor Intelligence Agent. Analyze these scrapes for move {move_id}:\n"
            "{scrapes}\n\n"
            "Identify key competitor moves, price changes, or creative hooks discovered."
        ).format(move_id=move_id, scrapes=scrapes)

        response = await self.llm.ainvoke(prompt)
        return {
            "competitor_insights": response.content,
            "status": ["analyzed"],
        }
