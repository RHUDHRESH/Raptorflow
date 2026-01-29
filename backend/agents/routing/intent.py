"""
Intent router with entity extraction using FLASH model.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..base import BaseRouter
from ..llm import ModelTier, get_llm

logger = logging.getLogger(__name__)


class Entity(BaseModel):
    """Extracted entity from user request."""

    name: str
    type: str
    value: str
    confidence: float


class IntentResult(BaseModel):
    """Intent extraction result."""

    primary_intent: str
    secondary_intents: List[str]
    entities: List[Entity]
    required_tools: List[str]
    required_data: List[str]
    complexity: str
    constraints: List[str]
    clarification_needed: bool
    clarification_question: Optional[str] = None


@dataclass
class IntentRouteResult:
    """Result from intent routing."""

    primary_intent: str
    secondary_intents: List[str]
    entities: List[Entity]
    required_tools: List[str]
    required_data: List[str]
    complexity: str
    constraints: List[str]
    clarification_needed: bool
    clarification_question: Optional[str]
    model_tier: str


class IntentRouter(BaseRouter):
    """Intent router with detailed entity extraction."""

    def __init__(self):
        super().__init__()
        self.model_tier = ModelTier.FLASH
        self.llm = get_llm(self.model_tier)

        # Intent extraction prompt
        self.INTENT_PROMPT = """
You are an intent analyzer for Raptorflow marketing automation platform.

Analyze the user's request and extract:
- primary_intent: The main goal of the request
- secondary_intents: Any additional goals (max 3)
- entities: Key entities mentioned (company names, dates, metrics, etc.)
- required_tools: Tools needed to fulfill the request
- required_data: Data that needs to be gathered
- complexity: simple, moderate, or complex
- constraints: Any limitations or requirements
- clarification_needed: Does the request need clarification?
- clarification_question: What to ask if clarification is needed

Available intents: onboarding, content_creation, strategy_planning, research, analytics, general
Available tools: titan_intelligence_engine, web_search, database, content_gen, template_tool, feedback_tool
Complexity levels: simple, moderate, complex

Examples:
- "Help me get started" ΓåÆ primary_intent: onboarding, complexity: simple, no clarification needed
- "Write a blog post about AI trends for Q1" ΓåÆ primary_intent: content_creation, entities: [AI trends, Q1], complexity: moderate
- "Create a 6-month marketing strategy with budget $50k" ΓåÆ primary_intent: strategy_planning, entities: [6 months, $50k], complexity: complex
- "Research competitors in SaaS industry" ΓåÆ primary_intent: research, entities: [SaaS industry], required_tools: [web_search]
- "Show me last month's campaign performance" ΓåÆ primary_intent: analytics, required_data: [campaign metrics], complexity: moderate

User request: {query}

Respond with valid JSON only:
{{
    "primary_intent": "...",
    "secondary_intents": ["...", "..."],
    "entities": [
        {{"name": "...", "type": "...", "value": "...", "confidence": 0.0}}
    ],
    "required_tools": ["...", "..."],
    "required_data": ["...", "..."],
    "complexity": "...",
    "constraints": ["...", "..."],
    "clarification_needed": false,
    "clarification_question": null
}}
"""

    async def route(self, query: str, **kwargs) -> IntentRouteResult:
        """Extract intent and entities from user query."""
        if not query or len(query.strip()) < 3:
            return IntentRouteResult(
                primary_intent="general",
                secondary_intents=[],
                entities=[],
                required_tools=[],
                required_data=[],
                complexity="simple",
                constraints=[],
                clarification_needed=False,
                clarification_question=None,
                model_tier=self.model_tier.value,
            )

        try:
            # Extract intent
            prompt = self.INTENT_PROMPT.format(query=query.strip())

            intent_data = await self.llm.generate_structured(
                prompt=prompt, output_schema=IntentResult
            )

            # Validate and create result
            intent = IntentResult(**intent_data)

            # Convert entities to Entity objects
            entities = []
            for entity_data in intent.entities:
                entities.append(Entity(**entity_data))

            return IntentRouteResult(
                primary_intent=intent.primary_intent,
                secondary_intents=intent.secondary_intents,
                entities=entities,
                required_tools=intent.required_tools,
                required_data=intent.required_data,
                complexity=intent.complexity,
                constraints=intent.constraints,
                clarification_needed=intent.clarification_needed,
                clarification_question=intent.clarification_question,
                model_tier=self.model_tier.value,
            )

        except Exception as e:
            logger.error(f"Error in intent routing: {e}")
            return IntentRouteResult(
                primary_intent="general",
                secondary_intents=[],
                entities=[],
                required_tools=[],
                required_data=[],
                complexity="simple",
                constraints=[],
                clarification_needed=False,
                clarification_question=None,
                model_tier=self.model_tier.value,
            )

    async def extract_entities_only(self, query: str) -> List[Entity]:
        """Extract only entities from a query."""
        result = await self.route(query)
        return result.entities

    async def get_required_tools(self, query: str) -> List[str]:
        """Get required tools for a query."""
        result = await self.route(query)
        return result.required_tools

    async def assess_complexity(self, query: str) -> str:
        """Assess complexity of a query."""
        result = await self.route(query)
        return result.complexity

    async def needs_clarification(self, query: str) -> tuple[bool, Optional[str]]:
        """Check if a query needs clarification."""
        result = await self.route(query)
        return result.clarification_needed, result.clarification_question

    def get_supported_intents(self) -> List[str]:
        """Get list of supported intents."""
        return [
            "onboarding",
            "content_creation",
            "strategy_planning",
            "research",
            "analytics",
            "general",
        ]

    def get_supported_tools(self) -> List[str]:
        """Get list of supported tools."""
        return [
            "titan_intelligence_engine",
            "web_search",
            "database",
            "content_gen",
            "template_tool",
            "feedback_tool",
        ]

    def get_complexity_levels(self) -> List[str]:
        """Get complexity levels."""
        return ["simple", "moderate", "complex"]

    async def batch_analyze(self, queries: List[str]) -> List[IntentRouteResult]:
        """Analyze multiple queries."""
        results = []

        for query in queries:
            result = await self.route(query)
            results.append(result)

        return results

    def validate_intent_result(self, result: Dict[str, Any]) -> bool:
        """Validate intent extraction result."""
        required_fields = [
            "primary_intent",
            "secondary_intents",
            "entities",
            "required_tools",
            "required_data",
            "complexity",
            "constraints",
            "clarification_needed",
        ]

        # Check required fields
        for field in required_fields:
            if field not in result:
                return False

        # Check valid values
        valid_intents = self.get_supported_intents()
        valid_tools = self.get_supported_tools()
        valid_complexity = self.get_complexity_levels()

        if result["primary_intent"] not in valid_intents:
            return False

        for tool in result["required_tools"]:
            if tool not in valid_tools:
                return False

        if result["complexity"] not in valid_complexity:
            return False

        return True

    def get_intent_stats(self) -> Dict[str, Any]:
        """Get intent router statistics."""
        return {
            "model_tier": self.model_tier.value,
            "supported_intents": self.get_supported_intents(),
            "supported_tools": self.get_supported_tools(),
            "complexity_levels": self.get_complexity_levels(),
        }
