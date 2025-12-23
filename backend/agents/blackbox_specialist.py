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
