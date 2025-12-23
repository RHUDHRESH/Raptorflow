from abc import ABC, abstractmethod
from typing import Dict, Any
from backend.inference import InferenceProvider


class BlackboxSpecialist(ABC):
    """
    Base abstract class for all Blackbox specialized agents.
    Uses strictly synchronous operations.
    """

    def __init__(self, agent_id: str, model_tier: str = "driver"):
        self.agent_id = agent_id
        self.model = InferenceProvider.get_model(model_tier=model_tier)

    @abstractmethod
    def run(self, move_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the specialized analysis logic.
        """
        pass

    def __call__(self, move_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Allows the specialist to be used synchronously.
        """
        return self.run(move_id, data)