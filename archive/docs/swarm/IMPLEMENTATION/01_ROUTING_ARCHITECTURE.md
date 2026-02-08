# ROUTING ARCHITECTURE

> Three-layer routing: Semantic → HLK → Intent

---

## 1. ROUTING OVERVIEW

```
User Request
     │
     ▼
┌─────────────────────────────────────────────────────┐
│              LAYER 1: SEMANTIC ROUTER               │
│                                                     │
│  Embedding-based similarity to route categories    │
│  Fast, cheap (no LLM call)                         │
│  Routes: onboarding | product | utility | unknown  │
└─────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│              LAYER 2: HLK ROUTER                    │
│                                                     │
│  Hierarchical-Label-Keyword classification         │
│  Lightweight LLM call (Flash-Lite)                 │
│  Routes to specific agent within category          │
└─────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│              LAYER 3: INTENT ROUTER                 │
│                                                     │
│  Extracts action intent + parameters               │
│  Determines: create | read | update | delete       │
│  Identifies required skills and tools              │
└─────────────────────────────────────────────────────┘
     │
     ▼
  Agent Execution
```

---

## 2. SEMANTIC ROUTER (Layer 1)

**Purpose**: Fast, embedding-based routing without LLM calls.

**How it works**:
1. Pre-compute embeddings for route descriptions
2. Embed incoming query
3. Cosine similarity to find best match
4. If confidence < threshold, fall through to HLK

```python
# backend/routing/semantic_router.py
from sentence_transformers import SentenceTransformer
import numpy as np
from dataclasses import dataclass
from enum import Enum

class RouteCategory(Enum):
    ONBOARDING = "onboarding"
    MOVES = "moves"
    CAMPAIGNS = "campaigns"
    MUSE = "muse"
    BLACKBOX = "blackbox"
    DAILY_WINS = "daily_wins"
    ANALYTICS = "analytics"
    FOUNDATION = "foundation"
    SETTINGS = "settings"
    UNKNOWN = "unknown"

@dataclass
class Route:
    category: RouteCategory
    description: str
    examples: list[str]
    embedding: np.ndarray | None = None

# Pre-defined routes with training examples
ROUTES = [
    Route(
        category=RouteCategory.ONBOARDING,
        description="User onboarding, business setup, evidence upload, market research, ICP generation, positioning",
        examples=[
            "Upload my pitch deck",
            "Extract facts from my website",
            "Research my competitors",
            "Generate ICP profiles",
            "Create positioning statement",
            "What's my market category?",
            "Find customer pain points"
        ]
    ),
    Route(
        category=RouteCategory.MOVES,
        description="Marketing moves, daily execution plans, tasks, battle plans",
        examples=[
            "Create a new move",
            "Generate a 7-day plan",
            "What should I do today?",
            "I missed yesterday's tasks",
            "Start an ignite move",
            "Create authority building campaign"
        ]
    ),
    Route(
        category=RouteCategory.CAMPAIGNS,
        description="Multi-move campaigns, strategic initiatives, product launches",
        examples=[
            "Launch a new campaign",
            "Plan my product launch",
            "Create a 60-day marketing campaign",
            "Bundle these moves together",
            "Start market entry campaign"
        ]
    ),
    Route(
        category=RouteCategory.MUSE,
        description="Copywriting, content generation, emails, social posts, scripts",
        examples=[
            "Write a cold email",
            "Draft LinkedIn post",
            "Create video script",
            "Generate carousel content",
            "Make this punchier",
            "Write in my brand voice"
        ]
    ),
    Route(
        category=RouteCategory.BLACKBOX,
        description="High-risk strategies, acquisition plays, virality tactics, bold moves",
        examples=[
            "Generate a risky strategy",
            "How can I go viral?",
            "Create acquisition play",
            "Give me a bold move",
            "Aggressive growth tactic",
            "Career-ending risk strategy"
        ]
    ),
    Route(
        category=RouteCategory.DAILY_WINS,
        description="Quick content wins, trending topics, easy posts, current events",
        examples=[
            "What can I post today?",
            "Quick win for LinkedIn",
            "Trending topic content",
            "Easy content idea",
            "What's happening I can comment on?"
        ]
    ),
    Route(
        category=RouteCategory.ANALYTICS,
        description="Performance metrics, reports, insights, tracking",
        examples=[
            "Show my analytics",
            "How are my moves performing?",
            "Campaign metrics",
            "What's working?",
            "Performance report"
        ]
    ),
    Route(
        category=RouteCategory.FOUNDATION,
        description="Business foundation, settings, profile, brand voice, ICPs",
        examples=[
            "Update my brand voice",
            "Edit my foundation",
            "Change my ICPs",
            "View my positioning",
            "My business details"
        ]
    )
]

class SemanticRouter:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.encoder = SentenceTransformer(model_name)
        self.routes = ROUTES
        self.threshold = 0.65  # Minimum confidence
        self._compute_embeddings()

    def _compute_embeddings(self):
        """Pre-compute embeddings for all routes."""
        for route in self.routes:
            # Combine description and examples
            texts = [route.description] + route.examples
            embeddings = self.encoder.encode(texts)
            # Average embedding
            route.embedding = np.mean(embeddings, axis=0)

    def route(self, query: str) -> tuple[RouteCategory, float]:
        """Route query to category with confidence score."""
        query_embedding = self.encoder.encode(query)

        best_match = None
        best_score = -1

        for route in self.routes:
            similarity = np.dot(query_embedding, route.embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(route.embedding)
            )
            if similarity > best_score:
                best_score = similarity
                best_match = route

        if best_score < self.threshold:
            return RouteCategory.UNKNOWN, best_score

        return best_match.category, best_score

    def route_with_fallback(self, query: str) -> tuple[RouteCategory, float, bool]:
        """Route with indicator if HLK fallback needed."""
        category, confidence = self.route(query)
        needs_hlk = confidence < 0.75  # Use HLK for uncertain cases
        return category, confidence, needs_hlk


# Singleton instance
_semantic_router: SemanticRouter | None = None

def get_semantic_router() -> SemanticRouter:
    global _semantic_router
    if _semantic_router is None:
        _semantic_router = SemanticRouter()
    return _semantic_router
```

---

## 3. HLK ROUTER (Layer 2)

**Purpose**: Hierarchical-Label-Keyword routing for precise agent selection.

**When used**:
- Semantic router confidence < 0.75
- Complex queries with multiple intents
- Ambiguous requests

```python
# backend/routing/hlk_router.py
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal

class HLKDecision(BaseModel):
    """Hierarchical-Label-Keyword routing decision."""

    # Hierarchy Level 1: Domain
    domain: Literal["onboarding", "product", "utility"] = Field(
        description="Top-level domain: onboarding (setup), product (features), utility (support)"
    )

    # Hierarchy Level 2: Category
    category: Literal[
        "evidence", "extraction", "research", "positioning", "icp",  # Onboarding
        "moves", "campaigns", "muse", "blackbox", "daily_wins", "analytics",  # Product
        "settings", "billing", "help"  # Utility
    ] = Field(description="Specific category within domain")

    # Hierarchy Level 3: Action
    action: Literal["create", "read", "update", "delete", "analyze", "generate"] = Field(
        description="Action to perform"
    )

    # Keywords extracted
    keywords: list[str] = Field(
        description="Key entities/concepts from the query"
    )

    # Confidence
    confidence: float = Field(
        description="Confidence in this routing decision (0-1)"
    )

    # Reasoning
    reasoning: str = Field(
        description="Brief explanation of routing decision"
    )

HLK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the HLK (Hierarchical-Label-Keyword) Router for Raptorflow.

Your job is to classify user requests into the correct processing pipeline.

HIERARCHY:
1. DOMAIN (top level):
   - onboarding: Initial setup, evidence upload, market research, ICP generation
   - product: Core features (moves, campaigns, muse, blackbox, daily wins)
   - utility: Settings, billing, help

2. CATEGORY (within domain):
   ONBOARDING: evidence, extraction, research, positioning, icp
   PRODUCT: moves, campaigns, muse, blackbox, daily_wins, analytics
   UTILITY: settings, billing, help

3. ACTION:
   - create: Generate new content/entities
   - read: Retrieve existing data
   - update: Modify existing entities
   - delete: Remove entities
   - analyze: Examine/report on data
   - generate: AI-powered content creation

Extract KEYWORDS: Key entities, names, concepts mentioned.

User's current context:
- Onboarding completed: {onboarding_completed}
- Current step (if onboarding): {current_step}
- Has moves: {has_moves}
- Has campaigns: {has_campaigns}
"""),
    ("human", "{query}")
])

class HLKRouter:
    def __init__(self):
        # Use cheapest model for routing
        self.llm = ChatVertexAI(
            model_name="gemini-2.0-flash-lite",
            project="your-gcp-project",
            location="us-central1",
            temperature=0.0,
            max_tokens=300
        )
        self.chain = HLK_PROMPT | self.llm.with_structured_output(HLKDecision)

    async def route(
        self,
        query: str,
        onboarding_completed: bool = False,
        current_step: int | None = None,
        has_moves: bool = False,
        has_campaigns: bool = False
    ) -> HLKDecision:
        """Route query using HLK classification."""

        return await self.chain.ainvoke({
            "query": query,
            "onboarding_completed": onboarding_completed,
            "current_step": current_step,
            "has_moves": has_moves,
            "has_campaigns": has_campaigns
        })


# Agent mapping from HLK decision
AGENT_MAP = {
    ("onboarding", "evidence"): "vault_processor",
    ("onboarding", "extraction"): "truth_extractor",
    ("onboarding", "research"): "market_researcher",
    ("onboarding", "positioning"): "positioning_mapper",
    ("onboarding", "icp"): "icp_architect",
    ("product", "moves"): "moves_generator",
    ("product", "campaigns"): "campaign_planner",
    ("product", "muse"): "muse_engine",
    ("product", "blackbox"): "blackbox_engine",
    ("product", "daily_wins"): "daily_wins_engine",
    ("product", "analytics"): "analytics_agent",
    ("utility", "settings"): "settings_handler",
    ("utility", "billing"): "billing_handler",
    ("utility", "help"): "help_agent",
}

def get_agent_from_hlk(decision: HLKDecision) -> str:
    """Map HLK decision to specific agent."""
    key = (decision.domain, decision.category)
    return AGENT_MAP.get(key, "orchestrator")
```

---

## 4. INTENT ROUTER (Layer 3)

**Purpose**: Extract detailed intent, parameters, and skill requirements.

```python
# backend/routing/intent_router.py
from pydantic import BaseModel, Field
from typing import Literal, Any

class ExtractedIntent(BaseModel):
    """Detailed intent extraction."""

    # Primary intent
    intent: str = Field(description="Primary action intent")

    # Sub-intents (for complex requests)
    sub_intents: list[str] = Field(default=[], description="Secondary intents")

    # Extracted parameters
    parameters: dict[str, Any] = Field(default={}, description="Extracted parameters")

    # Required skills
    required_skills: list[str] = Field(
        description="Skills needed to fulfill this request"
    )

    # Required tools
    required_tools: list[str] = Field(
        description="External tools needed"
    )

    # Context requirements
    needs_foundation: bool = Field(
        description="Does this need foundation context?"
    )
    needs_icps: bool = Field(
        description="Does this need ICP data?"
    )
    needs_history: bool = Field(
        description="Does this need conversation/move history?"
    )
    needs_web_search: bool = Field(
        description="Does this need real-time web data?"
    )

    # Complexity estimate
    complexity: Literal["simple", "moderate", "complex"] = Field(
        description="Estimated complexity"
    )

    # Human approval needed?
    needs_approval: bool = Field(
        description="Should output be reviewed before executing?"
    )

INTENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Intent Extractor for Raptorflow.

Given a routed request, extract detailed intent information for agent execution.

SKILLS AVAILABLE:
- Onboarding: evidence_processing, fact_extraction, market_research, competitor_analysis,
  icp_generation, positioning_creation, messaging_generation
- Moves: move_planning, task_breakdown, schedule_optimization, contingency_planning
- Campaigns: campaign_strategy, phase_planning, resource_allocation
- Muse: copywriting, tone_adjustment, template_filling, format_conversion
- BlackBox: risk_assessment, trend_analysis, virality_prediction, strategy_synthesis
- Daily Wins: trend_scanning, content_matching, quick_generation

TOOLS AVAILABLE:
- web_search, news_search, scrape_website, scrape_reviews
- process_pdf, process_image, ocr_extract
- get_foundation, get_icps, get_moves, get_campaigns
- calculate_gst, scrape_justdial, scrape_indiamart

Routed to: {agent}
Action: {action}
Keywords: {keywords}
"""),
    ("human", "{query}")
])

class IntentRouter:
    def __init__(self):
        self.llm = ChatVertexAI(
            model_name="gemini-2.0-flash-lite",
            project="your-gcp-project",
            temperature=0.0,
            max_tokens=500
        )
        self.chain = INTENT_PROMPT | self.llm.with_structured_output(ExtractedIntent)

    async def extract(
        self,
        query: str,
        agent: str,
        action: str,
        keywords: list[str]
    ) -> ExtractedIntent:
        """Extract detailed intent for execution."""

        return await self.chain.ainvoke({
            "query": query,
            "agent": agent,
            "action": action,
            "keywords": keywords
        })
```

---

## 5. UNIFIED ROUTING PIPELINE

```python
# backend/routing/pipeline.py
from dataclasses import dataclass
from .semantic_router import get_semantic_router, RouteCategory
from .hlk_router import HLKRouter, HLKDecision, get_agent_from_hlk
from .intent_router import IntentRouter, ExtractedIntent

@dataclass
class RoutingResult:
    """Complete routing result."""
    category: RouteCategory
    agent: str
    hlk_decision: HLKDecision | None
    intent: ExtractedIntent
    routing_path: list[str]  # Which routers were used
    total_latency_ms: float

class RoutingPipeline:
    def __init__(self):
        self.semantic_router = get_semantic_router()
        self.hlk_router = HLKRouter()
        self.intent_router = IntentRouter()

    async def route(
        self,
        query: str,
        user_context: dict
    ) -> RoutingResult:
        """Full routing pipeline."""
        import time
        start = time.time()
        routing_path = []

        # Layer 1: Semantic routing
        category, confidence, needs_hlk = self.semantic_router.route_with_fallback(query)
        routing_path.append(f"semantic:{category.value}:{confidence:.2f}")

        hlk_decision = None

        # Layer 2: HLK if needed
        if needs_hlk or category == RouteCategory.UNKNOWN:
            hlk_decision = await self.hlk_router.route(
                query=query,
                onboarding_completed=user_context.get("onboarding_completed", False),
                current_step=user_context.get("current_step"),
                has_moves=user_context.get("has_moves", False),
                has_campaigns=user_context.get("has_campaigns", False)
            )
            routing_path.append(f"hlk:{hlk_decision.domain}:{hlk_decision.category}")
            agent = get_agent_from_hlk(hlk_decision)
            action = hlk_decision.action
            keywords = hlk_decision.keywords
        else:
            # Direct mapping from semantic category
            agent = self._category_to_agent(category)
            action = "generate"  # Default
            keywords = []

        # Layer 3: Intent extraction
        intent = await self.intent_router.extract(
            query=query,
            agent=agent,
            action=action,
            keywords=keywords
        )
        routing_path.append(f"intent:{intent.intent}")

        latency = (time.time() - start) * 1000

        return RoutingResult(
            category=category,
            agent=agent,
            hlk_decision=hlk_decision,
            intent=intent,
            routing_path=routing_path,
            total_latency_ms=latency
        )

    def _category_to_agent(self, category: RouteCategory) -> str:
        """Map semantic category to default agent."""
        mapping = {
            RouteCategory.ONBOARDING: "onboarding_orchestrator",
            RouteCategory.MOVES: "moves_generator",
            RouteCategory.CAMPAIGNS: "campaign_planner",
            RouteCategory.MUSE: "muse_engine",
            RouteCategory.BLACKBOX: "blackbox_engine",
            RouteCategory.DAILY_WINS: "daily_wins_engine",
            RouteCategory.ANALYTICS: "analytics_agent",
            RouteCategory.FOUNDATION: "foundation_manager",
            RouteCategory.SETTINGS: "settings_handler",
            RouteCategory.UNKNOWN: "orchestrator"
        }
        return mapping.get(category, "orchestrator")


# Usage in main flow
async def process_request(query: str, user_context: dict):
    pipeline = RoutingPipeline()
    routing = await pipeline.route(query, user_context)

    # Now execute with full context
    return await execute_agent(
        agent=routing.agent,
        intent=routing.intent,
        user_context=user_context
    )
```

---

## 6. WHEN TO USE EACH ROUTER

| Scenario | Router | Reason |
|----------|--------|--------|
| Clear feature request | Semantic only | Fast, no LLM cost |
| Ambiguous query | Semantic → HLK | Needs classification |
| Complex multi-step | All three | Full intent extraction |
| Settings/utility | Semantic only | Simple routing |
| First message in chat | All three | No context yet |
| Follow-up message | HLK → Intent | Skip semantic, use context |

---

## 7. COST ANALYSIS

| Router | LLM Calls | Tokens | Cost |
|--------|-----------|--------|------|
| Semantic | 0 | 0 | $0 |
| HLK | 1 | ~200 | ~$0.00003 |
| Intent | 1 | ~300 | ~$0.00005 |
| **Full Pipeline** | **2** | **~500** | **~$0.00008** |

Routing overhead is negligible (~$0.00008 per request).
