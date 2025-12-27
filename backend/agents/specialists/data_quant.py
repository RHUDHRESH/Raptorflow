import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.data_quant")


class DataQuantAgent(BaseCognitiveAgent):
    """
    The Data Quant.
    Specializes in BigQuery analysis, Bayesian statistics, and KPI monitoring.
    """

    def __init__(self):
        from core.prompts import AssetSpecializations

        super().__init__(
            name="DataQuantAgent",
            role="data_quant",
            system_prompt=AssetSpecializations.DATA_QUANT,
            model_tier="driver",
            auto_assign_tools=True,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        logger.info(f"DataQuantAgent ({self.name}) crunching longitudinal data...")
        return await super().__call__(state)
