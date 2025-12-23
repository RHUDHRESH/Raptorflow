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


class BlackboxCritiqueAgent(BlackboxSpecialist):
    """
    Quality Gate specialist that critiques analysis results and findings.
    Implements Task 46: Critique loop.
    """

    def __init__(self, model_tier: str = "ultra"):
        super().__init__(agent_id="blackbox_critique", model_tier=model_tier)

    def run(self, move_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        findings = data.get("findings", [])
        attribution = data.get("attribution", "No attribution yet.")
        drift = data.get("drift_report", "No drift report yet.")

        prompt = (
            "You are the RaptorFlow Quality Gate. Your goal is to rigorously critique "
            "marketing analysis for logical consistency and strategic depth.\n\n"
            f"Move ID: {move_id}\n"
            f"Findings: {findings}\n"
            f"Attribution: {attribution}\n"
            f"Drift Report: {drift}\n\n"
            "Identify logic gaps or missing context. Return a confidence score (0.0-1.0) "
            "and a detailed reflection on what needs to be improved."
        )

        response = self.model.invoke(prompt)
        content = response.content
        
        # Simple score extraction
        import re
        score = 0.5
        match = re.search(r"score[:\s]*(\d+\.?\d*)", content.lower())
        if match:
            try:
                score = float(match.group(1))
            except (ValueError, IndexError):
                pass

        return {
            "critique": content,
            "confidence": score,
            "status": "critiqued"
        }