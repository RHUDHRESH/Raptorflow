from typing import Dict, Any
from backend.agents.blackbox_specialist import BlackboxSpecialist


class ROIAnalystAgent(BlackboxSpecialist):
    """
    Specialist focused on business outcome attribution and ROI calculation.
    Uses strictly synchronous operations.
    """

    def __init__(self, model_tier: str = "reasoning"):
        super().__init__(agent_id="roi_analyst", model_tier=model_tier)

    def run(self, move_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        outcomes = data.get("outcomes", [])
        
        prompt = (
            "You are the RaptorFlow ROI Analyst. Your goal is to attribute business value "
            "to marketing moves with statistical rigor.\n\n"
            f"Move ID: {move_id}\n"
            f"Outcomes Data: {outcomes}\n\n"
            "Provide a concise attribution report including ROI estimate and confidence."
        )

        response = self.model.invoke(prompt)
        return {
            "attribution": response.content,
            "status": "attributed"
        }

