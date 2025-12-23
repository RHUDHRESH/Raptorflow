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
            "status": "attributed",
        }
