"""
Channel Recommender Specialist Agent
Recommends optimal marketing channels based on ICP behavior and strategic position.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)


class ChannelRecommender(BaseAgent):
    """Specialist agent for acquisition channel strategy and media mix."""

    def __init__(self):
        super().__init__(
            name="ChannelRecommender",
            description="Recommends optimal marketing channels and media mix",
            model_tier=ModelTier.FLASH,
            tools=["database", "web_search"],
            skills=[
                "channel_strategy",
                "media_mix_optimization",
                "acquisition_planning",
            ],
        )

    def get_system_prompt(self) -> str:
        return """You are the ChannelRecommender.
        Your goal is to select the specific marketing channels where the ICP actually lives.

        Key Responsibilities:
        1. Channel Selection: Rank channels (SEO, LinkedIn, X, Cold Outreach, etc.) by relevance to the ICP.
        2. Media Mix: Propose a percentage split between Organic, Paid, and Referral.
        3. Strategic Rationale: Explain WHY each channel was chosen based on psychographics.
        4. Resource Implication: Estimate the effort and cost for each channel.

        Be data-driven. Use 'Editorial Restraint'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute channel recommendation analysis."""
        logger.info("ChannelRecommender: Mapping channel architecture")

        business_context = state.get("business_context", {})
        icp_profiles = state.get("step_data", {}).get("icp_profiles", {})

        prompt = f"""
        Analyze the business context and ICP profiles to recommend a high-leverage channel mix.

        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}

        ICP PROFILES:
        {json.dumps(icp_profiles, indent=2)}

        Output a JSON object with:
        - recommendations: list of {{channel: string, priority: string, rationale: string, effort: string, cost: string}}
        - mix: {{organic: float, paid: float, referral: float}}
        - key_message_by_channel: dict mapping channel to string
        """

        res = await self._call_llm(prompt)

        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_res)
            return {"output": data}
        except Exception as e:
            logger.error(f"ChannelRecommender: Failed to parse LLM response: {e}")
            return {"error": f"Failed to parse channel mix: {str(e)}", "output": {}}
