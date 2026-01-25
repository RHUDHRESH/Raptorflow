"""
Insight Extractor Specialist Agent
Maps Pain/Desire/Objection from market research data.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from ..base import BaseAgent
from backend.agents.config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)

class InsightExtractor(BaseAgent):
    """Specialist agent for extracting market insights from research data."""

    def __init__(self):
        super().__init__(
            name="InsightExtractor",
            description="Extracts deep customer insights from research data",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["insight_mapping", "sentiment_analysis", "competitor_discovery"]
        )

    def get_system_prompt(self) -> str:
        return """You are the InsightExtractor.
        Your goal is to parse raw customer verbatims (from Reddit, G2, etc.) and extract high-value market intelligence.
        
        Key Responsibilities:
        1. Map Pain Points: What are they struggling with?
        2. Map Desires: What is their ideal state?
        3. Map Objections: Why do they hesitate to buy current solutions?
        4. Sentiment Scoring: Assign a -1 to 1 score for each verbatim.
        5. Auto-Discovery: Identify competitors mentioned in the data.
        
        Be precise. Extract actual quotes where possible. Rejects fluff."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute insight extraction."""
        logger.info("InsightExtractor: Processing research data")
        
        # Extract research data from state
        # Usually from Step 7 (reddit_scraper)
        research_data = state.get("step_data", {}).get("reddit_scraper", {}).get("threads", [])
        
        if not research_data:
            return {"output": {"pain_points": [], "desires": [], "objections": [], "discovered_competitors": []}}

        # Prepare context for LLM
        context = []
        for thread in research_data:
            text = f"Title: {thread.get('title')}\nContent: {thread.get('selftext')}\nComments:\n"
            for comment in thread.get("comments", []):
                text += f"- {comment.get('body')}\n"
            context.append(text)
            
        context_str = "\n\n---\n\n".join(context)
        
        prompt = f"""
        Extract market insights from the following research data.
        
        DATA:
        {context_str[:15000]} # Limit context
        
        Output a JSON object with:
        - pain_points: list of {{category: string, description: string, sentiment: float, quote: string}}
        - desires: list of {{category: string, description: string, sentiment: float}}
        - objections: list of {{category: string, description: string, sentiment: float}}
        - discovered_competitors: list of strings
        """
        
        res = await self._call_llm(prompt)
        
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            insights = json.loads(clean_res)
            return {
                "output": insights
            }
        except Exception as e:
            logger.error(f"InsightExtractor: Failed to parse LLM response: {e}")
            return {
                "error": f"Failed to parse insights: {str(e)}",
                "output": {}
            }
