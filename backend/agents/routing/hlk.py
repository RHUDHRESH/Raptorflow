"""
HLK (Hierarchical-Label-Keyword) router using FLASH_LITE classification.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from pydantic import BaseModel

from ..llm import ModelTier, get_llm
from ..base import BaseRouter

logger = logging.getLogger(__name__)


class HLKClassification(BaseModel):
    """Classification result from HLK routing."""

    domain: str
    category: str
    agent: str
    confidence: float
    reasoning: str


@dataclass
class HLKRouteResult:
    """Result from HLK routing."""

    domain: str
    category: str
    agent: str
    confidence: float
    reasoning: str
    model_tier: str


class HLKRouter(BaseRouter):
    """HLK router using FLASH_LITE for classification."""

    def __init__(self):
        super().__init__()
        self.model_tier = ModelTier.FLASH_LITE
        self.llm = get_llm(self.model_tier)

        # Classification prompt template
        self.CLASSIFICATION_PROMPT = """
You are a routing classifier for Raptorflow marketing automation platform.

Analyze the user's request and classify it into:
- domain: The business domain (marketing, sales, research, analytics, general)
- category: The specific category (onboarding, content, strategy, research, analytics)
- agent: The specific agent that should handle this (onboarding_orchestrator, content_creator, move_strategist, market_research, analytics_agent)
- confidence: Your confidence in this classification (0.0-1.0)
- reasoning: Brief explanation of why you chose this classification

Available domains: marketing, sales, research, analytics, general
Available categories: onboarding, content, strategy, research, analytics
Available agents: onboarding_orchestrator, content_creator, move_strategist, market_research, analytics_agent

Examples:
- "Help me get started" → domain: marketing, category: onboarding, agent: onboarding_orchestrator
- "Write a blog post about AI" → domain: marketing, category: content, agent: content_creator
- "Create a marketing campaign" → domain: marketing, category: strategy, agent: move_strategist
- "Research my competitors" → domain: research, category: research, agent: market_research
- "Show me my campaign results" → domain: analytics, category: analytics, agent: analytics_agent

User request: {query}

Respond with valid JSON only:
{{
    "domain": "...",
    "category": "...",
    "agent": "...",
    "confidence": 0.0,
    "reasoning": "..."
}}
"""

    async def route(self, query: str, **kwargs) -> HLKRouteResult:
        """Route a query using HLK classification."""
        if not query or len(query.strip()) < 3:
            return HLKRouteResult(
                domain="general",
                category="general",
                agent="general",
                confidence=0.0,
                reasoning="Query too short or empty",
                model_tier=self.model_tier.value,
            )

        try:
            # Generate classification
            prompt = self.CLASSIFICATION_PROMPT.format(query=query.strip())

            classification_data = await self.llm.generate_structured(
                prompt=prompt, output_schema=HLKClassification
            )

            # Validate classification
            classification = HLKClassification(**classification_data)

            # Map to agent names
            agent_mapping = {
                "onboarding_orchestrator": "OnboardingOrchestrator",
                "content_creator": "ContentCreator",
                "move_strategist": "MoveStrategist",
                "market_research": "MarketResearchAgent",
                "analytics_agent": "AnalyticsAgent",
            }

            agent_name = agent_mapping.get(classification.agent, classification.agent)

            return HLKRouteResult(
                domain=classification.domain,
                category=classification.category,
                agent=agent_name,
                confidence=classification.confidence,
                reasoning=classification.reasoning,
                model_tier=self.model_tier.value,
            )

        except Exception as e:
            logger.error(f"Error in HLK routing: {e}")
            return HLKRouteResult(
                domain="general",
                category="general",
                agent="general",
                confidence=0.0,
                reasoning=f"Classification error: {str(e)}",
                model_tier=self.model_tier.value,
            )

    async def batch_classify(self, queries: list) -> list[HLKRouteResult]:
        """Classify multiple queries."""
        results = []

        for query in queries:
            result = await self.route(query)
            results.append(result)

        return results

    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics."""
        return {
            "model_tier": self.model_tier.value,
            "supported_domains": [
                "marketing",
                "sales",
                "research",
                "analytics",
                "general",
            ],
            "supported_categories": [
                "onboarding",
                "content",
                "strategy",
                "research",
                "analytics",
            ],
            "supported_agents": [
                "onboarding_orchestrator",
                "content_creator",
                "move_strategist",
                "market_research",
                "analytics_agent",
            ],
        }

    def validate_classification(self, classification: Dict[str, Any]) -> bool:
        """Validate a classification result."""
        required_fields = ["domain", "category", "agent", "confidence", "reasoning"]

        # Check required fields
        for field in required_fields:
            if field not in classification:
                return False

        # Check confidence range
        confidence = classification.get("confidence", 0)
        if not (0.0 <= confidence <= 1.0):
            return False

        # Check valid values
        valid_domains = ["marketing", "sales", "research", "analytics", "general"]
        valid_categories = [
            "onboarding",
            "content",
            "strategy",
            "research",
            "analytics",
        ]
        valid_agents = [
            "onboarding_orchestrator",
            "content_creator",
            "move_strategist",
            "market_research",
            "analytics_agent",
        ]

        if classification["domain"] not in valid_domains:
            return False

        if classification["category"] not in valid_categories:
            return False

        if classification["agent"] not in valid_agents:
            return False

        return True

    def get_routing_confidence_threshold(self) -> float:
        """Get the minimum confidence threshold for routing."""
        return 0.5

    async def route_with_threshold(
        self, query: str, threshold: float = None
    ) -> HLKRouteResult:
        """Route with confidence threshold check."""
        if threshold is None:
            threshold = self.get_routing_confidence_threshold()

        result = await self.route(query)

        # If confidence below threshold, route to general
        if result.confidence < threshold:
            return HLKRouteResult(
                domain="general",
                category="general",
                agent="general",
                confidence=result.confidence,
                reasoning=f"Low confidence ({result.confidence:.3f}) below threshold ({threshold})",
                model_tier=self.model_tier.value,
            )

        return result
