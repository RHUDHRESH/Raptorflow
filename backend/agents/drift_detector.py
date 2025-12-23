from typing import Dict, Any
from backend.agents.blackbox_specialist import BlackboxSpecialist


class StrategicDriftAgent(BlackboxSpecialist):
    """
    Specialist focused on detecting deviation from brand foundation and strategy.
    Uses strictly synchronous operations.
    """

    def __init__(self, model_tier: str = "reasoning"):
        super().__init__(agent_id="strategic_drift", model_tier=model_tier)

    def run(self, move_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        trace = data.get("trace", "")
        brand_kit = data.get("brand_kit", "")
        
        prompt = (
            "You are the RaptorFlow Strategic Drift Agent. Your goal is to detect if "
            "marketing execution is diverging from the core brand mission.\n\n"
            f"Move ID: {move_id}\n"
            f"Brand Kit: {brand_kit}\n"
            f"Execution Trace: {trace}\n\n"
            "Identify any 'Strategic Drift' or misalignment. Provide a brief report."
        )

        response = self.model.invoke(prompt)
        return {
            "drift_report": response.content,
            "status": "analyzed"
        }

