from typing import Any, Dict

from agents.blackbox_specialist import BlackboxSpecialist


class CompetitorIntelligenceAgent(BlackboxSpecialist):
    """
    Specialist focused on extracting insights from competitor scrape telemetry.
    Uses strictly synchronous operations.
    """

    def __init__(self, model_tier: str = "reasoning"):
        super().__init__(agent_id="competitor_intelligence", model_tier=model_tier)

    def run(self, move_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        telemetry = data.get("telemetry_data", [])

        # Filter for scrape actions
        scrapes = [t for t in telemetry if "scrape" in str(t).lower()]

        prompt = (
            "You are the RaptorFlow Competitor Intelligence Agent. Your goal is to "
            "identify key competitor moves from execution telemetry.\n\n"
            f"Move ID: {move_id}\n"
            f"Scrape Data: {scrapes}\n\n"
            "Identify key competitor prices, features, or creative hooks discovered."
        )

        response = self.model.invoke(prompt)
        return {"competitor_insights": response.content, "status": "analyzed"}
