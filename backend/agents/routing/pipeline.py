"""
Routing pipeline that chains Semantic → HLK → Intent routers.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .hlk import HLKRouter, HLKRouteResult
from .intent import IntentRouter, IntentRouteResult
from .semantic import SemanticRouter, SemanticRouteResult

logger = logging.getLogger(__name__)


@dataclass
class RoutingDecision:
    """Complete routing decision from the pipeline."""

    target_agent: str
    routing_path: List[str]
    confidence: float
    semantic_result: Optional[SemanticRouteResult]
    hlk_result: Optional[HLKRouteResult]
    intent_result: Optional[IntentRouteResult]
    total_latency_ms: int
    reasoning: str


class RoutingPipeline:
    """Pipeline that chains multiple routers for intelligent routing."""

    def __init__(self):
        """Initialize the routing pipeline."""
        self.semantic_router = SemanticRouter()
        self.hlk_router = HLKRouter()
        self.intent_router = IntentRouter()

        # Route to agent mapping
        self.ROUTE_TO_AGENT = {
            "onboarding": "OnboardingOrchestrator",
            "moves": "MoveStrategist",
            "muse": "ContentCreator",
            "blackbox": "BlackboxStrategist",
            "research": "MarketResearch",
            "analytics": "AnalyticsAgent",
            "email": "EmailSpecialist",
            "campaign": "CampaignPlanner",
            "icp": "ICPArchitect",
            "evidence": "EvidenceProcessor",
            "fact": "FactExtractor",
            "daily_wins": "DailyWinsGenerator",
            "general": "GeneralAgent",
        }

        # Agent to route mapping (reverse)
        self.AGENT_TO_ROUTE = {v: k for k, v in self.ROUTE_TO_AGENT.items()}

    async def route(self, request: str, fast_mode: bool = False) -> RoutingDecision:
        """Route a request through the pipeline."""
        start_time = time.time()

        try:
            # Step 1: Semantic routing (always runs)
            semantic_result = await self.semantic_router.route(request, threshold=0.85)

            # If high confidence in semantic, return early
            # Calibrated threshold based on empirical testing
            if semantic_result.confidence >= 0.75:  # Reduced from 0.85
                target_agent = self.ROUTE_TO_AGENT.get(
                    semantic_result.route, "GeneralAgent"
                )

                return RoutingDecision(
                    target_agent=target_agent,
                    routing_path=["semantic"],
                    confidence=semantic_result.confidence,
                    semantic_result=semantic_result,
                    hlk_result=None,
                    intent_result=None,
                    total_latency_ms=int((time.time() - start_time) * 1000),
                    reasoning=f"High confidence semantic match: {semantic_result.reasoning}",
                )

            # Step 2: HLK routing
            hlk_result = await self.hlk_router.route(request)

            # Step 3: Intent routing (skip in fast mode)
            intent_result = None
            if not fast_mode:
                intent_result = await self.intent_router.route(request)

            # Make final decision
            target_agent, confidence, reasoning = self._make_routing_decision(
                semantic_result, hlk_result, intent_result
            )

            # Build routing path
            routing_path = ["semantic", "hlk"]
            if intent_result:
                routing_path.append("intent")

            return RoutingDecision(
                target_agent=target_agent,
                routing_path=routing_path,
                confidence=confidence,
                semantic_result=semantic_result,
                hlk_result=hlk_result,
                intent_result=intent_result,
                total_latency_ms=int((time.time() - start_time) * 1000),
                reasoning=reasoning,
            )

        except Exception as e:
            logger.error(f"Error in routing pipeline: {e}")
            return RoutingDecision(
                target_agent="GeneralAgent",
                routing_path=["error"],
                confidence=0.0,
                semantic_result=None,
                hlk_result=None,
                intent_result=None,
                total_latency_ms=int((time.time() - start_time) * 1000),
                reasoning=f"Routing error: {str(e)}",
            )

    def _make_routing_decision(
        self,
        semantic_result: SemanticRouteResult,
        hlk_result: HLKRouteResult,
        intent_result: Optional[IntentRouteResult],
    ) -> tuple[str, float, str]:
        """Make final routing decision based on all router results."""

        # Priority order: HLK > Semantic > Intent
        # Calibrated thresholds based on empirical testing
        if hlk_result.confidence >= 0.6:  # Reduced from 0.7
            # Trust HLK classification
            target_agent = hlk_result.agent
            confidence = hlk_result.confidence
            reasoning = f"HLK classification: {hlk_result.reasoning}"
        elif semantic_result.confidence >= 0.5:  # Reduced from 0.6
            # Use semantic routing
            target_agent = self.ROUTE_TO_AGENT.get(
                semantic_result.route, "GeneralAgent"
            )
            confidence = semantic_result.confidence
            reasoning = f"Semantic routing: {semantic_result.reasoning}"
        elif intent_result and intent_result.primary_intent != "general":
            # Use intent routing
            intent_to_agent = {
                "onboarding": "OnboardingOrchestrator",
                "content_creation": "ContentCreator",
                "strategy_planning": "MoveStrategist",
                "research": "MarketResearchAgent",
                "analytics": "AnalyticsAgent",
            }
            target_agent = intent_to_agent.get(
                intent_result.primary_intent, "GeneralAgent"
            )
            confidence = 0.4  # Reduced from 0.5
            reasoning = f"Intent-based routing: {intent_result.primary_intent}"
        else:
            # Default to general
            target_agent = "GeneralAgent"
            confidence = 0.2  # Reduced from 0.3
            reasoning = "Low confidence across all routers, defaulting to general"

        return target_agent, confidence, reasoning

    async def batch_route(
        self, requests: List[str], fast_mode: bool = False
    ) -> List[RoutingDecision]:
        """Route multiple requests."""
        results = []

        for request in requests:
            result = await self.route(request, fast_mode)
            results.append(result)

        return results

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "routers": {
                "semantic": self.semantic_router.get_route_info(),
                "hlk": self.hlk_router.get_classification_stats(),
                "intent": self.intent_router.get_intent_stats(),
            },
            "route_to_agent": self.ROUTE_TO_AGENT,
            "supported_agents": list(self.ROUTE_TO_AGENT.values()),
        }

    def get_routing_path_explanation(self, routing_path: List[str]) -> str:
        """Get explanation of routing path."""
        explanations = {
            "semantic": "Fast embedding-based routing for common patterns",
            "hlk": "Hierarchical classification using FLASH_LITE",
            "intent": "Detailed intent and entity extraction using FLASH",
            "error": "Error occurred during routing",
        }

        return " → ".join(explanations.get(step, step) for step in routing_path)

    async def route_with_context(
        self, request: str, context: Dict[str, Any], fast_mode: bool = False
    ) -> RoutingDecision:
        """Route with additional context."""
        # In a real implementation, context would influence routing
        # For now, just use the standard routing
        return await self.route(request, fast_mode)

    def validate_routing_decision(self, decision: RoutingDecision) -> bool:
        """Validate a routing decision."""
        if not decision.target_agent:
            return False

        if decision.confidence < 0 or decision.confidence > 1:
            return False

        if decision.target_agent not in self.ROUTE_TO_AGENT.values():
            if decision.target_agent != "GeneralAgent":
                return False

        return True

    def get_agent_for_route(self, route: str) -> str:
        """Get agent name for a route."""
        return self.ROUTE_TO_AGENT.get(route, "GeneralAgent")

    def get_route_for_agent(self, agent: str) -> str:
        """Get route name for an agent."""
        return self.AGENT_TO_ROUTE.get(agent, "general")

    async def benchmark_routing(self, test_queries: List[str]) -> Dict[str, Any]:
        """Benchmark routing performance."""
        results = {
            "total_queries": len(test_queries),
            "semantic_only": 0,
            "full_pipeline": 0,
            "avg_latency_ms": 0,
            "avg_confidence": 0,
            "agent_distribution": {},
        }

        total_latency = 0
        total_confidence = 0

        for query in test_queries:
            # Test semantic only
            start = time.time()
            semantic_result = await self.semantic_router.route(query)
            semantic_latency = (time.time() - start) * 1000

            # Test full pipeline
            start = time.time()
            full_result = await self.route(query, fast_mode=False)
            full_latency = (time.time() - start) * 1000

            # Track metrics
            if semantic_result.confidence >= 0.85:
                results["semantic_only"] += 1
            else:
                results["full_pipeline"] += 1

            total_latency += full_latency
            total_confidence += full_result.confidence

            # Track agent distribution
            agent = full_result.target_agent
            results["agent_distribution"][agent] = (
                results["agent_distribution"].get(agent, 0) + 1
            )

        results["avg_latency_ms"] = total_latency / len(test_queries)
        results["avg_confidence"] = total_confidence / len(test_queries)

        return results
