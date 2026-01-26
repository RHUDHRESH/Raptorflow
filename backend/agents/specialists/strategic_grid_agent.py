"""
Strategic Grid Orchestrator Agent
Locks in strategic position and generates execution milestones.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from backend.agents.config import ModelTier

from ..base import BaseAgent
from ..state import AgentState

logger = logging.getLogger(__name__)


class StrategicGridGenerator(BaseAgent):
    """Specialist agent for locking position and synthesizing milestones."""

    def __init__(self):
        super().__init__(
            name="StrategicGridGenerator",
            description="Orchestrates position selection and milestone synthesis",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["strategic_grid_mapping", "milestone_planning", "gap_analysis"],
        )

    def get_system_prompt(self) -> str:
        return """You are the StrategicGridOrchestrator.
        Your goal is to transition from strategic analysis to execution planning.

        Key Responsibilities:
        1. Position Selection: Confirm the optimal positioning choice from Step 11.
        2. Milestone Synthesis: Generate 3-5 high-leverage milestones to achieve this position.
        3. Gap Analysis: Identify immediate Threats and Opportunities (Gap Analysis Cards).
        4. BCM Update: Prepare the data to update the Business Context Map (BCM).

        Be decisive. Use 'Editorial Restraint'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute position selection and milestone planning."""
        logger.info("StrategicGridOrchestrator: Finalizing strategic lock")

        business_context = state.get("business_context", {})
        perceptual_map = state.get("step_data", {}).get("perceptual_map", {})

        prompt = f"""
        Analyze the positioning options and select the ultimate 'Winner'.
        Synthesize execution milestones and gap analysis cards.

        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}

        PERCEPTUAL MAP & OPTIONS:
        {json.dumps(perceptual_map, indent=2)}

        Output a JSON object with:
        - selected_position: string
        - rationale: string
        - milestones: list of {{name: string, description: string, timeline: string}}
        - threats: list of strings (Adversarial risks)
        - opportunities: list of strings (Expansion potential)
        """

        res = await self._call_llm(prompt)

        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_res)
            return {"output": data}
        except Exception as e:
            logger.error(
                f"StrategicGridOrchestrator: Failed to parse LLM response: {e}"
            )
            return {"error": f"Failed to parse strategic lock: {str(e)}", "output": {}}
